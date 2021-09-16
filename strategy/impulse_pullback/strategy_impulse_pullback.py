from models.base_models import OrderAction
from typing import List, Tuple
from strategy.strategy import Strategy
from models.impulse_pullback.models import EventImpulsePullback
from strategy.models import StrategyData, StrategyResult, StrategyResultType
from strategy.configs.models import StrategyConfig
from strategy.configs.impulse_pullback.models import StrategyImpulsePullbackConfig
from strategy.impulse_pullback.models import StrategyImpulsePullbackData, StrategyImpulsePullbackResult, StrategyImpulsePullbackResultResultType
from helpers import log

class StrategyImpulsePullback(Strategy):
    # Properties
    currentBar: EventImpulsePullback = None
    previousBars: List[EventImpulsePullback] = None

    # Strategy Parameters
    willingToLose: float = None
    winLossRatio: float
    maxPeriodsToHoldPosition: int

    def run(self, strategyData: StrategyData, strategyConfig: StrategyConfig) -> StrategyResult:
        self.strategyData = strategyData
        self.strategyConfig = strategyConfig

        self.fetchInformation()
        result = self.validateStrategy()
        if result:
            return result

        isInsideCandle = self.isInsideBarCandle(self.currentBar, self.previousBars[-1])
        isPullbackCandle, pullbackOrderAction = self.isPullbackCandle(self.currentBar, self.previousBars[-1])
        action: OrderAction = pullbackOrderAction
        pullbacksFound: int = 1 if isPullbackCandle == True else 0
        swingCandlePosition = None

        if isPullbackCandle or isInsideCandle:
            self.logmagico(isPullbackCandle)
            self.logmagico(isInsideCandle)
            for i in range(1, len(self.previousBars)):
                bar = self.previousBars[-i]
                previousBar = self.previousBars[-(i+1)]
                isPullbackCandle, pullbackOrderAction = self.isPullbackCandle(bar, previousBar)
                self.logmagico(-i)
                if pullbacksFound > 0:
                    if action == None:
                        print("❌ The action shouldn't be None at this point ❌")
                        return StrategyImpulsePullbackResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent)
                    if action == OrderAction.Buy:
                        self.logmagico(self.previousBars[-(i+7):-(i)])

                        hasSwingHigh, swingHighPosition = self.isSwingHighCandle(bar, self.previousBars[-(i+7):-(i)])
                        self.logmagico("Action Buy")
                        if hasSwingHigh:
                            self.logmagico("SwingHigh")
                            swingCandlePosition = swingHighPosition
                            #print("Swing High found 😘", bar.datetime, self.currentBar.datetime, action)
                            break
                    elif action == OrderAction.Sell:
                        hasSwingLow, swingLowPosition = self.isSwingLowCandle(bar, self.previousBars[-(i+7):-(i)])
                        self.logmagico("Action Sell")
                        if hasSwingLow:
                            self.logmagico("SwingLow")
                            swingCandlePosition = swingLowPosition
                            #print("Swing Low found 😘", bar.datetime, self.currentBar.datetime, action)
                            break
                    if isPullbackCandle and pullbackOrderAction == action:
                        self.logmagico("is Pullback")
                        pullbacksFound += 1
                        if pullbacksFound > 2:
                            #print("❌ Too many pullbacks. Ignore Event ❌")
                            return StrategyImpulsePullbackResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent)
                    elif self.isInsideBarCandle(bar, previousBar):
                        self.logmagico("is Inside Bar")
                        continue
                    else:
                        self.logmagico("else")
                        #print("❌ Invalid Candle. Ignore Event ❌")
                        return StrategyImpulsePullbackResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent)
                else:
                    if isPullbackCandle and pullbackOrderAction == action:
                        pullbacksFound += 1
                    elif self.isInsideBarCandle(bar, previousBar):
                        continue
                    else:
                        #print("❌ Invalid Candle. Ignore Event ❌")
                        return StrategyImpulsePullbackResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent)

            if swingCandlePosition is not None:
                self.hasCrossInSwingCandle(action, swingCandlePosition, self.previousBars)
    
    def logmagico(self, data: str):
        if self.currentBar.datetime.year == 2021 and self.currentBar.datetime.month == 7 and self.currentBar.datetime.day == 27:
            print(data)
    def hasCrossInSwingCandle(self, action: OrderAction, swingCandlePosition: int, previousBars: List[EventImpulsePullback]) -> bool:
        if self.hasEMACross(action, swingCandlePosition, previousBars):
            print("Swing found 😘", self.currentBar.datetime.date(), action, previousBars[-swingCandlePosition].datetime.date())
            print("BAMOS")
            return True
        return False

    def hasEMACross(self, action: OrderAction, swingCandlePosition: int, previousBars: List[EventImpulsePullback]) -> bool: 
        if action == OrderAction.Buy:
            eventA = previousBars[-(swingCandlePosition-1)]
            eventB = previousBars[-(swingCandlePosition)]
            if eventA.ema6 > eventA.ema18 and eventB.ema6 <= eventB.ema18:
                return True    

            eventA = previousBars[-(swingCandlePosition)]
            eventB = previousBars[-(swingCandlePosition+1)]
            if eventA.ema6 > eventA.ema18 and eventB.ema6 <= eventB.ema18:
                return True

            eventA = previousBars[-(swingCandlePosition+1)]
            eventB = previousBars[-(swingCandlePosition+2)]
            if eventA.ema6 > eventA.ema18 and eventB.ema6 <= eventB.ema18:
                return True

        elif action == OrderAction.Sell:
            eventA = previousBars[-(swingCandlePosition-1)]
            eventB = previousBars[-(swingCandlePosition)]
            if eventA.ema6 <= eventA.ema18 and eventB.ema6 > eventB.ema18:
                return True    

            eventA = previousBars[-(swingCandlePosition)]
            eventB = previousBars[-(swingCandlePosition+1)]
            if eventA.ema6 <= eventA.ema18 and eventB.ema6 > eventB.ema18:
                return True

            eventA = previousBars[-(swingCandlePosition+1)]
            eventB = previousBars[-(swingCandlePosition+2)]
            if eventA.ema6 <= eventA.ema18 and eventB.ema6 > eventB.ema18:
                return True


    def hasMACDCross(self, action: OrderAction, swingCandlePosition: int, previousBars: List[EventImpulsePullback]) -> bool:
        eventA = previousBars[-(swingCandlePosition-1)]
        eventB = previousBars[-(swingCandlePosition)]
        if action == OrderAction.Buy:
            pass
        elif action == OrderAction.Sell:
            pass

    def isSwingHighCandle(self, bar: EventImpulsePullback, previousBars: List[EventImpulsePullback]) -> Tuple[bool, int]:
        previousBars.reverse()
        for i, event in enumerate(previousBars):
            self.logmagico(event.datetime.date())
            if event.high >= bar.high:
                return (False, i)
        return (True, i)

    def isSwingLowCandle(self, bar: EventImpulsePullback, previousBars: List[EventImpulsePullback]) -> Tuple[bool, int]:
        previousBars.reverse()
        for i, event in enumerate(previousBars):
            if event.low <= bar.low:
                return (False, i)
        return (True, i)

    def isPullbackCandle(self, bar: EventImpulsePullback, previousBar: EventImpulsePullback) -> Tuple[bool, OrderAction]:
        if bar.low < previousBar.low and bar.high < previousBar.high:
            return (True, OrderAction.Buy)
        elif bar.low > previousBar.low and bar.high > previousBar.high:
            return (True, OrderAction.Sell)
        return (False, None)

    def isInsideBarCandle(self, bar: EventImpulsePullback, previousBar: EventImpulsePullback) -> bool:
        return (bar.low > previousBar.low and bar.high < previousBar.high)

    # # Constructor

    def fetchInformation(self):
        strategyData: StrategyImpulsePullbackData = self.strategyData
        strategyConfig: StrategyImpulsePullbackConfig = self.strategyConfig

        # Event Data
        self.currentBar = strategyData.event
        self.previousBars = strategyData.previousEvents

        # Strategy Data

        self.willingToLose = strategyConfig.willingToLose
        self.maxPeriodsToHoldPosition = strategyConfig.maxPeriodsToHoldPosition
        self.winLossRatio = strategyConfig.winLossRatio

    # Validations

    def validateStrategy(self):
        if (not self.isConfigsValid() or not self.isStrategyDataValid()):
            log("🚨 Invalid data for %s 🚨" % self.currentBar.contract.symbol)
            return StrategyImpulsePullbackResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent)
        else:
            return None

    def isStrategyDataValid(self):
        currentBarValid = False
        if ((self.currentBar is not None) and 
            (self.currentBar.stochK is not None) and 
            (self.currentBar.stochD is not None) and
            
            (self.currentBar.ema6 is not None) and 
            (self.currentBar.ema18 is not None) and
            (self.currentBar.ema50 is not None) and 
            (self.currentBar.ema100 is not None) and
            (self.currentBar.ema200 is not None) and 

            (self.currentBar.bollingerBandHigh is not None) and
            (self.currentBar.bollingerBandLow is not None) and 
            (self.currentBar.macd is not None) and 
            (self.currentBar.macdEMA is not None) and

            (self.currentBar.datetime is not None)):
            currentBarValid = True

        previousBarsValid = True
        for previousBar in self.previousBars:
            if ((previousBar is None) or 
                (previousBar.datetime is None)):
                previousBarsValid = False
                break
        return currentBarValid and previousBarsValid

    def isConfigsValid(self):
        return (self.maxPeriodsToHoldPosition > 0 and
                self.winLossRatio > 0 and
                self.willingToLose > 0)