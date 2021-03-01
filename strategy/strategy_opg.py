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
    positionTimeout = datetime.combine(date.today(),time(12,30))
    strategyTimeValidation = datetime.combine(date.today(),time(9,45))

    def __init__(self):
        self.strategyData = None
        self.gapPrice = None
        self.gapPercentage = None
        self.gapType = None

    def run(self, strategyData: StrategyData):
        self.strategyData = strategyData

        if self.strategyData.position:
            if self.isPositionTimeExpired():
                print("Leave Position - Time expired")
                if self.strategyData.position.type == OrderType.Long:
                    return StrategyResult(StrategyResultType.PositionExpired_Sell)    
                elif self.strategyData.position.type == OrderType.Short:
                    return StrategyResult(StrategyResultType.PositionExpired_Buy)
                raise ValueError('Something is wrong. One of the conditions above should be triggered.')
            else:
                print("Lets pray for that position.")
                return StrategyResult(StrategyResultType.KeepPosition)
        elif self.strategyData.order:
            if self.isOrderTimeExpired(): 
                return StrategyResult(StrategyResultType.StrategyDateWindowExpiredCancelOrder, self.strategyData.order)
            else:
                print("Lets pray for that order.")
                return StrategyResult(StrategyResultType.KeepPosition)
        elif not self.shouldRunStrategy():
            print("Don't run strategy.")
            return StrategyResult(StrategyResultType.StrategyDateWindowExpired)
            
        print("Run Strategy for %s" % strategyData.ticker)

        self.gapPrice = self.strategyData.ystdClosePrice - self.strategyData.openPrice
        self.gapPercentage = abs(self.gapPrice/self.strategyData.ystdClosePrice*100)
        self.profitTarget = None

        self.determinaGapType()

        if self.isStrategyDataValid():
            self.profitTarget = self.calculatePnl()
        else:
            print("The GAP is poor or don't exist. Do nothing")
            return StrategyResult(StrategyResultType.DoNothing)

        type = StrategyResultType.Buy if self.gapType == GapType.Long else StrategyResultType.Sell
        order = self.createOrder()
        return StrategyResult(type, order)

    def shouldRunStrategy(self):
        return self.strategyData.datetime <= self.strategyTimeValidation

    def isStrategyDataValid(self):
        return self.strategyData and self.gapType and self.gapPrice and self.gapPercentage

    def determinaGapType(self):
        if self.isLongGap():
            self.gapType = GapType.Long
        elif self.isShortGap():
            self.gapType = GapType.Short
    
    def isLongGap(self):
        return self.gapPrice > 0 and self.gapPercentage > self.minGap and self.gapPercentage < self.maxGap

    def isShortGap(self):
        return self.gapPrice < 0 and self.gapPercentage > self.minGap and self.gapPercentage < self.maxGap

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
        if self.gapType == GapType.Long and self.strategyData.lastPrice >= profitTarget:
            return True
        elif self.gapType == GapType.Short and self.strategyData.lastPrice <= profitTarget:
            return True
        return False

    def isPositionTimeExpired(self):
        return self.strategyData.datetime >= self.positionTimeout

    def isOrderTimeExpired(self):
        return self.strategyData.datetime >= self.positionTimeout

    def createOrder(self):
        type = OrderType.Long if self.gapType == GapType.Long else OrderType.Short
        totalCash = 2000 # Tenho que ir buscar este valor ao portfolio
        portfolioLoss = totalCash * self.willingToLose
        stopLossPriceRatio = self.strategyData.lastPrice*self.stopToLosePercentage
        stopLossPrice = self.strategyData.lastPrice - stopLossPriceRatio if type == OrderType.Long else self.strategyData.lastPrice + stopLossPriceRatio

        size = min(portfolioLoss/stopLossPriceRatio, (totalCash*self.maxToInvestPerStockPercentage)/self.strategyData.lastPrice)
        print("Last(%.2f) Open(%.2f) YClose(%.2f) Date(%s)" % (self.strategyData.lastPrice, self.strategyData.openPrice, self.strategyData.ystdClosePrice, self.strategyData.datetime))
        print("Type(%s) Size(%i) Price(%.2f) ProfitPrice(%.2f) StopLoss(%.2f)" % (type, size, self.strategyData.lastPrice, self.profitTarget, stopLossPrice))

        return Order(type, self.strategyData.ticker, size, self.strategyData.lastPrice, OrderExecutionType.MarketPrice, self.profitTarget, stopLossPrice)


def buildStrategyData(ticker: Ticker):
    return None