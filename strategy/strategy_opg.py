from enum import Enum
from datetime import *
from helpers import log, utcToLocal, round_down
from strategy import Strategy, StrategyData, StrategyResult, StrategyResultType, StrategyConfig, ContractDetails
from models import Order, OrderAction, OrderType
from country_config import CountryConfig

class StrategyOPG(Strategy):
    # Properties

    strategyData: StrategyData = None
    strategyConfig: StrategyConfig = None
    countryConfig: CountryConfig = None

    minGap: int = None
    maxGap: int = None
    maxLastGap: int = None
    gapProfitPercentage: float = None
    willingToLose: float = None
    stopToLosePercentage: float = None
    maxToInvestPerStockPercentage: None
    strategyMaxTime: datetime = None
    strategyValidPeriod: datetime = None
    runStrategyStartTime: datetime = None

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
    volumeFirstMinute: float = None
    datetime: datetime = None
    contractDetails: ContractDetails = None

    def run(self, strategyData: StrategyData, strategyConfig: StrategyConfig, countryConfig: CountryConfig):
        self.strategyData = strategyData
        self.strategyConfig = strategyConfig
        self.countryConfig = countryConfig
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

        if (self.gapPercentage is not None) and (self.gapLastPercentage is not None) and (self.openPrice is not None) and (self.closePrice is not None) and (lastPrice is not None) and (self.gapType is not None):
            log("💍 Strategy for %s: Open(%.2f) Close(%.2f) lastPrice(%.2f) Gap(%.2f) GapLast(%.2f) GapType(%s) 💍" % (self.strategyData.ticker.contract.symbol, self.openPrice, self.closePrice, lastPrice, self.gapPercentage, self.gapLastPercentage, self.gapType))
        else:
            log("💍 Invalid Gap for %s 💍" % (self.strategyData.ticker.contract.symbol))

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
                # print("❗️ %s %s %.2f ❗️" % (self.strategyData.ticker.time, self.gapType, self.gapPrice))
                # print("❗️The GAP is poor or don't exist. Do nothing! %s GapPercentage(%.2f) GapLastPercentage(%.2f)❗️" % (self.strategyData.ticker.contract.symbol, self.gapPercentage, self.gapLastPercentage))

                log("❗️The GAP is poor or don't exist. Do nothing! %s GapPercentage(%.2f) GapLastPercentage(%.2f)❗️" % (self.strategyData.ticker.contract.symbol, self.gapPercentage, self.gapLastPercentage))
                return StrategyResult(strategyData.ticker, StrategyResultType.DoNothing)
    
    # Constructor

    def fetchInformation(self):
        # Ticker Data
        self.closePrice = self.strategyData.ticker.close
        self.openPrice = self.strategyData.ticker.open
        self.lastPrice = self.strategyData.ticker.last
        self.askPrice = self.strategyData.ticker.ask
        self.bidPrice = self.strategyData.ticker.bid
        self.datetime = utcToLocal(self.strategyData.ticker.time, self.countryConfig.timezone)
        self.avgVolume = self.strategyData.averageVolume
        self.volumeFirstMinute = self.strategyData.volumeFirstMinute
        self.contractDetails = self.strategyData.contractDetails

        # Strategy Parameters
        self.minGap = self.strategyConfig.minGap
        self.maxGap = self.strategyConfig.maxGap
        self.maxLastGap = self.strategyConfig.maxLastGap
        self.gapProfitPercentage = self.strategyConfig.gapProfitPercentage
        self.willingToLose = self.strategyConfig.willingToLose
        self.stopToLosePercentage = self.strategyConfig.stopToLosePercentage
        self.maxToInvestPerStockPercentage = self.strategyConfig.maxToInvestPerStockPercentage
        self.averageVolumePercentage = self.strategyConfig.averageVolumePercentage

        self.strategyMaxTime = self.strategyConfig.strategyMaxTime
        self.strategyValidPeriod = self.strategyConfig.strategyValidPeriod
        self.runStrategyStartTime = self.strategyConfig.startRunningStrategy

    # Validations

    def validateStrategy(self):
        if self.strategyData.position:
            return self.handlePosition()

        elif self.strategyData.order:
            return self.handleOrder()

        if not self.datetimeIsValidForStrategy():
            return StrategyResult(self.strategyData.ticker, StrategyResultType.StrategyDateWindowExpired)

        elif (not self.isConfigsValid() or not self.isStrategyDataValid()):
            log("🙅‍♂️ Invalid data for %s: isConfigsValid(%s) isStrategyDataValid(%s) 🙅‍♂️" % (self.strategyData.ticker.contract.symbol, self.isConfigsValid(), self.isStrategyDataValid()))
            return StrategyResult(self.strategyData.ticker, StrategyResultType.IgnoreEvent)

        elif (not self.isVolumeValid()):
            log("❗️ Invalid Volume for %s: AVGVolume(%.2f) VolumeMinute(%.2f) unsubscribing...❗️" % (self.strategyData.ticker.contract.symbol, self.avgVolume, self.volumeFirstMinute))
            return StrategyResult(self.strategyData.ticker, StrategyResultType.DoNothing)

        return None

    def datetimeIsValidForStrategy(self):
        return (self.datetime and
                self.isDatetimeInThePeriodToRunThisStrategy())

    def isDatetimeInThePeriodToRunThisStrategy(self):
        datetime = self.datetime.replace(microsecond=0).time()
        validPeriod = self.strategyValidPeriod.replace(microsecond=0).time()
        return datetime <= validPeriod

    def isStrategyDataValid(self):
        if ((self.volumeFirstMinute is not None) and
            (self.avgVolume is not None)):
            log("😏 Data for %s: AVGVolume(%.2f) MinuteVolume(%.2f) IsDateTimeValid(%s) 😏" % (self.strategyData.ticker.contract.symbol, self.avgVolume, self.volumeFirstMinute, self.isDatetimeValid()))
        return ((self.volumeFirstMinute is not None) and self.volumeFirstMinute >= 0 and
                (self.avgVolume is not None) and self.avgVolume >= 0 and
                self.isDatetimeValid() and
                (self.closePrice is not None) and self.closePrice > 0 and
                (self.openPrice is not None) and self.openPrice > 0 and
                (self.lastPrice is not None) and self.lastPrice > 0 and
                (self.askPrice is not None) and self.askPrice > 0 and
                (self.bidPrice is not None) and self.bidPrice > 0)

    def isDatetimeValid(self):
        return ((self.datetime is not None) and
                ((self.datetime.hour > self.runStrategyStartTime.hour) 
                or
                (self.datetime.hour == self.runStrategyStartTime.hour and 
                self.datetime.minute >= self.runStrategyStartTime.minute)))

    def isVolumeValid(self):
        return self.volumeFirstMinute < (self.avgVolume+(self.avgVolume*self.averageVolumePercentage))

    def isConfigsValid(self):
        return ((self.strategyMaxTime is not None) and
                (self.strategyValidPeriod is not None) and
                (self.runStrategyStartTime is not None) and
                self.minGap > 0 and
                self.maxGap > 0 and
                self.maxLastGap > 0 and
                self.gapProfitPercentage > 0 and
                self.willingToLose > 0 and
                self.stopToLosePercentage > 0 and
                self.maxToInvestPerStockPercentage > 0)

    def isTimeForThisStartegyExpired(self):
        datetime = self.datetime.replace(microsecond=0).time()
        maxTime = self.strategyMaxTime.replace(microsecond=0).time()
        return datetime > maxTime

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
        minTick = self.contractDetails.minTick
        action = self.gapType
        price = self.getOrderPrice()
        profitTarget = self.calculatePnl()
        stopLossPrice = self.getStopLossPrice()
        size = self.getSize()

        log("\t⭐️ [Create] Type(%s) Size(%i) Price(%.2f) ProfitPrice(%.2f) StopLoss(%.2f) ⭐️" % (self.gapType, size, price, profitTarget, stopLossPrice))

        profitOrder = Order(action.reverse, OrderType.LimitOrder, size, round(round_down(profitTarget, minTick), 2))
        stopLossOrder = Order(action.reverse, OrderType.StopOrder, size, round(round_down(stopLossPrice, minTick), 2))
        return Order(action=action, type=OrderType.LimitOrder, totalQuantity=size, price=price, takeProfitOrder=profitOrder, stopLossOrder=stopLossOrder)

    def updateCurrentOrder(self):
        minTick = self.contractDetails.minTick
        price = self.getOrderPrice()
        profitTarget = self.calculatePnl()
        stopLossPrice = self.getStopLossPrice()
        size = self.getSize()

        log("\t⭐️ [Upadte] Type(%s) Size(%i) Price(%.2f) ProfitPrice(%.2f) StopLoss(%.2f) ⭐️" % (self.gapType, size, price, profitTarget, stopLossPrice))

        self.strategyData.order.lmtPrice = round(price, 2)
        self.strategyData.order.totalQuantity = int(size)

        self.strategyData.order.takeProfitOrder.lmtPrice = round(round_down(profitTarget, minTick), 2)
        self.strategyData.order.takeProfitOrder.totalQuantity = int(size)

        self.strategyData.order.stopLossOrder.auxPrice = round(round_down(stopLossPrice, minTick), 2)
        self.strategyData.order.stopLossOrder.totalQuantity = int(size)
