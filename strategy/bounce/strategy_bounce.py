from enum import Enum
from strategy.strategy import Strategy
from models.bounce.models import EventBounce
from strategy.bounce.models import StrategyBounceData, StrategyBounceResultType, StrategyBounceResult
from strategy.models import StrategyData, StrategyResult, StrategyResultType
from strategy.configs.models import StrategyConfig
from strategy.configs.bounce.models import StrategyBounceConfig
from helpers.math import round_down
from models.base_models import OrderAction
from typing import List, Tuple
from helpers import log

class CriteriaResultType(Enum):
    success = 0
    failure = 1

class ReversalCandletType(Enum):
    SingleCandleReversal = 0
    Original2CandleReversal = 1
    InsideBar2CandleReversal = 2
    TradeThroughCandleReversal = 3

class StrategyBounce(Strategy):
    # Properties
    currentBar: EventBounce = None
    previousBars: List[EventBounce] = None
    criteria: StrategyBounceResultType = None

    def run(self, strategyData: StrategyData, strategyConfig: StrategyConfig) -> StrategyResult:
        self.strategyData = strategyData
        self.strategyConfig = strategyConfig

        self.fetchInformation()
        result = self.validateStrategy()
        if result:
            return result

        criteriaResult, action, reversalCandlePosition, reversalType, result = self.computeCriteria1()

        if criteriaResult == CriteriaResultType.failure and result:
            return result

        self.criteria = StrategyBounceResultType.criteria1
        strategyType = StrategyResultType.Sell if action == OrderAction.Sell else StrategyResultType.Buy
        order = self.createOrder(strategyType)
        #criteriaResult, result = self.computeCriteria2(action)

        print("(%s) \t⭐️⭐️ \t ReversalCandle(%s) ReversalType(%s) Action(%s)" % (self.currentBar.contract.symbol, self.previousBars[reversalCandlePosition].datetime.date(),reversalType, action.code))

        if criteriaResult == CriteriaResultType.failure:
            #log("(%s) \t⭐️ \t Swing(%s) PB(%s) Action(%s)" % (self.currentBar.contract.symbol, self.previousBars[-swingPosition].datetime.date(),self.currentBar.datetime.date(), action.code))
            #return StrategyImpulsePullbackResult(self.strategyData.contract, self.currentBar, strategyType, StrategyImpulsePullbackResultResultType.criteria1, order)
            return StrategyBounceResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent)
        return StrategyBounceResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent)
        # self.criteria = StrategyBounceResultType.criteria2
        # order = self.createOrder(strategyType)
        # criteriaResult, result = self.computeCriteria3(action, swingPosition)
        
        # if criteriaResult == CriteriaResultType.failure:
        #     #log("(%s) \t⭐️⭐️‍ \t Swing(%s) PB(%s) Action(%s)" % (self.currentBar.contract.symbol, self.previousBars[-swingPosition].datetime.date(),self.currentBar.datetime.date(), action.code))
        #     #return StrategyImpulsePullbackResult(self.strategyData.contract, self.currentBar, strategyType, StrategyImpulsePullbackResultResultType.criteria2, order)
        #     return StrategyBounceResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent)

        # else:
        #     self.criteria = StrategyBounceResultType.criteria3
        #     order = self.createOrder(strategyType)
        #     log("🎃 OrderPrice used for %s: %.2f 🎃" % (self.strategyData.contract.symbol, order.parentOrder.price))
        #     log("\t⭐️ [Create] Type(%s) Size(%i) Price(%.2f) ProfitPrice(%.2f) StopLoss(%.2f) ⭐️" % (action, order.parentOrder.size, order.parentOrder.price, order.takeProfitOrder.price, order.stopLossOrder.price))
        #     log("(%s) \t⭐️⭐️⭐️‍ \t Swing(%s) PB(%s) Action(%s)" % (self.currentBar.contract.symbol, self.previousBars[-swingPosition].datetime.date(),self.currentBar.datetime.date(), action.code))
        #     return StrategyBounceResult(self.strategyData.contract, self.currentBar, strategyType, StrategyBounceResultType.criteria2, order)

    ### Criteria 1 ###
        ## Look For:
            ## Original 2 candle reversal
            ## Inside Bar 2 candle reversal
            ## Trade Through 2 candle reversal
            ## Single candle reversal
        ## Confirmation Candle

    def computeCriteria1(self) -> Tuple[CriteriaResultType, OrderAction, int, ReversalCandletType, StrategyBounceResult]:
        hasConfirmationCandle, action, confirmationCandle = self.isConfirmationCandle(self.currentBar, self.previousBars[-1])
        if hasConfirmationCandle:
            reversalCandles = [(self.previousBars[-1], self.previousBars[-2], -1), (self.previousBars[-2], self.previousBars[-3], -2)]
            for item in reversalCandles:
                hasReversalCandle, reversalType, reversalCandle = self.isReversalCandle(item[0], item[1], action)
                if hasReversalCandle:
                    print("ConfirmationCandle(%s)" % (confirmationCandle.datetime.date()))
                    return (CriteriaResultType.success, action, item[2], reversalType, StrategyBounceResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent))
            
        return (CriteriaResultType.failure, None, None, None, StrategyBounceResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent))

    def isReversalCandle(self, reversalCandle: EventBounce, previousReversalCandle: EventBounce, action: OrderAction) -> Tuple[bool, ReversalCandletType, EventBounce]:
        has2CandleReversal, candleReversalType = self.is2CandleReversal(reversalCandle, previousReversalCandle, action)
        if has2CandleReversal:
            return (True, candleReversalType, reversalCandle)
        else:
            hasSingleCandleReversal = self.isSingleCandleReversal(reversalCandle, previousReversalCandle, action)
            if hasSingleCandleReversal:
                return (True, ReversalCandletType.SingleCandleReversal, reversalCandle)
        return (False, None, None)

    def is2CandleReversal(self, reversalCandle: EventBounce, previousReversalCandle: EventBounce, action: OrderAction) -> Tuple[bool, ReversalCandletType]:
        hasOriginal2CandleReversal = self.isOriginal2CandleReversal(reversalCandle, previousReversalCandle, action)
        hasInsideBar2CandleReversal = self.isInsideBar2CandleReversal(reversalCandle, previousReversalCandle, action)
        hasTradeThrough2CandleReversal = self.isTradeThrough2CandleReversal(reversalCandle, previousReversalCandle, action)

        if hasOriginal2CandleReversal:
            return (True, ReversalCandletType.Original2CandleReversal)
        elif hasInsideBar2CandleReversal:
            return (True, ReversalCandletType.InsideBar2CandleReversal)
        elif hasTradeThrough2CandleReversal:
            return (True, ReversalCandletType.TradeThroughCandleReversal)

        return (False, None)

    def isOriginal2CandleReversal(self, reversalCandle: EventBounce, previousReversalCandle: EventBounce, action: OrderAction) -> bool:
        if action == OrderAction.Buy: 
            emas = [50, 100, 200]
            for ema in emas:
                if (self.isBarBodyAboveEMA(reversalCandle, ema) and self.isBarDownShadowExtendingEMA(reversalCandle, ema) and
                    reversalCandle.low < previousReversalCandle.low and self.bottomValueOfBody(reversalCandle) > previousReversalCandle.low):
                    return previousReversalCandle.low > self.getEMAValue(previousReversalCandle, ema) # last confirmation (Previous candle of reversal)
        elif action == OrderAction.Sell:
            emas = [50, 100, 200]
            for ema in emas:
                if (self.isBarBodyBelowEMA(reversalCandle, ema) and self.isBarUpShadowExtendingEMA(reversalCandle, ema) and
                    reversalCandle.high > previousReversalCandle.high and self.topValueOfBody(reversalCandle) < previousReversalCandle.high):
                    return previousReversalCandle.high < self.getEMAValue(previousReversalCandle, ema) # last confirmation (Previous candle of reversal)
        return False

    def isInsideBar2CandleReversal(self, reversalCandle: EventBounce, previousReversalCandle: EventBounce, action: OrderAction) -> bool:
        if action == OrderAction.Buy: 
            emas = [50, 100, 200]
            for ema in emas:
                if (self.isBarBodyAboveEMA(reversalCandle, ema) and self.isBarDownShadowExtendingEMA(reversalCandle, ema) and self.isInsideBar(reversalCandle, previousReversalCandle)):
                    return self.isBarBodyAboveEMA(previousReversalCandle, ema) and self.isBarDownShadowExtendingEMA(previousReversalCandle, ema) # last confirmation (Previous candle of reversal)
        elif action == OrderAction.Sell:
            emas = [50, 100, 200]
            for ema in emas:
                if (self.isBarBodyBelowEMA(reversalCandle, ema) and self.isBarUpShadowExtendingEMA(reversalCandle, ema) and self.isInsideBar(reversalCandle, previousReversalCandle)):
                    return self.isBarBodyBelowEMA(previousReversalCandle, ema) and self.isBarUpShadowExtendingEMA(previousReversalCandle, ema) # last confirmation (Previous candle of reversal)
        return False

    def isTradeThrough2CandleReversal(self, reversalCandle: EventBounce, previousReversalCandle: EventBounce, action: OrderAction) -> bool:
        if action == OrderAction.Buy: 
            emas = [50, 100, 200]
            for ema in emas:
                if (self.isBullishCandle(reversalCandle) and 
                    reversalCandle.open < self.getEMAValue(reversalCandle, ema) and reversalCandle.close > self.getEMAValue(reversalCandle, ema) and
                    reversalCandle.low < previousReversalCandle.low):
                    return self.isBearishCandle(previousReversalCandle) and reversalCandle.open > self.getEMAValue(reversalCandle, ema) and reversalCandle.close < self.getEMAValue(reversalCandle, ema) # last confirmation (Previous candle of reversal)
        elif action == OrderAction.Sell:
            emas = [50, 100, 200]
            for ema in emas:
                if (self.isBearishCandle(reversalCandle) and 
                    reversalCandle.open > self.getEMAValue(reversalCandle, ema) and reversalCandle.close < self.getEMAValue(reversalCandle, ema) and
                    reversalCandle.high > previousReversalCandle.high):
                    return self.isBullishCandle(previousReversalCandle) and reversalCandle.open < self.getEMAValue(reversalCandle, ema) and reversalCandle.close > self.getEMAValue(reversalCandle, ema) # last confirmation (Previous candle of reversal)
        return False

    def isSingleCandleReversal(self, reversalCandle: EventBounce, previousReversalCandle: EventBounce, action: OrderAction) -> bool:
        if action == OrderAction.Buy:
            if self.isBullishPinBar(reversalCandle):
                emas = [50, 100, 200]
                for ema in emas:
                    if self.isBarBodyAboveEMA(reversalCandle, ema) and self.isBarDownShadowExtendingEMA(reversalCandle, ema):
                        return True
                return False

        elif action == OrderAction.Sell:
            if self.isBearishPinBar(reversalCandle):
                emas = [50, 100, 200]
                for ema in emas:
                    if self.isBarBodyBelowEMA(reversalCandle, ema) and self.isBarDownShadowExtendingEMA(reversalCandle, ema):
                        return True
                return False
        return False
    
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

        return (1-(barSize/barTopBodySize)) >= 0.8

    def isBearishPinBar(self, bar: EventBounce) -> bool:
        barSize = bar.high - bar.low
        barBottomBodySize = (bar.close if bar.close > bar.open else bar.open) - bar.low 

        return (1-(barSize/barBottomBodySize)) >= 0.8
        
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
        target = self.currentBar.low if action == OrderAction.Buy else self.currentBar.high

        return target-gap if action == OrderAction.Buy else target+gap
    
    def getOrderPrice(self, action: OrderAction):
        return self.getPriceTarget(action)

    def calculatePnl(self, action: OrderAction):
        targetPrice = self.getPriceTarget(action)
        stopLossPrice = self.getStopLossPrice(action)
        r = (targetPrice-stopLossPrice)*2.5 if action == OrderAction.Buy else (stopLossPrice-targetPrice)*2.5
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