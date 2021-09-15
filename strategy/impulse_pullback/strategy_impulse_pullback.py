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

        isInsideCandle = self.isPullbackCandle(self.currentBar, self.previousBars[-1])
        isPullbackCandle, pullbackOrderAction = self.isPullbackCandle(self.currentBar, self.previousBars[-1])
        action: OrderAction = pullbackOrderAction
        pullbacksFound: int = 1 if isPullbackCandle == True else 0
        if isPullbackCandle or isInsideCandle:
            for i in range(0, len(self.previousBars)):
                bar = self.previousBars[-i]
                previousBar = self.previousBars[-(i+1)]
                if pullbacksFound > 0:
                    if action == None:
                        print("❌ The action shouldn't be None at this point ❌")
                        return StrategyImpulsePullbackResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent)

                    if self.currentBar.contract.symbol == 'TSLA':
                        print("😘", self.currentBar.datetime, action)

                    if action == OrderAction.Buy and self.isSwingHighCandle(bar, []):
                        pass
                    elif action == OrderAction.Sell and self.isSwingLowCandle(bar, []):
                        pass
                    elif self.isPullbackCandle(bar, previousBar):
                        pullbacksFound += 1
                        if pullbacksFound > 2:
                            print("❌ Too many pullbacks. Ignore Event ❌")
                            return StrategyImpulsePullbackResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent)
                    elif self.isInsideBarCandle(bar, previousBar):
                        continue
                    else:
                        print("❌ Invalid Candle. Ignore Event ❌")
                        return StrategyImpulsePullbackResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent)

                else:
                    pass
    
    def isSwingHighCandle(self, bar: EventImpulsePullback, previousBars: List[EventImpulsePullback]) -> bool:
        return False

    def isSwingLowCandle(self, bar: EventImpulsePullback, previousBars: List[EventImpulsePullback]) -> bool:
        return False

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