from enum import Enum
from datetime import *
from helpers import log
from strategy import Strategy, StrategyData, StrategyResult, StrategyResultType
from models import Order, OrderAction, OrderType

class StrategyOPG(Strategy):
    # Constants
    minGap: int = 3
    maxGap: int = 8
    maxLastGap: int = 9
    gapProfitPercentage: float = 0.7
    willingToLose: float = 0.02
    stopToLosePercentage: float = 0.1
    maxToInvestPerStockPercentage: float = 0.2
    strategyHoldTimeout: datetime = datetime.combine(date.today(),time(17,30))
    runStrategyMaxTime: datetime = datetime.combine(date.today(),time(14,45))
    runStrategyStartTime: time = datetime.combine(date.today(),time(14,15))

    # Properties
    strategyData: StrategyData = None
    gapPrice: float= None
    gapPercentage: float = None
    gapType: OrderAction = None

    gapLastPrice: float = None
    gapLastPercentage: float = None

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

        lastPrice = self.getOrderPrice()
        self.gapLastPrice = self.closePrice - lastPrice if self.gapType == OrderAction.Buy else lastPrice - self.closePrice
        self.gapLastPercentage = self.gapLastPrice/self.closePrice*100

        if self.isGapValid():
            if self.strategyData.order:
                self.updateCurrentOrder()
                return StrategyResult(self.strategyData.ticker, StrategyResultType.KeepOrder, self.strategyData.order)
            else:
                type = StrategyResultType.Buy if self.gapType == OrderAction.Buy else StrategyResultType.Sell
                order = self.createOrder()
                return StrategyResult(strategyData.ticker, type, order)
        else:
            if self.strategyData.order:
                if self.isLastPriceReachingProfitOrder():
                    log("❗️ Order cancelled!❗️")
                    return StrategyResult(strategyData.ticker, StrategyResultType.CancelOrder, self.strategyData.order)
                else:
                    log("❗️ The GAP is becoming poor for this order!❗️")
                    return StrategyResult(strategyData.ticker, StrategyResultType.KeepOrder, self.strategyData.order)
            else:
                log("❗️The GAP is poor or don't exist. Do nothing! %s GapPercentage(%.2f) GapLastPercentage(%.2f)❗️" % (self.strategyData.ticker.contract.symbol, self.gapPercentage, self.gapLastPercentage))
                return StrategyResult(strategyData.ticker, StrategyResultType.DoNothing)
    
    # Constructor

    def fetchInformation(self):
        self.closePrice = self.strategyData.ticker.close
        self.openPrice = self.strategyData.ticker.open
        self.lastPrice = self.strategyData.ticker.last
        self.askPrice = self.strategyData.ticker.ask
        self.bidPrice = self.strategyData.ticker.bid
        self.avgVolume = self.strategyData.ticker.avVolume
        self.datetime = self.strategyData.ticker.time

    # Validations

    def validateStrategy(self):
        if self.strategyData.position:
            return self.handlePosition()

        elif self.strategyData.order:
            return self.handleOrder()

        if not self.datetimeIsValidForStrategy():
            return StrategyResult(self.strategyData.ticker, StrategyResultType.StrategyDateWindowExpired)

        elif not self.isStrategyDataValid():
            return StrategyResult(self.strategyData.ticker, StrategyResultType.IgnoreEvent)

        return None

    def datetimeIsValidForStrategy(self):
        return (self.datetime and
                self.isDatetimeInThePeriodToRunThisStrategy() and
                self.isDatetimeAfterExchangeStartTime())

    def isDatetimeInThePeriodToRunThisStrategy(self):
        datetime = self.datetime.replace(microsecond=0, tzinfo=None)
        maxDatetime = self.runStrategyMaxTime.replace(microsecond=0, tzinfo=None)
        return datetime <= maxDatetime

    def isDatetimeAfterExchangeStartTime(self):
        datetime = self.datetime.replace(microsecond=0, tzinfo=None)
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
        datetime = self.datetime.replace(microsecond=0, tzinfo=None)
        holdTimeout = self.strategyHoldTimeout.replace(microsecond=0, tzinfo=None)
        return datetime > holdTimeout

    def isGapValid(self):
        return (self.gapType and self.gapPrice and self.gapPercentage and 
                self.gapLastPercentage >= self.minGap and self.gapLastPercentage <= self.maxLastGap)
    
    def isLongGap(self):
        return (self.gapPrice > 0 and self.gapPercentage >= self.minGap and self.gapPercentage <= self.maxGap)

    def isShortGap(self):
        return (self.gapPrice < 0 and self.gapPercentage > self.minGap and self.gapPercentage < self.maxGap)

    def shouldGetStockEarnings(self):
        return True

    def isLastPriceReachingProfitOrder(self):
        lastPrice = self.getOrderPrice()
        profitPrice = self.strategyData.order.takeProfitOrder.lmtPrice
        isReachingProfit = lastPrice < profitPrice if self.strategyData.order.action == OrderAction.Buy else lastPrice > profitPrice
        return isReachingProfit

    # Handlers

    def handlePosition(self):
        if self.isTimeForThisStartegyExpired():
            # TODO: Validar se o Position Size é negativo quando estou a fazer short
            if self.strategyData.position.position > 0:
                return StrategyResult(self.strategyData.ticker, StrategyResultType.PositionExpired_Sell, None, self.strategyData.position)    
            elif self.strategyData.position.position < 0:
                return StrategyResult(self.strategyData.ticker, StrategyResultType.PositionExpired_Buy, None, self.strategyData.position)
        else:
            return StrategyResult(self.strategyData.ticker, StrategyResultType.KeepPosition)

    def handleOrder(self):
        if self.isTimeForThisStartegyExpired(): 
            return StrategyResult(self.strategyData.ticker, StrategyResultType.StrategyDateWindowExpiredCancelOrder, self.strategyData.order)
        return None

    # Calculations

    def calculatePnl(self):
        price = self.getOrderPrice()
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

    def getOrderPrice(self):
        return self.bidPrice if self.gapType == OrderAction.Buy else self.askPrice

    def getStopLossPrice(self):
        price = self.getOrderPrice()
        totalCash = self.strategyData.totalCash
        stopLossPriceRatio = price*self.stopToLosePercentage

        return price - stopLossPriceRatio if self.gapType == OrderAction.Buy else price + stopLossPriceRatio

    def getSize(self):
        price = self.getOrderPrice()
        totalCash = self.strategyData.totalCash
        portfolioLoss = totalCash * self.willingToLose
        stopLossPriceRatio = price*self.stopToLosePercentage

        return int(min(portfolioLoss/stopLossPriceRatio, (totalCash*self.maxToInvestPerStockPercentage)/price))

    # Final Operations

    def createOrder(self):
        action = self.gapType
        price = self.getOrderPrice()
        profitTarget = self.calculatePnl()
        stopLossPrice = self.getStopLossPrice()
        size = self.getSize()

        log("\t⭐️ [Create] Type(%s) Size(%i) Price(%.2f) ProfitPrice(%.2f) StopLoss(%.2f) ⭐️" % (self.gapType, size, price, profitTarget, stopLossPrice))

        profitOrder = Order(action.reverse, OrderType.LimitOrder, size, profitTarget)
        stopLossOrder = Order(action.reverse, OrderType.StopOrder, size, stopLossPrice)
        return Order(action=action, type=OrderType.LimitOrder, totalQuantity=size, price=price, takeProfitOrder=profitOrder, stopLossOrder=stopLossOrder)

    def updateCurrentOrder(self):
        price = self.getOrderPrice()
        profitTarget = self.calculatePnl()
        stopLossPrice = self.getStopLossPrice()
        size = self.getSize()

        log("\t⭐️ [Upadte] Type(%s) Size(%i) Price(%.2f) ProfitPrice(%.2f) StopLoss(%.2f) ⭐️" % (self.gapType, size, price, profitTarget, stopLossPrice))

        self.strategyData.order.lmtPrice = round(price,2)
        self.strategyData.order.totalQuantity = int(size)

        self.strategyData.order.takeProfitOrder.lmtPrice = round(profitTarget, 2)
        self.strategyData.order.takeProfitOrder.totalQuantity = int(size)

        self.strategyData.order.stopLossOrder.auxPrice = round(stopLossPrice, 2)
        self.strategyData.order.stopLossOrder.totalQuantity = int(size)
