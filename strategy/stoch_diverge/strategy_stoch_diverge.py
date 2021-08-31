from strategy.stoch_diverge.models import StrategyStochDivergeData, StrategyStochDivergeResult
from models.stoch_diverge.models import EventStochDiverge
from database.model import FillDB
from datetime import timedelta, timezone
from strategy.configs.models import StrategyConfig
from typing import List, Tuple
from helpers import log
from strategy.strategy import Strategy
from strategy.models import StrategyData, StrategyResult, StrategyResultType
from strategy.configs.stoch_diverge.models import StrategyStochDivergeConfig
from models.base_models import OrderAction

class StrategyStochDiverge(Strategy):
    # Properties
    currentBar: EventStochDiverge = None
    previousBars: List[EventStochDiverge] = None
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
        crossBars = 3
        diveregeDays = 6
        isEngulfing, state = self.engulfingState()
        if isEngulfing:
            if state == 'short':
                startPreviousBar = self.currentBar
                if startPreviousBar.k <= 80 and startPreviousBar.d <= 80 and startPreviousBar.k < startPreviousBar.d:
                    crossBelowUpperBand = False
                    eventsAboveUpperBand = False
                    for i in range(1, crossBars):
                        previousBar = self.previousBars[-i]
                        if previousBar.k <= 80 and previousBar.d <= 80 and previousBar.k > previousBar.d:
                            crossBelowUpperBand = True
                        elif previousBar.k > 80 and previousBar.d > 80 and previousBar.k > previousBar.d:
                            break

                        if previousBar.k > 80 and previousBar.d > 80 and crossBelowUpperBand:
                            eventsAboveUpperBand = True

                        if crossBelowUpperBand and eventsAboveUpperBand:
                            print("🎃 🎃 ENGULFING 🎃 🎃 ", self.currentBar.contract.symbol)
                            print(previousBar.datetime,"--> K:", previousBar.k, "--> D:", previousBar.d)
                            print("✅ Sell -- Engulfing Date:", self.currentBar.datetime)
                            
                            priceDivergenceFound = False
                            kDivergenceFound = False
                            kOverbought = False
                            barKDivergence = None
                            for j in range(i, diveregeDays):
                                previousBar = self.previousBars[-j]
                                if previousBar.kDivergenceOverbought is not None:
                                    kDivergenceFound = True
                                    barKDivergence = previousBar
                                    if previousBar.k >= 70:
                                        kOverbought = True
                                if previousBar.priceDivergenceOverbought is not None:
                                    priceDivergenceFound = True

                                if priceDivergenceFound and kDivergenceFound:
                                    print("💎 💎 💎 Overbought Divergence Found -- Date:", barKDivergence.datetime)
                                    if kOverbought:
                                        print("💎 💎 💎 Overbought above 80 💎 💎 💎 -- Date:", barKDivergence.datetime)

                                    break
                            print("🎃 🎃 🎃 🎃 \n\n\n\n")
                            break

            if state == 'long':
                startPreviousBar = self.currentBar
                if startPreviousBar.k >= 20 and startPreviousBar.d >= 20 and startPreviousBar.k > startPreviousBar.d:
                    crossAboveLowerBand = False
                    eventsBelowLowerBand = False
                    for i in range(1, crossBars):
                        previousBar = self.previousBars[-i]

                        if previousBar.k >= 20 and previousBar.d >= 20 and previousBar.k < previousBar.d:
                            crossAboveLowerBand = True
                        elif previousBar.k < 20 and previousBar.d < 20 and previousBar.k < previousBar.d:
                            break

                        if previousBar.k < 20 and previousBar.d < 20 and crossAboveLowerBand:
                            eventsBelowLowerBand = True

                        if crossAboveLowerBand and eventsBelowLowerBand:
                            print("🎃 🎃 ENGULFING 🎃 🎃 ", self.currentBar.contract.symbol)
                            print(previousBar.datetime,"--> K:", previousBar.k, "--> D:", previousBar.d)
                            print("✅ Buy -- Engulfing Date:", self.currentBar.datetime)

                            priceDivergenceFound = False
                            kDivergenceFound = False
                            kOversold = False
                            barKDivergence = None
                            for j in range(i, diveregeDays):
                                previousBar = self.previousBars[-j]
                                if previousBar.kDivergenceOversold is not None:
                                    kDivergenceFound = True
                                    barKDivergence = previousBar
                                    if previousBar.k <= 20:
                                        kOversold = True

                                if previousBar.priceDivergenceOversold is not None:
                                    priceDivergenceFound = True

                                if priceDivergenceFound and kDivergenceFound:
                                    print("💎 💎 💎 Oversold Divergence Found -- Date:", barKDivergence.datetime)
                                    if kOversold:
                                        print("💎 💎 💎 Oversold below 20 💎 💎 💎 -- Date:", barKDivergence.datetime)
                                    break
                            print("🎃 🎃 🎃 🎃 \n\n\n\n")
                            break

    def engulfingState(self) -> Tuple[bool, str]:
        previousBar = self.previousBars[-1]
        
        if self.isRedCandle(self.currentBar) and self.isGreenCandle(previousBar):
            if ((self.currentBar.open >= previousBar.close) and
                (self.currentBar.close <= previousBar.open)):
                return (True, 'short')
        elif self.isGreenCandle(self.currentBar) and self.isRedCandle(previousBar):
            if ((self.currentBar.close >= previousBar.open) and
                (self.currentBar.open <= previousBar.close)):
                return (True, 'long')

        return (False, '')

    def isRedCandle(self, event: EventStochDiverge):
        return event.open > event.close

    def isGreenCandle(self, event: EventStochDiverge):
        return event.open < event.close

    # def getZigZag(self) -> Tuple[EventStochDiverge, int]:
    #     strategyConfig: StrategyStochDivergeConfig = self.strategyConfig
    #     index = -1
    #     zigzagBar = None
    #     for bar in reversed(self.previousBars):
    #         if (bar.zigzag == True and (bar.rsi <= self.minRSI or bar.rsi >= self.maxRSI) and index < -strategyConfig.daysAfterZigZag):
    #             log("🎃 Bar Found %s: %d 🎃" % (self.strategyData.contract.symbol, index))
    #             zigzagBar = bar
    #             break
    #         index -= 1
    #     return (zigzagBar, index)

    # def isShorting(self, startIndex: int):
    #     index = startIndex + 1
    #     while (index <= 0):
    #         if index == 0:
    #             if (self.previousBars[index-1].high < self.currentBar.high):
    #                 log("👻 (%.2f) Not Shorting %.2f < %.2f 👻" % (index, self.previousBars[index-1].high, self.currentBar.high))
    #                 return False
    #             else:
    #                 log("👻 😁 (%.2f) Shorting %.2f > %.2f 😁 👻" % (index, self.previousBars[index-1].high, self.currentBar.high))
    #         elif (self.previousBars[index-1].high < self.previousBars[index].high):
    #             log("👻  (%.2f) Not Shorting %.2f < %.2f 👻" % (index, self.previousBars[index-1].high, self.previousBars[index].high))
    #             return False
    #         else:
    #             log("👻 😁 (%.2f) Shorting %.2f > %.2f 😁 👻" % (index, self.previousBars[index-1].high, self.previousBars[index].high))
    #         index += 1
    #     return True

    # def isLonging(self, startIndex: int):
    #     index = startIndex + 1
    #     while (index <= 0):
    #         if index == 0:
    #             if (self.previousBars[index-1].low > self.currentBar.low):
    #                 log("👻  (%.2f) Not Longing %.2f > %.2f 👻" % (index, self.previousBars[index-1].low, self.currentBar.low))
    #                 return False
    #             else:
    #                 log("👻 😁 (%.2f) Longing %.2f < %.2f 😁 👻" % (index, self.previousBars[index-1].low, self.currentBar.low))
    #         elif (self.previousBars[index-1].low > self.previousBars[index].low):
    #             log("👻 (%.2f) Not Longing %.2f > %.2f 👻" % (index, self.previousBars[index-1].low, self.previousBars[index].low))
    #             return False
    #         else:
    #             log("👻 😁 (%.2f) Longing %.2f < %.2f 😁 👻" % (index, self.previousBars[index-1].low, self.previousBars[index].low))
    #         index += 1
    #     return True

    # # Constructor

    def fetchInformation(self):
        strategyData: StrategyStochDivergeData = self.strategyData
        strategyConfig: StrategyStochDivergeConfig = self.strategyConfig

        # Event Data
        self.currentBar = strategyData.event
        self.previousBars = strategyData.previousEvents
        self.fill = strategyData.fill

        # Strategy Parameters
        # self.willingToLose = strategyConfig.willingToLose
        # self.stopToLosePercentage = strategyConfig.stopToLosePercentage
        # self.profitPercentage = strategyConfig.profitPercentage
        # self.maxToInvestPerStockPercentage = strategyConfig.maxToInvestPerStockPercentage
        # self.maxToInvestPerStrategy = strategyConfig.maxToInvestPerStrategy

        # self.minRSI = strategyConfig.minRSI
        # self.maxRSI = strategyConfig.maxRSI

        # self.timezone = strategyData.timezone

    # # Validations

    # def validateStrategy(self):
    #     handleFillResult = None
    #     if self.strategyData.fill:
    #         handleFillResult = self.handleFill()

    #     if handleFillResult is None:
    #         if (not self.isConfigsValid() or not self.isStrategyDataValid()):
    #             return StrategyZigZagResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent)
    #         else:
    #             return None
    #     else:
    #         return handleFillResult

    # def isStrategyDataValid(self):
    #     return ((self.currentBar is not None) and (self.currentBar.zigzag is not None) and (self.currentBar.rsi is not None) and
    #             (self.currentBar.open is not None) and (self.currentBar.close is not None) and

    #             (self.previousBars[-1] is not None) and (self.previousBars[-1].zigzag is not None) and (self.previousBars[-1].rsi is not None) and
    #             (self.previousBars[-1].open is not None) and (self.previousBars[-1].close is not None) and

    #             (self.previousBars[-2] is not None) and (self.previousBars[-2].zigzag is not None) and (self.previousBars[-2].rsi is not None) and
    #             (self.previousBars[-2].open is not None) and (self.previousBars[-2].close is not None) and

    #             (self.previousBars[-3] is not None) and (self.previousBars[-3].zigzag is not None) and (self.previousBars[-3].rsi is not None) and
    #             (self.previousBars[-3].open is not None) and (self.previousBars[-3].close is not None) and

    #             (self.previousBars[-4] is not None) and (self.previousBars[-4].zigzag is not None) and (self.previousBars[-4].rsi is not None) and
    #             (self.previousBars[-4].open is not None) and (self.previousBars[-4].close is not None))

    # def isConfigsValid(self):
    #     return (self.profitPercentage > 0 and
    #             self.willingToLose > 0 and
    #             self.stopToLosePercentage > 0 and
    #             self.maxToInvestPerStockPercentage > 0)

    # # Handlers

    # def handleFill(self):
    #     today = self.strategyData.today # date.today() #date(2021, 5, 21)
    #     now = self.strategyData.now.astimezone(self.timezone) #datetime.now() #datetime(2021,5,21,17,30)
    #     strategyConfig: StrategyZigZagConfig = self.strategyConfig
    #     executionDate = self.fill.date
    #     dateLimit = today-timedelta(days=strategyConfig.daysBefore)

    #     if (self.strategyData.position is None and
    #         dateLimit <= executionDate):
    #         log("🥵 Cant do nothing with Stock (%s) - You had a Fill for this stock in the last 6 days 🥵" % self.strategyData.contract.symbol)
    #         return StrategyZigZagResult(self.strategyData.contract, self.currentBar, StrategyResultType.DoNothing)

    #     elif self.strategyData.position is not None:
    #         shares = self.strategyData.position.size
    #         posisitonsCheckTime = strategyConfig.runPositionsCheckTime
    #         daysToHold = executionDate+timedelta(days=strategyConfig.daysToHold)
    #         if (now.hour == posisitonsCheckTime.hour and today >= daysToHold):
    #             if shares > 0:
    #                 return StrategyZigZagResult(self.strategyData.contract, self.currentBar, StrategyResultType.PositionExpired_Sell, None, None, self.strategyData.position)
    #             elif shares < 0:
    #                 return StrategyZigZagResult(self.strategyData.contract, self.currentBar, StrategyResultType.PositionExpired_Buy, None, None, self.strategyData.position)
    #         log("🥵 Cant do nothing with Stock (%s) - You already have a position and it's not expired 🥵" % self.strategyData.contract.symbol)
    #         return StrategyZigZagResult(self.strategyData.contract, self.currentBar, StrategyResultType.KeepPosition)

    #     return None

    # # Calculations

    # def getOrderPrice(self, action: OrderAction):
    #     return self.currentBar.lastPrice

    # def calculatePnl(self, action: OrderAction):
    #     price = self.getOrderPrice(action)
    #     if action == OrderAction.Buy:
    #         return price + price * self.profitPercentage
    #     elif action == OrderAction.Sell:
    #         return price - price * self.profitPercentage

    # def getStopLossPrice(self, action: OrderAction):
    #     price = self.getOrderPrice(action)
    #     stopLossPriceRatio = price*self.stopToLosePercentage

    #     return price - stopLossPriceRatio if action == OrderAction.Buy else price + stopLossPriceRatio

    # def getSize(self, action: OrderAction):
    #     price = self.getOrderPrice(action)
    #     totalCash = self.strategyData.totalCash
    #     if self.maxToInvestPerStrategy > 0:
    #         totalCash = min(self.maxToInvestPerStrategy, self.strategyData.totalCash)
    #     portfolioLoss = totalCash * self.willingToLose
    #     stopLossPriceRatio = price*self.stopToLosePercentage

    #     if (stopLossPriceRatio == 0 or price == 0):
    #         print("Price is 0 for: ", self.strategyData.contract.symbol,
    #               " at:", self.currentBar.datetime.date())
    #         return 0
    #     return int(min(portfolioLoss/stopLossPriceRatio, (totalCash*self.maxToInvestPerStockPercentage)/price))
