from database.model import FillDB
from datetime import timedelta
from strategy.configs.models import StrategyConfig
from strategy.zigzag.models import StrategyZigZagData, StrategyZigZagResult
from typing import List, Tuple
from helpers import log
from strategy.strategy import Strategy
from strategy.models import StrategyData, StrategyResult, StrategyResultType
from strategy.configs.zigzag.models import StrategyZigZagConfig
from models.base_models import OrderAction
from models.zigzag.models import EventZigZag

class StrategyZigZag(Strategy):
    # Properties
    currentBar: EventZigZag = None
    previousBars: List[EventZigZag] = None
    fill: FillDB = None

    # Strategy Parameters
    profitPercentage: float = None
    willingToLose: float = None
    stopToLosePercentage: float = None
    maxToInvestPerStockPercentage: float = 1
    maxToInvestPerStrategy: float = -1

    minRSI: float = None
    maxRSI: float = None

    timezone: timezone = None

    def run(self, strategyData: StrategyData, strategyConfig: StrategyConfig) -> StrategyResult:
        self.strategyData = strategyData
        self.strategyConfig = strategyConfig
        self.fetchInformation()

        result = self.validateStrategy()
        if result:
            return result

        log("😁 %s 😁" % (self.strategyData.contract.symbol))
        log("😁 [%s] Bar[-4]-> RSI(%.2f) Open(%.2f) Close(%.2f) High(%.2f) Low(%.2f) ZigZag(%s) 😁" % (self.previousBars[-4].datetime.date(), self.previousBars[-4].rsi, self.previousBars[-4].open, self.previousBars[-4].close, self.previousBars[-4].high, self.previousBars[-4].low, self.previousBars[-4].zigzag))
        log("😁 [%s] Bar[-3]-> RSI(%.2f) Open(%.2f) Close(%.2f) High(%.2f) Low(%.2f) ZigZag(%s) 😁" % (self.previousBars[-3].datetime.date(), self.previousBars[-3].rsi, self.previousBars[-3].open, self.previousBars[-3].close, self.previousBars[-3].high, self.previousBars[-3].low, self.previousBars[-3].zigzag))
        log("😁 [%s] Bar[-2]-> RSI(%.2f) Open(%.2f) Close(%.2f) High(%.2f) Low(%.2f) ZigZag(%s) 😁" % (self.previousBars[-2].datetime.date(), self.previousBars[-2].rsi, self.previousBars[-2].open, self.previousBars[-2].close, self.previousBars[-2].high, self.previousBars[-2].low, self.previousBars[-2].zigzag))
        log("😁 [%s] Bar[-1]-> RSI(%.2f) Open(%.2f) Close(%.2f) High(%.2f) Low(%.2f) ZigZag(%s) 😁" % (self.previousBars[-1].datetime.date(), self.previousBars[-1].rsi, self.previousBars[-1].open, self.previousBars[-1].close, self.previousBars[-1].high, self.previousBars[-1].low, self.previousBars[-1].zigzag))
        log("😁 [%s] CurrentBar-> RSI(%.2f) Open(%.2f) Close(%.2f) High(%.2f) Low(%.2f) ZigZag(%s) 😁" % (self.currentBar.datetime.date(), self.currentBar.rsi, self.currentBar.open, self.currentBar.close, self.currentBar.high, self.currentBar.low, self.currentBar.zigzag))
        log("😁  😁")

        zigzagBar, zigzagIndex = self.getZigZag()
        if (zigzagBar is not None):
            if (self.currentBar.rsi >= self.minRSI or self.currentBar.rsi <= self.maxRSI):
                if (zigzagBar.rsi <= self.minRSI and self.isLonging(zigzagIndex)):
                    type = StrategyResultType.Buy
                    order = self.createOrder(type)
                    return StrategyZigZagResult(strategyData.contract, self.currentBar, type, zigzagIndex, order, None)
                elif (zigzagBar.rsi >= self.maxRSI and self.isShorting(zigzagIndex)):
                    type = StrategyResultType.Sell
                    order = self.createOrder(type)
                    return StrategyZigZagResult(strategyData.contract, self.currentBar, type, zigzagIndex, order, None)
                return StrategyZigZagResult(strategyData.contract, self.currentBar, StrategyResultType.DoNothing, None)
            else:
                return StrategyZigZagResult(strategyData.contract, self.currentBar, StrategyResultType.DoNothing, None)
        else:
            return StrategyZigZagResult(strategyData.contract, self.currentBar, StrategyResultType.DoNothing, None)

    def getZigZag(self) -> Tuple[EventZigZag, int]:
        strategyConfig: StrategyZigZagConfig = self.strategyConfig
        index = -1
        zigzagBar = None
        for bar in reversed(self.previousBars):
            if (bar.zigzag == True and (bar.rsi <= self.minRSI or bar.rsi >= self.maxRSI) and index < -strategyConfig.daysAfterZigZag):
                log("🎃 Bar Found %s: %d 🎃" % (self.strategyData.contract.symbol, index))
                zigzagBar = bar
                break
            index -= 1
        return (zigzagBar, index)

    def isShorting(self, startIndex: int):
        index = startIndex + 1
        while (index <= 0):
            if index == 0:
                if (self.previousBars[index-1].high < self.currentBar.high):
                    log("👻 (%.2f) Not Shorting %.2f < %.2f 👻" % (index, self.previousBars[index-1].high, self.currentBar.high))
                    return False
                else:
                    log("👻 😁 (%.2f) Shorting %.2f > %.2f 😁 👻" % (index, self.previousBars[index-1].high, self.currentBar.high))
            elif (self.previousBars[index-1].high < self.previousBars[index].high):
                log("👻  (%.2f) Not Shorting %.2f < %.2f 👻" % (index, self.previousBars[index-1].high, self.previousBars[index].high))
                return False
            else:
                log("👻 😁 (%.2f) Shorting %.2f > %.2f 😁 👻" % (index, self.previousBars[index-1].high, self.previousBars[index].high))
            index += 1
        return True

    def isLonging(self, startIndex: int):
        index = startIndex + 1
        while (index <= 0):
            if index == 0:
                if (self.previousBars[index-1].low > self.currentBar.low):
                    log("👻  (%.2f) Not Longing %.2f > %.2f 👻" % (index, self.previousBars[index-1].low, self.currentBar.low))
                    return False
                else:
                    log("👻 😁 (%.2f) Longing %.2f < %.2f 😁 👻" % (index, self.previousBars[index-1].low, self.currentBar.low))
            elif (self.previousBars[index-1].low > self.previousBars[index].low):
                log("👻 (%.2f) Not Longing %.2f > %.2f 👻" % (index, self.previousBars[index-1].low, self.previousBars[index].low))
                return False
            else:
                log("👻 😁 (%.2f) Longing %.2f < %.2f 😁 👻" % (index, self.previousBars[index-1].low, self.previousBars[index].low))
            index += 1
        return True

    # Constructor

    def fetchInformation(self):
        strategyData: StrategyZigZagData = self.strategyData
        strategyConfig: StrategyZigZagConfig = self.strategyConfig

        # Event Data
        self.currentBar = strategyData.event
        self.previousBars = strategyData.previousEvents
        self.fill = strategyData.fill

        # Strategy Parameters
        self.willingToLose = strategyConfig.willingToLose
        self.stopToLosePercentage = strategyConfig.stopToLosePercentage
        self.profitPercentage = strategyConfig.profitPercentage
        self.maxToInvestPerStockPercentage = strategyConfig.maxToInvestPerStockPercentage
        self.maxToInvestPerStrategy = strategyConfig.maxToInvestPerStrategy

        self.minRSI = strategyConfig.minRSI
        self.maxRSI = strategyConfig.maxRSI

        self.timezone = strategyData.timezone

    # Validations

    def validateStrategy(self):
        handleFillResult = None
        if self.strategyData.fill:
            handleFillResult = self.handleFill()

        if handleFillResult is None:
            if (not self.isConfigsValid() or not self.isStrategyDataValid()):
                return StrategyZigZagResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent)
            else:
                return None
        else:
            return handleFillResult

    def isStrategyDataValid(self):
        return ((self.currentBar is not None) and (self.currentBar.zigzag is not None) and (self.currentBar.rsi is not None) and
                (self.currentBar.open is not None) and (self.currentBar.close is not None) and

                (self.previousBars[-1] is not None) and (self.previousBars[-1].zigzag is not None) and (self.previousBars[-1].rsi is not None) and
                (self.previousBars[-1].open is not None) and (self.previousBars[-1].close is not None) and

                (self.previousBars[-2] is not None) and (self.previousBars[-2].zigzag is not None) and (self.previousBars[-2].rsi is not None) and
                (self.previousBars[-2].open is not None) and (self.previousBars[-2].close is not None) and

                (self.previousBars[-3] is not None) and (self.previousBars[-3].zigzag is not None) and (self.previousBars[-3].rsi is not None) and
                (self.previousBars[-3].open is not None) and (self.previousBars[-3].close is not None) and

                (self.previousBars[-4] is not None) and (self.previousBars[-4].zigzag is not None) and (self.previousBars[-4].rsi is not None) and
                (self.previousBars[-4].open is not None) and (self.previousBars[-4].close is not None))

    def isConfigsValid(self):
        return (self.profitPercentage > 0 and
                self.willingToLose > 0 and
                self.stopToLosePercentage > 0 and
                self.maxToInvestPerStockPercentage > 0)

    # Handlers

    def handleFill(self):
        today = self.strategyData.today # date.today() #date(2021, 5, 21)
        now = self.strategyData.now.astimezone(self.timezone) #datetime.now() #datetime(2021,5,21,17,30)
        strategyConfig: StrategyZigZagConfig = self.strategyConfig
        executionDate = self.fill.date
        dateLimit = today-timedelta(days=strategyConfig.daysBefore)

        if (self.strategyData.position is None and
            dateLimit <= executionDate):
            log("🥵 Cant do nothing with Stock (%s) - You had a Fill for this stock in the last 6 days 🥵" % self.strategyData.contract.symbol)
            return StrategyZigZagResult(self.strategyData.contract, self.currentBar, StrategyResultType.DoNothing)

        elif self.strategyData.position is not None:
            shares = self.strategyData.position.size
            posisitonsCheckTime = strategyConfig.runPositionsCheckTime
            daysToHold = executionDate+timedelta(days=strategyConfig.daysToHold)
            if (now.hour == posisitonsCheckTime.hour and today >= daysToHold):
                if shares > 0:
                    return StrategyZigZagResult(self.strategyData.contract, self.currentBar, StrategyResultType.PositionExpired_Sell, None, None, self.strategyData.position)
                elif shares < 0:
                    return StrategyZigZagResult(self.strategyData.contract, self.currentBar, StrategyResultType.PositionExpired_Buy, None, None, self.strategyData.position)
            log("🥵 Cant do nothing with Stock (%s) - You already have a position and it's not expired 🥵" % self.strategyData.contract.symbol)
            return StrategyZigZagResult(self.strategyData.contract, self.currentBar, StrategyResultType.KeepPosition)

        return None

    # Calculations

    def getOrderPrice(self, action: OrderAction):
        return self.currentBar.lastPrice

    def calculatePnl(self, action: OrderAction):
        price = self.getOrderPrice(action)
        if action == OrderAction.Buy:
            return price + price * self.profitPercentage
        elif action == OrderAction.Sell:
            return price - price * self.profitPercentage

    def getStopLossPrice(self, action: OrderAction):
        price = self.getOrderPrice(action)
        stopLossPriceRatio = price*self.stopToLosePercentage

        return price - stopLossPriceRatio if action == OrderAction.Buy else price + stopLossPriceRatio

    def getSize(self, action: OrderAction):
        price = self.getOrderPrice(action)
        totalCash = self.strategyData.totalCash
        if self.maxToInvestPerStrategy > 0:
            totalCash = min(self.maxToInvestPerStrategy, self.strategyData.totalCash)
        portfolioLoss = totalCash * self.willingToLose
        stopLossPriceRatio = price*self.stopToLosePercentage

        return int(min(portfolioLoss/stopLossPriceRatio, (totalCash*self.maxToInvestPerStockPercentage)/price))
