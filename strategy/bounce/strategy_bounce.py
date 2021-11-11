from enum import Enum
from strategy.strategy import Strategy
from models.bounce.models import EventBounce
from strategy.bounce.models import StrategyBounceData, StrategyBounceResultType, StrategyBounceResult, ReversalCandletType
from strategy.models import StrategyData, StrategyResult, StrategyResultType
from strategy.configs.models import StrategyConfig
from strategy.configs.bounce.models import StrategyBounceConfig
from helpers.math import round_down
from models.base_models import Order, OrderAction
from typing import List, Tuple
from helpers import log

class CriteriaResultType(Enum):
    success = 0
    failure = 1

class StrategyBounce(Strategy):
    # Properties
    currentBar: EventBounce = None
    reversalCandle: EventBounce = None
    previousBars: List[EventBounce] = None
    criteria: StrategyBounceResultType = None

    def run(self, strategyData: StrategyData, strategyConfig: StrategyConfig) -> StrategyResult:
        self.strategyData = strategyData
        self.strategyConfig = strategyConfig

        self.fetchInformation()
        result = self.validateStrategy()
        if result:
            return result

        criteriaResult, action, reversalCandlePosition, reversalType, emaCross, result = self.computeCriteria1()

        if criteriaResult == CriteriaResultType.failure and result:
            return result

        self.reversalCandle = self.previousBars[reversalCandlePosition]
        self.criteria = StrategyBounceResultType.criteria1
        strategyType = StrategyResultType.Sell if action == OrderAction.Sell else StrategyResultType.Buy
        order = self.createOrder(strategyType)
        criteriaResult = self.computeCriteria2(action, reversalCandlePosition)

        if criteriaResult == CriteriaResultType.failure:
            return StrategyBounceResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent)
        self.criteria = StrategyBounceResultType.criteria2
        result.bracketOrder = order
        result.resultType = self.criteria

        print("(%s)\t CC(%s) RC(%s)\t EMA(%d)\tAction(%s) ReversalType(%s)" % (self.currentBar.contract.symbol, self.currentBar.datetime.date(), self.previousBars[reversalCandlePosition].datetime.date(), emaCross, action.code, reversalType.code))        
        return result

    ### Criteria 1 ###
        ## Look For:
            ## Original 2 candle reversal
            ## Inside Bar 2 candle reversal
            ## Trade Through 2 candle reversal
            ## Single candle reversal
        ## Confirmation Candle

    def computeCriteria1(self) -> Tuple[CriteriaResultType, OrderAction, int, ReversalCandletType, int, StrategyBounceResult]:
        hasConfirmationCandle, action, confirmationCandle = self.isConfirmationCandle(self.currentBar, self.previousBars[-1])
        if hasConfirmationCandle:
            reversalCandles = [(self.previousBars[-1], self.previousBars[-2], -1), (self.previousBars[-2], self.previousBars[-3], -2)]
            for item in reversalCandles:
                hasReversalCandle, reversalType, reversalCandle, emaCross = self.isReversalCandle(item[0], item[1], action)
                if hasReversalCandle:
                    strategyResult = StrategyResultType.Buy if action == OrderAction.Buy else StrategyResultType.Sell
                    return (CriteriaResultType.success, action, item[2], reversalType, emaCross, StrategyBounceResult(self.strategyData.contract, self.currentBar, strategyResult, self.criteria, reversalCandle, confirmationCandle, reversalType, emaCross))
            
        return (CriteriaResultType.failure, None, None, None, None, StrategyBounceResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent))

    ### Criteria 2 ###
        ## Long - EMA_18 > EMA_50 > EMA_100 > EMA_200 / Short - EMA_18 < EMA_50 < EMA_100 < EMA_200 (Check last 20 bars)
        ## Stochastics(5,3,3)
            ## Long
                # Reversal Candle below 30
                # Stoch_K cross above Stoch_D between ConfirmationCandle and ReversalCandle
            ## Short
                # Reversal Candle above 70
                # Stoch_K cross below Stoch_D between ConfirmationCandle and ReversalCandle
        ## MACD(50,100,9)
            ## Long
                # bullish - main line above signal line
                # bearish - if the cross bearish was more than 5 candles ago (Starting from the reversal candle)
            ## Short
                # bearish - main line below signal line
                # bullish - if the cross bullish was more than 5 candles ago (Starting from the reversal candle)
            
    def computeCriteria2(self, action: OrderAction, reversalCandlePosition: int) -> CriteriaResultType:
        emasValid = self.areEMAsValid(action, reversalCandlePosition)
        stochasticValid = self.isStochasticValid(action, reversalCandlePosition)
        macdValid = self.isMACDValid(action, reversalCandlePosition)

        if emasValid and stochasticValid and macdValid:
            return CriteriaResultType.success

        return CriteriaResultType.failure

    def isMACDValid(self, action: OrderAction, reversalCandlePosition: int) -> bool:
        reversalCandle = self.previousBars[reversalCandlePosition]

        if action == OrderAction.Buy:
            if reversalCandle.macd > reversalCandle.macdEMA:
             return True
            for i in range(reversalCandlePosition-5, reversalCandlePosition):
                if self.previousBars[i].macd > self.previousBars[i].macdEMA:
                    return False
            return True

        elif action == OrderAction.Sell:
            if reversalCandle.macd < reversalCandle.macdEMA:
                return True
            for i in range(reversalCandlePosition-5, reversalCandlePosition):
                if self.previousBars[i].macd < self.previousBars[i].macdEMA:
                    return False
            return True

        return False

    def areEMAsValid(self, action: OrderAction, reversalCandlePosition: int) -> bool:
        for i in range(reversalCandlePosition-20, reversalCandlePosition):
            if action == OrderAction.Buy:
                return (self.previousBars[i].ema18 >= self.previousBars[i].ema50 and
                        self.previousBars[i].ema50 >= self.previousBars[i].ema100 and
                        self.previousBars[i].ema100 >= self.previousBars[i].ema200 and
                        self.previousBars[i].ema50 >= self.previousBars[i-1].ema50 and
                        self.previousBars[i].ema100 >= self.previousBars[i-1].ema100 and
                        self.previousBars[i].ema200 >= self.previousBars[i-1].ema200)
            elif action == OrderAction.Sell:
                return (self.previousBars[i].ema18 <= self.previousBars[i].ema50 and
                        self.previousBars[i].ema50 <= self.previousBars[i].ema100 and
                        self.previousBars[i].ema100 <= self.previousBars[i].ema200 and
                        self.previousBars[i].ema50 <= self.previousBars[i-1].ema50 and
                        self.previousBars[i].ema100 <= self.previousBars[i-1].ema100 and
                        self.previousBars[i].ema200 <= self.previousBars[i-1].ema200)
            return False

    def isStochasticValid(self, action: OrderAction, reversalCandlePosition: int) -> bool:
        reversalCandle = self.previousBars[reversalCandlePosition]
        confirmationCandle = self.currentBar
        if action == OrderAction.Buy:
            validStochCondition = (reversalCandle.stochK < reversalCandle.stochD or confirmationCandle.stochK > confirmationCandle.stochD)
            return (reversalCandle.stochK < 30 and
                    reversalCandle.stochD < 30 and
                    validStochCondition)

        elif action == OrderAction.Sell:
            validStochCondition = (reversalCandle.stochK > reversalCandle.stochD or confirmationCandle.stochK < confirmationCandle.stochD)
            return (reversalCandle.stochK > 70 and
                    reversalCandle.stochD > 70)
        return False

    def isReversalCandle(self, reversalCandle: EventBounce, previousReversalCandle: EventBounce, action: OrderAction) -> Tuple[bool, ReversalCandletType, EventBounce, int]:
        has2CandleReversal, candleReversalType, ema2Candle = self.is2CandleReversal(reversalCandle, previousReversalCandle, action)
        hasSingleCandleReversal, emaSingleCandle = self.isSingleCandleReversal(reversalCandle, previousReversalCandle, action)
        if has2CandleReversal:
            return (True, candleReversalType, reversalCandle, ema2Candle)
        elif hasSingleCandleReversal:
            return (True, ReversalCandletType.SingleCandleReversal, reversalCandle, emaSingleCandle)
        return (False, None, None, None)

    def is2CandleReversal(self, reversalCandle: EventBounce, previousReversalCandle: EventBounce, action: OrderAction) -> Tuple[bool, ReversalCandletType, int]:
        hasOriginal2CandleReversal, emaOriginal = self.isOriginal2CandleReversal(reversalCandle, previousReversalCandle, action)
        hasInsideBar2CandleReversal, emaInsideBar = self.isInsideBar2CandleReversal(reversalCandle, previousReversalCandle, action)
        hasTradeThrough2CandleReversal, emaTradeThrough = self.isTradeThrough2CandleReversal(reversalCandle, previousReversalCandle, action)

        if hasOriginal2CandleReversal:
            return (True, ReversalCandletType.Original2CandleReversal, emaOriginal)
        elif hasInsideBar2CandleReversal:
            return (True, ReversalCandletType.InsideBar2CandleReversal, emaInsideBar)
        elif hasTradeThrough2CandleReversal:
            return (True, ReversalCandletType.TradeThroughCandleReversal, emaTradeThrough)

        return (False, None, None)

    def isOriginal2CandleReversal(self, reversalCandle: EventBounce, previousReversalCandle: EventBounce, action: OrderAction) -> Tuple[bool, int]:
        if action == OrderAction.Buy: 
            emas = [50, 100, 200]
            for ema in emas:
                if (self.isBarBodyAboveEMA(reversalCandle, ema) and self.isBarDownShadowExtendingEMA(reversalCandle, ema) and
                    reversalCandle.low < previousReversalCandle.low and self.bottomValueOfBody(reversalCandle) > previousReversalCandle.low):
                    return ((previousReversalCandle.low > self.getEMAValue(previousReversalCandle, ema)), ema) # last confirmation (Previous candle of reversal)
        elif action == OrderAction.Sell:
            emas = [50, 100, 200]
            for ema in emas:
                if (self.isBarBodyBelowEMA(reversalCandle, ema) and self.isBarUpShadowExtendingEMA(reversalCandle, ema) and
                    reversalCandle.high > previousReversalCandle.high and self.topValueOfBody(reversalCandle) < previousReversalCandle.high):
                    return ((previousReversalCandle.high < self.getEMAValue(previousReversalCandle, ema)), ema) # last confirmation (Previous candle of reversal)
        return (False, None)

    def isInsideBar2CandleReversal(self, reversalCandle: EventBounce, previousReversalCandle: EventBounce, action: OrderAction) -> Tuple[bool,int]:
        if action == OrderAction.Buy: 
            emas = [50, 100, 200]
            for ema in emas:
                if (self.isBarBodyAboveEMA(reversalCandle, ema) and self.isBarDownShadowExtendingEMA(reversalCandle, ema) and self.isInsideBar(reversalCandle, previousReversalCandle)):
                    return ((self.isBarBodyAboveEMA(previousReversalCandle, ema) and self.isBarDownShadowExtendingEMA(previousReversalCandle, ema)), ema) # last confirmation (Previous candle of reversal)
        elif action == OrderAction.Sell:
            emas = [50, 100, 200]
            for ema in emas:
                if (self.isBarBodyBelowEMA(reversalCandle, ema) and self.isBarUpShadowExtendingEMA(reversalCandle, ema) and self.isInsideBar(reversalCandle, previousReversalCandle)):
                    return ((self.isBarBodyBelowEMA(previousReversalCandle, ema) and self.isBarUpShadowExtendingEMA(previousReversalCandle, ema)), ema) # last confirmation (Previous candle of reversal)
        return (False, None)

    def isTradeThrough2CandleReversal(self, reversalCandle: EventBounce, previousReversalCandle: EventBounce, action: OrderAction) -> Tuple[bool, int]:
        if action == OrderAction.Buy: 
            emas = [50, 100, 200]
            for ema in emas:
                if (self.isBullishCandle(reversalCandle) and 
                    reversalCandle.open < self.getEMAValue(reversalCandle, ema) and reversalCandle.close > self.getEMAValue(reversalCandle, ema) and
                    reversalCandle.low < previousReversalCandle.low):
                    return ((self.isBearishCandle(previousReversalCandle) and previousReversalCandle.open > self.getEMAValue(previousReversalCandle, ema) and previousReversalCandle.close < self.getEMAValue(previousReversalCandle, ema)), ema) # last confirmation (Previous candle of reversal)
        elif action == OrderAction.Sell:
            emas = [50, 100, 200]
            for ema in emas:
                if (self.isBearishCandle(reversalCandle) and 
                    reversalCandle.open > self.getEMAValue(reversalCandle, ema) and reversalCandle.close < self.getEMAValue(reversalCandle, ema) and
                    reversalCandle.high > previousReversalCandle.high):
                    return ((self.isBullishCandle(previousReversalCandle) and previousReversalCandle.open < self.getEMAValue(previousReversalCandle, ema) and previousReversalCandle.close > self.getEMAValue(previousReversalCandle, ema)), ema) # last confirmation (Previous candle of reversal)
        return (False, None)

    def isSingleCandleReversal(self, reversalCandle: EventBounce, previousReversalCandle: EventBounce, action: OrderAction) -> Tuple[bool, int]:
        if action == OrderAction.Buy:
            if self.isBullishPinBar(reversalCandle):
                emas = [50, 100, 200]
                for ema in emas:
                    if self.isBarBodyAboveEMA(reversalCandle, ema) and self.isBarDownShadowExtendingEMA(reversalCandle, ema):
                        return (True, ema)
                return (False, None)

        elif action == OrderAction.Sell:
            if self.isBearishPinBar(reversalCandle):
                emas = [50, 100, 200]
                for ema in emas:
                    if self.isBarBodyBelowEMA(reversalCandle, ema) and self.isBarUpShadowExtendingEMA(reversalCandle, ema):
                        return (True, ema)
                return (False, None)
        return (False, None)
    
    def isInsideBar(self, reversalCandle: EventBounce, previousReversalCandle: EventBounce) -> bool:
        return reversalCandle.high < previousReversalCandle.high and reversalCandle.low > previousReversalCandle.low

    def bottomValueOfBody(self, bar: EventBounce) -> float:
        return bar.open if bar.open < bar.close else bar.close

    def topValueOfBody(self, bar: EventBounce) -> float:
        return bar.open if bar.open > bar.close else bar.close

    def isBarBodyAboveEMA(self, bar: EventBounce, ema: int) -> bool:
        emaValue = self.getEMAValue(bar, ema)
        if emaValue == None:
            return False

        return bar.open > emaValue and bar.close > emaValue

    def isBarBodyBelowEMA(self, bar: EventBounce, ema: int) -> bool:
        emaValue = self.getEMAValue(bar, ema)
        if emaValue == None:
            return False

        return bar.open < emaValue and bar.close < emaValue

    def isBarUpShadowExtendingEMA(self, bar: EventBounce, ema: int) -> bool:
        emaValue = self.getEMAValue(bar, ema)
        if emaValue == None:
            return False

        return bar.high > emaValue

    def isBarDownShadowExtendingEMA(self, bar: EventBounce, ema: int) -> bool:
        emaValue = self.getEMAValue(bar, ema)
        if emaValue == None:
            return False

        return bar.low < emaValue

    def getEMAValue(self, bar: EventBounce, ema: int) -> float:
        if ema == 50:
            return bar.ema50
        elif ema == 100:
            return bar.ema100
        elif ema == 200:
            return bar.ema200
        return None

    def isBullishPinBar(self, bar: EventBounce) -> bool:
        barSize = bar.high - bar.low
        barTopBodySize = bar.high - (bar.close if bar.close < bar.open else bar.open)
    
        if barSize <= 0: return False
        return (1-(barTopBodySize/barSize)) >= 0.8

    def isBearishPinBar(self, bar: EventBounce) -> bool:
        barSize = bar.high - bar.low
        barBottomBodySize = (bar.close if bar.close > bar.open else bar.open) - bar.low 

        if barSize <= 0: return False 
        return (1-(barBottomBodySize/barSize)) >= 0.8
        
    def getPreviousCandleOf(self, candle: EventBounce) -> Tuple[EventBounce, int]:
        if candle == self.currentBar:
            return (self.previousBars[-1], -1)
        else:
            for i in range(1, len(self.previousBars)):
                bar = self.previousBars[-i]
                if candle == bar:
                    return (self.previousBars[-i-1], -i-1)
        return (None, None)

    def isConfirmationCandle(self, bar: EventBounce, previousBar: EventBounce) -> Tuple[bool, OrderAction, EventBounce]:
        if self.isBullishCandle(bar):
            if bar.low > previousBar.low and bar.close > previousBar.high:
                return (True, OrderAction.Buy, bar)
        elif self.isBearishCandle(bar):
            if bar.high < previousBar.high and bar.close < previousBar.low:
                return (True, OrderAction.Sell, bar)
        return (False, None, None)

    def isBullishCandle(self, bar: EventBounce) -> bool:
        return bar.close > bar.open

    def isBearishCandle(self, bar: EventBounce) -> bool:
        return bar.close <= bar.open

    ## Concepts

    def isTouchingEMA(self, bar: EventBounce, action: OrderAction) -> Tuple[bool, int]:
        if action == OrderAction.Buy: 
            emas = [50, 100, 200]
            for ema in emas:
                if self.isBarDownShadowExtendingEMA(bar, ema) and self.isBarBodyAboveEMA(bar, ema):
                    return (True, ema)
        elif action == OrderAction.Sell:
            emas = [50, 100, 200]
            for ema in emas:
                if self.isBarUpShadowExtendingEMA(bar, ema) and self.isBarBodyBelowEMA(bar, ema):
                    return (True, ema)
        return (False, None)

    ## Constructor

    def fetchInformation(self):
        strategyData: StrategyBounceData = self.strategyData
        strategyConfig: StrategyBounceConfig = self.strategyConfig

        # Event Data

        self.currentBar = strategyData.event
        self.previousBars = strategyData.previousEvents

        # Strategy Data

        self.willingToLose = strategyConfig.willingToLose
        self.maxPeriodsToHoldPosition = strategyConfig.maxPeriodsToHoldPosition
        self.winLossRatio = strategyConfig.winLossRatio

    ## Validations

    def validateStrategy(self):
        if (not self.isConfigsValid() or not self.isStrategyDataValid()):
            log("🚨 Invalid data for %s 🚨" % self.currentBar.contract.symbol)
            return StrategyBounceResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent)
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
    
        ## Orders & Postion Sizing

    def positonSizing(self, criteria: StrategyBounceResultType, action:OrderAction, balance: float, r: float) -> int:
        willingToLose = self.willingToLose
        value = (balance*willingToLose)/(r)
        return int(round_down(value, 0))

    def getPriceTarget(self, action: OrderAction) -> float:
        gap = self.getGap()
        target = self.currentBar.high if action == OrderAction.Buy else self.currentBar.low

        return target+gap if action == OrderAction.Buy else target-gap

    def getStopLossPrice(self, action: OrderAction) -> float:
        gap = self.getGap()
        target = self.reversalCandle.low if action == OrderAction.Buy else self.reversalCandle.high

        return target-gap if action == OrderAction.Buy else target+gap
    
    def getOrderPrice(self, action: OrderAction):
        return self.getPriceTarget(action)

    def calculatePnl(self, action: OrderAction):
        targetPrice = self.getPriceTarget(action)
        stopLossPrice = self.getStopLossPrice(action)
        r = (targetPrice-stopLossPrice)*2 if action == OrderAction.Buy else (stopLossPrice-targetPrice)*2
        return targetPrice+r if action == OrderAction.Buy else targetPrice-r

    def getSize(self, action: OrderAction):
        targetPrice = self.getPriceTarget(action)
        stopLossPrice = self.getStopLossPrice(action)
        balance = self.strategyData.totalCash
        r = targetPrice-stopLossPrice if action == OrderAction.Buy else stopLossPrice-targetPrice
        return self.positonSizing(self.criteria, action, balance, r)

    def getGap(self) -> float:
        if self.currentBar.close < 5 :
            return 0.03
        elif self.currentBar.close >= 5 and self.currentBar.close < 10:
            return 0.04
        elif self.currentBar.close >= 10 and self.currentBar.close < 50:
            return 0.06
        elif self.currentBar.close >= 50 and self.currentBar.close < 100:
            return 0.08
        elif self.currentBar.close >= 100 and self.currentBar.close < 200:
            return 0.12
        elif self.currentBar.close >= 200:
            return 0.18
        return 0.0