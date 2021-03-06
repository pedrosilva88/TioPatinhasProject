from enum import Enum
from datetime import *
from strategy import Strategy, StrategyData, StrategyResult, StrategyResultType
from models import Order, OrderAction, OrderType

class StrategyOPG(Strategy):
    # Constants
    minGap: int = 2
    maxGap: int = 8
    gapProfitPercentage: float = 0.7
    willingToLose: float = 0.02
    stopToLosePercentage: float = 0.05
    maxToInvestPerStockPercentage: float = 0.2
    strategyHoldTimeout: datetime = datetime.combine(date.today(),time(17,30))
    runStrategyMaxTime: datetime = datetime.combine(date.today(),time(14,45))
    runStrategyStartTime: time = datetime.combine(date.today(),time(14,15))

    # Properties
    strategyData: StrategyData = None
    gapPrice: float= None
    gapPercentage: float = None
    gapType: OrderAction = None

    closePrice: float = None
    openPrice: float = None
    lastPrice: float = None
    askPrice: float = None
    bidPrice: float = None
    avgVolume: float = None
    datetime: datetime = None

    def run(self, strategyData: StrategyData):
        self.strategyData = strategyData
        self.fetchInformation()

        result = self.validateStrategy()
        if result:
            return result

        self.gapPrice = self.closePrice - self.openPrice
        self.gapPercentage = abs(self.gapPrice/self.closePrice*100)
        self.determineGapType()

        if self.isGapValid():
            type = StrategyResultType.Buy if self.gapType == OrderAction.Buy else StrategyResultType.Sell
            order = self.createOrder()
            return StrategyResult(strategyData.ticker, type, order)
        else:
            print("❗️The GAP is poor or don't exist. Do nothing! GapPercentage(%.2f)❗️" % self.gapPercentage)
            return StrategyResult(strategyData.ticker, StrategyResultType.DoNothing)

    # Validations

    def validateStrategy(self):
        if self.strategyData.position:
            return self.handlePosition()

        elif self.strategyData.order:
            return self.handleOrder()

        elif not self.datetimeIsValidForStrategy():
            return StrategyResult(self.strategyData.ticker, StrategyResultType.StrategyDateWindowExpired)

        elif not self.isStrategyDataValid():
            return StrategyResult(self.strategyData.ticker, StrategyResultType.IgnoreEvent)

        return None

    def datetimeIsValidForStrategy(self):
        return (self.datetime and
                self.isDatetimeInThePeriodToRunThisStrategy() and
                self.isDatetimeAfterExchangeStartTime())

    def isDatetimeInThePeriodToRunThisStrategy(self):
        datetime = self.datetime.replace(microsecond=0)
        maxDatetime = self.runStrategyMaxTime.replace(microsecond=0)
        return datetime <= maxDatetime

    def isDatetimeAfterExchangeStartTime(self):
        datetime = self.datetime.replace(microsecond=0)
        startTime = self.runStrategyStartTime.replace(microsecond=0)
        return datetime >= startTime

    def isStrategyDataValid(self):
        return (self.closePrice > 0 and
                self.openPrice > 0 and
                self.lastPrice > 0 and
                self.askPrice > 0 and
                self.bidPrice > 0 and
                self.datetime)

    def isTimeForThisStartegyExpired(self):
        datetime = self.datetime.replace(microsecond=0)
        holdTimeout = self.strategyHoldTimeout.replace(microsecond=0)
        return datetime > holdTimeout

    def isGapValid(self):
        return (self.gapType and self.gapPrice and self.gapPercentage)
    
    def isLongGap(self):
        return (self.gapPrice > 0 and self.gapPercentage > self.minGap and self.gapPercentage < self.maxGap)

    def isShortGap(self):
        return (self.gapPrice < 0 and self.gapPercentage > self.minGap and self.gapPercentage < self.maxGap)

    #Handlers

    def handlePosition(self):
        if self.isTimeForThisStartegyExpired():
            if self.strategyData.position.position > 0:
                return StrategyResult(self.strategyData.ticker, StrategyResultType.PositionExpired_Sell, None, self.strategyData.position)    
            elif self.strategyData.position.position < 0:
                return StrategyResult(self.strategyData.ticker, StrategyResultType.PositionExpired_Buy, None, self.strategyData.position)
        else:
            return StrategyResult(self.strategyData.ticker, StrategyResultType.KeepPosition)

    def handleOrder(self):
        if self.isTimeForThisStartegyExpired(): 
            return StrategyResult(self.strategyData.ticker, StrategyResultType.StrategyDateWindowExpiredCancelOrder, self.strategyData.order)
        else:
            return StrategyResult(self.strategyData.ticker, StrategyResultType.KeepOrder, self.strategyData.order)

    # Calculations

    def calculatePnl(self):
        price = self.orderPrice()
        if self.gapType == OrderAction.Buy:
            value = min(self.openPrice, price)
            return value + value * (self.gapPercentage/100 * self.gapProfitPercentage)
        elif self.gapType == OrderAction.Sell:
            value = max(self.openPrice, price)
            return value - value * (self.gapPercentage/100 * self.gapProfitPercentage)

    def determineGapType(self):
        if self.isLongGap():
            self.gapType = OrderAction.Buy
        elif self.isShortGap():
            self.gapType = OrderAction.Sell
        else:
            self.gapType = None

    def orderPrice(self):
        return self.bidPrice if self.gapType == OrderAction.Buy else self.askPrice

    # Constructor

    def fetchInformation(self):
        self.closePrice = self.strategyData.ticker.close
        self.openPrice = self.strategyData.ticker.open
        self.lastPrice = self.strategyData.ticker.last
        self.askPrice = self.strategyData.ticker.ask
        self.bidPrice = self.strategyData.ticker.last
        self.avgVolume = self.strategyData.ticker.avVolume
        self.datetime = self.strategyData.ticker.time

    # Final Operations

    def createOrder(self):
        action = self.gapType
        totalCash = self.strategyData.totalCash
        price = self.orderPrice()

        profitTarget = self.calculatePnl()
        
        portfolioLoss = totalCash * self.willingToLose
        stopLossPriceRatio = price*self.stopToLosePercentage
        stopLossPrice = price - stopLossPriceRatio if self.gapType == OrderAction.Buy else price + stopLossPriceRatio

        size = int(min(portfolioLoss/stopLossPriceRatio, (totalCash*self.maxToInvestPerStockPercentage)/price))

        print("\t⭐️ Type(%s) Size(%i) Price(%.2f) ProfitPrice(%.2f) StopLoss(%.2f) ⭐️" % (self.gapType, size, price, profitTarget, stopLossPrice))

        profitOrder = Order(action.reverse, OrderType.LimitOrder, size, profitTarget)
        stopLossOrder = Order(action.reverse, OrderType.StopOrder, size, stopLossPrice)

        return Order(action, OrderType.LimitOrder, size, price, profitOrder, stopLossOrder)