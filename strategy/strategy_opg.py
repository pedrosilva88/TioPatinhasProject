from enum import Enum
from datetime import *
from strategy import Strategy, StrategyData, GapType, StrategyResult, StrategyResultType
from order import *
from ib_insync import Ticker

### Ideas
# Devia validar se compensa investir na stock mesmo que exista GAP. 
#   Se o lastPrice for muito proximo do valor de fecho pode já não compensar
#

class StrategyOPG(Strategy):
    # Constants
    minGap: int = 2
    maxGap: int = 8
    gapProfitPercentage: float = 0.7
    willingToLose: float = 0.02
    stopToLosePercentage: float = 0.05
    maxToInvestPerStockPercentage: float = 0.2
    positionTimeout = datetime.combine(date.today(),time(17,30))
    strategyTimeValidation = datetime.combine(date.today(),time(14,30))
    exchangeStartTime = time(14,30)

    def __init__(self):
        self.strategyData = None
        self.gapPrice = None
        self.gapPercentage = None
        self.gapType = None

    def run(self, strategyData: StrategyData):
        self.strategyData = strategyData

        if self.strategyData.position:
            if self.isPositionTimeExpired():
                #print("Leave Position - Time expired")
                if self.strategyData.position.type == OrderType.Long:
                    return StrategyResult(strategyData.ticker, StrategyResultType.PositionExpired_Sell)    
                elif self.strategyData.position.type == OrderType.Short:
                    return StrategyResult(strategyData.ticker, StrategyResultType.PositionExpired_Buy)
                raise ValueError('Something is wrong. One of the conditions above should be triggered.')
            else:
                #print("Lets pray for that position.")
                return StrategyResult(strategyData.ticker, StrategyResultType.KeepPosition)
        elif self.strategyData.order:
            if self.isOrderTimeExpired(): 
                return StrategyResult(strategyData.ticker, StrategyResultType.StrategyDateWindowExpiredCancelOrder, self.strategyData.order)
            else:
                #print("Lets pray for that order.")
                return StrategyResult(strategyData.ticker, StrategyResultType.KeepOrder)
        elif not self.shouldRunStrategy():
            #print("Don't run strategy.")
            return StrategyResult(strategyData.ticker, StrategyResultType.StrategyDateWindowExpired)
            
        #print("Run Strategy for %s" % strategyData.ticker)

        self.gapPrice = self.strategyData.ystdClosePrice - self.strategyData.openPrice
        self.gapPercentage = abs(self.gapPrice/self.strategyData.ystdClosePrice*100)
        self.profitTarget = None

        self.determineGapType()

        if self.isStrategyDataValid():
            self.profitTarget = self.calculatePnl()
        else:
            return StrategyResult(strategyData.ticker, StrategyResultType.DoNothing)

        type = StrategyResultType.Buy if self.gapType == GapType.Long else StrategyResultType.Sell
        order = self.createOrder()
        return StrategyResult(strategyData.ticker, type, order)

    def shouldRunStrategy(self):
        return (self.strategyData.datetime and
                self.strategyData.datetime.day == self.strategyTimeValidation.day and 
                self.strategyData.datetime.month == self.strategyTimeValidation.month and
                self.strategyData.datetime.year == self.strategyTimeValidation.year and 
                self.strategyData.datetime.hour == self.exchangeStartTime.hour and
                self.strategyData.datetime.minute >= self.exchangeStartTime.minute and
                self.strategyData.datetime.hour == self.strategyTimeValidation.hour and
                self.strategyData.datetime.minute <= self.strategyTimeValidation.minute)

    def isStrategyDataValid(self):
        return (self.strategyData and self.gapType and self.gapPrice and self.gapPercentage)

    def determineGapType(self):
        if self.isLongGap():
            self.gapType = GapType.Long
        elif self.isShortGap():
            self.gapType = GapType.Short
        else:
            self.gapType = None
    
    def isLongGap(self):
        return (self.gapPrice > 0 and self.gapPercentage > self.minGap and self.gapPercentage < self.maxGap)

    def isShortGap(self):
        return (self.gapPrice < 0 and self.gapPercentage > self.minGap and self.gapPercentage < self.maxGap)

    def calculatePnl(self):
        if self.gapType == GapType.Long:
            value = min(self.strategyData.openPrice, self.strategyData.lastPrice)
            return value + value * (self.gapPercentage/100 * self.gapProfitPercentage)
            #         self.longGaps += 1
            #         print("Should be long: ProfitPrice(%.2f) Open(%.2f) YClose(%.2f) High(%.2f)" % (profitPrice, self.stock['open'][1], self.stock['close'][0], self.stock['high'][1]))
        elif self.gapType == GapType.Short:
            value = max(self.strategyData.openPrice, self.strategyData.lastPrice)
            return value - value * (self.gapPercentage/100 * self.gapProfitPercentage)
            #         self.shortGaps += 1
            #         print("Should be short: ProfitPrice(%.2f) Open(%.2f) YClose(%.2f) Low(%.2f)" % (profitPrice, self.stock['open'][1], self.stock['close'][0], self.stock['low'][1]))
        return -1

    def isProfitTargetReached(self):
        if (self.gapType == GapType.Long and self.strategyData.lastPrice >= profitTarget):
            return True
        elif (self.gapType == GapType.Short and self.strategyData.lastPrice <= profitTarget):
            return True
        return False

    def isPositionTimeExpired(self):
        return (self.strategyData.datetime >= self.positionTimeout)

    def isOrderTimeExpired(self):
        return (self.strategyData.datetime >= self.positionTimeout)

    def createOrder(self):
        type = OrderType.Long if self.gapType == GapType.Long else OrderType.Short
        totalCash = self.strategyData.totalCash
        portfolioLoss = totalCash * self.willingToLose
        stopLossPriceRatio = self.strategyData.lastPrice*self.stopToLosePercentage
        stopLossPrice = self.strategyData.lastPrice - stopLossPriceRatio if type == OrderType.Long else self.strategyData.lastPrice + stopLossPriceRatio

        size = min(portfolioLoss/stopLossPriceRatio, (totalCash*self.maxToInvestPerStockPercentage)/self.strategyData.lastPrice)
        print("Last(%.2f) Open(%.2f) YClose(%.2f) Date(%s)" % (self.strategyData.lastPrice, self.strategyData.openPrice, self.strategyData.ystdClosePrice, self.strategyData.datetime))
        print("Type(%s) Size(%i) Price(%.2f) ProfitPrice(%.2f) StopLoss(%.2f)" % (type, size, self.strategyData.lastPrice, self.profitTarget, stopLossPrice))

        return Order(type, self.strategyData.ticker, size, self.strategyData.lastPrice, OrderExecutionType.MarketPrice, self.profitTarget, stopLossPrice)