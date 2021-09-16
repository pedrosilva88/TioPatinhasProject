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

        self.computeCriteria1()
    
    def logmagico(self, data: str):
        if self.currentBar.datetime.year == 2021 and self.currentBar.datetime.month == 7 and self.currentBar.datetime.day == 45:
            print(data)

    ## 6x18 or MACD cross
    ## Swing Candle
    ## Pullbacks
    def computeCriteria1(self) -> Tuple[StrategyImpulsePullbackResult]:
        isInsideCandle = self.isInsideBarCandle(self.currentBar, self.previousBars[-1])
        isPullbackCandle, pullbackOrderAction = self.isPullbackCandle(self.currentBar, self.previousBars[-1])
        action: OrderAction = pullbackOrderAction
        pullbacksFound: int = 1 if isPullbackCandle == True else 0
        swingCandlePosition = None

        if isPullbackCandle or isInsideCandle:
            for i in range(1, len(self.previousBars)):
                bar = self.previousBars[-i]
                previousBar = self.previousBars[-(i+1)]
                isPullbackCandle, pullbackOrderAction = self.isPullbackCandle(bar, previousBar)
                if pullbacksFound > 0:
                    if action == None:
                        # print("❌ The action shouldn't be None at this point ❌")
                        return StrategyImpulsePullbackResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent)
                    if action == OrderAction.Buy:
                        hasSwingHigh = self.isSwingHighCandle(bar, self.previousBars[-(i+7):-(i)])
                        if hasSwingHigh:
                            swingCandlePosition = i
                            break
                    elif action == OrderAction.Sell:
                        hasSwingLow = self.isSwingLowCandle(bar, self.previousBars[-(i+7):-(i)])
                        if hasSwingLow:
                            swingCandlePosition = i
                            break
                    if isPullbackCandle and pullbackOrderAction == action:
                        pullbacksFound += 1
                        if pullbacksFound > 2:
                            #print("❌ Too many pullbacks. Ignore Event ❌")
                            return StrategyImpulsePullbackResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent)
                    elif self.isInsideBarCandle(bar, previousBar):
                        continue
                    else:
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
                hasCross = self.hasCrossInSwingCandle(action, swingCandlePosition, self.previousBars)
                if hasCross:
                    return
                else:
                    return StrategyImpulsePullbackResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent)

    def hasCrossInSwingCandle(self, action: OrderAction, swingCandlePosition: int, previousBars: List[EventImpulsePullback]) -> bool:
        if self.hasEMACross(action, swingCandlePosition, previousBars):
            print("EMA Swing found 😘", self.currentBar.datetime.date(), action, previousBars[-swingCandlePosition].datetime.date())
            return True
        if self.hasMACDCross(action, swingCandlePosition, previousBars):
            print("MACD Swing found 😘", self.currentBar.datetime.date(), action, previousBars[-swingCandlePosition].datetime.date())
            return True

        return False

    def hasEMACross(self, action: OrderAction, swingCandlePosition: int, previousBars: List[EventImpulsePullback]) -> bool: 
        if action == OrderAction.Buy:
            eventA = previousBars[-(swingCandlePosition)]
            eventB = previousBars[-(swingCandlePosition+1)]
            if eventA.ema6 > eventA.ema18 and eventB.ema6 <= eventB.ema18:
                return True

            eventA = previousBars[-(swingCandlePosition+1)]
            eventB = previousBars[-(swingCandlePosition+2)]
            if eventA.ema6 > eventA.ema18 and eventB.ema6 <= eventB.ema18:
                return True

        elif action == OrderAction.Sell: 
            eventA = previousBars[-(swingCandlePosition)]
            eventB = previousBars[-(swingCandlePosition+1)]
            if eventA.ema6 <= eventA.ema18 and eventB.ema6 > eventB.ema18:
                return True

            eventA = previousBars[-(swingCandlePosition+1)]
            eventB = previousBars[-(swingCandlePosition+2)]
            if eventA.ema6 <= eventA.ema18 and eventB.ema6 > eventB.ema18:
                return True
        
        return False


    def hasMACDCross(self, action: OrderAction, swingCandlePosition: int, previousBars: List[EventImpulsePullback]) -> bool:
        if action == OrderAction.Buy:
            eventA = previousBars[-(swingCandlePosition)]
            eventB = previousBars[-(swingCandlePosition+1)]
            if eventA.macd > eventA.macdEMA and eventB.macd <= eventB.macdEMA:
                return True

            eventA = previousBars[-(swingCandlePosition+1)]
            eventB = previousBars[-(swingCandlePosition+2)]
            if eventA.macd > eventA.macdEMA and eventB.macd <= eventB.macdEMA:
                return True

        elif action == OrderAction.Sell: 
            eventA = previousBars[-(swingCandlePosition)]
            eventB = previousBars[-(swingCandlePosition+1)]
            if eventA.macd <= eventA.macdEMA and eventB.macd > eventB.macdEMA:
                return True

            eventA = previousBars[-(swingCandlePosition+1)]
            eventB = previousBars[-(swingCandlePosition+2)]
            if eventA.macd <= eventA.macd and eventB.macdEMA > eventB.macdEMA:
                return True
        
        return False

    def isSwingHighCandle(self, bar: EventImpulsePullback, previousBars: List[EventImpulsePullback]) -> bool:
        previousBars.reverse()
        for i, event in enumerate(previousBars):
            if event.high >= bar.high:
                return False
        return True

    def isSwingLowCandle(self, bar: EventImpulsePullback, previousBars: List[EventImpulsePullback]) -> bool:
        previousBars.reverse()
        for i, event in enumerate(previousBars):
            if event.low <= bar.low:
                return False
        return True

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