from strategy.stoch_diverge.models import StrategyStochDivergeData, StrategyStochDivergeResult
from models.stoch_diverge.models import EventStochDiverge
from database.model import FillDB
from datetime import date, datetime, timedelta, timezone
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

    # Strategy Parameters
    profitPercentage: float = None
    willingToLose: float = None
    stopToLosePercentage: float = None
    maxToInvestPerStockPercentage: float = 1
    maxToInvestPerStrategy: float = -1

    minStochK: float = None
    maxStochK: float = None
    crossMaxPeriods: int = None
    divergenceMaxPeriods: int = None

    timezone: timezone = None

    maxPeriodsToHoldPosition: int
    takeProfitSafeMargin: float
    minTakeProfitToEnterPosition: int

    def run(self, strategyData: StrategyData, strategyConfig: StrategyConfig) -> StrategyResult:
        self.strategyData = strategyData
        self.strategyConfig = strategyConfig

        self.fetchInformation()
        result = self.validateStrategy()
        if result:
            return result
        
        isEngulfing, orderAction = self.engulfingState()
        isInsideBands = self.isInsideOfTheBands(orderAction)
        if isEngulfing and isInsideBands:
            didCrossInsideBands, crossData, position = self.didCrossInsideBands(orderAction)
            if didCrossInsideBands:
                hasDivergences, barKDivergenceTuple, barPriceDivergenceTuple = self.hasDivergences(orderAction, position)
                if hasDivergences:
                    kDivergenceDate = barKDivergenceTuple[1].kDivergenceOverbought if orderAction == OrderAction.Sell else barKDivergenceTuple[1].kDivergenceOversold
                    barKDivergence_Position_Start, barKDivergence_Data1 = self.getPreviousBar(kDivergenceDate)
                    barKDivergence_Position_Finish, barKDivergence_Data2 = barKDivergenceTuple

                    priceDivergenceDate = barPriceDivergenceTuple[1].priceDivergenceOverbought if orderAction == OrderAction.Sell else barPriceDivergenceTuple[1].priceDivergenceOversold
                    barPriceDivergence_Position_Start, barPriceDivergence_Data1 = self.getPreviousBar(priceDivergenceDate)
                    barPriceDivergence_Position_Finish, barPriceDivergence_Data2 = barPriceDivergenceTuple

                    percentage, targetPrice = self.getTakeProfitPrice(orderAction, (barKDivergence_Position_Start, barKDivergence_Position_Finish), (barPriceDivergence_Position_Start, barPriceDivergence_Position_Finish))
                    
                    if abs(percentage) >= self.minTakeProfitToEnterPosition:
                        log("💎 Stochastic Divergence Found: %s 💎 " % self.currentBar.contract.symbol)
                        log("🔧 Order Type: %s 🔧 " % orderAction.code)
                        log("🍪 Engulfing Candle: %s" % self.currentBar.datetime.date())
                        log("🍩 Cross Inside Bands: (%s) K(%.2f) D(%.2f)" % (crossData.datetime.date(), crossData.k, crossData.d))
                        log("🍫 K Divergence - Point.1[Date(%s) K(-)] Point.2[Date(%s) K(%.2f)" % (kDivergenceDate.date(), barKDivergence_Data2.datetime.date(), barKDivergence_Data2.k))
                        log("🍫 Price Divergence - Point.1[Date(%s) Price(-)] Point.2[Date(%s) Price(%.2f)" % (priceDivergenceDate.date(), barPriceDivergence_Data2.datetime.date(), barPriceDivergence_Data2.close))
                        log("🍫 Take Profit Data: Percentage(%.2f) Price(%.2f)" % (percentage, targetPrice))
                        log("💎 💎 💎 💎 💎 💎 💎 💎 💎 \n\n\n\n")
                        resultType = StrategyResultType.Buy if orderAction == OrderAction.Buy else StrategyResultType.Sell
                        candlesToHold = max(barKDivergence_Position_Start-barKDivergence_Position_Finish, barPriceDivergence_Position_Start-barPriceDivergence_Position_Finish)
                        return StrategyStochDivergeResult(self.currentBar.contract, self.currentBar, resultType, targetPrice, percentage, min(candlesToHold, self.maxPeriodsToHoldPosition))

        return StrategyStochDivergeResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent)

    def getTakeProfitPrice(self, orderAction: OrderAction, kPosition: Tuple[int, int], pricePosition: Tuple[int, int]) -> Tuple[float, float]:
        startPosition = kPosition[0] if kPosition[0] > pricePosition[0] else pricePosition[0]
        finishPosition = kPosition[1] if kPosition[1] < pricePosition[1] else pricePosition[1]

        if orderAction == OrderAction.Buy:
            higherPrice = self.currentBar.high
            for i in range(finishPosition, startPosition):
                previousBar = self.previousBars[-i]
                if previousBar.high > higherPrice:
                    higherPrice = previousBar.high
            higherPrice = higherPrice - higherPrice*self.takeProfitSafeMargin
            percentageValue = (self.currentBar.high/higherPrice)-1
            return (percentageValue, higherPrice)

        elif orderAction == OrderAction.Sell:
            lowerPrice = self.currentBar.low
            for i in range(finishPosition, startPosition):
                previousBar = self.previousBars[-i]
                if previousBar.low < lowerPrice:
                    lowerPrice = previousBar.low
            lowerPrice = lowerPrice + lowerPrice*self.takeProfitSafeMargin
            percentageValue = (lowerPrice/self.currentBar.low)-1
            return (percentageValue, lowerPrice)
        
        return None            

    def getPreviousBar(self, datetime: datetime) -> Tuple[int, EventStochDiverge]:
        for i in range(0, len(self.previousBars)):
            previousBar = self.previousBars[-i]
            if previousBar.datetime == datetime:
                return (i, previousBar)
        return (-1, None)

    def hasDivergences(self, orderAction: OrderAction, barPosition: int) -> Tuple[bool, Tuple[int, EventStochDiverge], Tuple[int, EventStochDiverge]]:
        priceDivergenceFound = False
        kDivergenceFound = False
        kOutsideBands = False
        barKDivergence = None
        barPriceDivergence = None
        for j in range(barPosition, self.divergenceMaxPeriods):
            previousBar = self.previousBars[-j]
            positionK = j
            positionPrice = j

            if orderAction == OrderAction.Sell:
                if previousBar.kDivergenceOverbought is not None:
                    kDivergenceFound = True
                    barKDivergence = previousBar
                    positionK = j
                    if previousBar.k >= self.maxStochK:
                        kOutsideBands = True

                if previousBar.priceDivergenceOverbought is not None:
                    priceDivergenceFound = True
                    barPriceDivergence = previousBar
                    positionPrice = j

            elif orderAction == OrderAction.Buy:
                if previousBar.kDivergenceOversold is not None:
                    kDivergenceFound = True
                    barKDivergence = previousBar
                    positionK = j
                    if previousBar.k <= self.minStochK:
                        kOutsideBands = True

                if previousBar.priceDivergenceOversold is not None:
                    priceDivergenceFound = True
                    barPriceDivergence = previousBar
                    positionPrice = j

            if priceDivergenceFound and kDivergenceFound:
                if kOutsideBands:
                    return (True, (positionK ,barKDivergence), (positionPrice, barPriceDivergence))

        return (False, None, None)

    def didCrossInsideBands(self, orderAction: OrderAction) -> Tuple[bool, EventStochDiverge, int]:
        for i in range(1, self.crossMaxPeriods):
            previousBar = self.previousBars[-i]
            if orderAction == OrderAction.Sell:
                if previousBar.k <= self.maxStochK and previousBar.d <= self.maxStochK and previousBar.k > previousBar.d:
                    return (True, previousBar, i)
                elif previousBar.k > self.maxStochK and previousBar.d > self.maxStochK and previousBar.k > previousBar.d:
                    return (False, None, -1)
            elif orderAction == OrderAction.Buy:
                if previousBar.k >= self.minStochK and previousBar.d >= self.minStochK and previousBar.k < previousBar.d:
                    return (True, previousBar, i)
                elif previousBar.k < self.minStochK and previousBar.d < self.minStochK and previousBar.k < previousBar.d:
                    return (False, None, -1)

        return (False, None, -1)
    
    def isInsideOfTheBands(self, orderAction: OrderAction) -> bool:
        if orderAction == OrderAction.Sell:
            startPreviousBar = self.currentBar
            if startPreviousBar.k <= self.maxStochK and startPreviousBar.d <= self.maxStochK and startPreviousBar.k < startPreviousBar.d:
                return True
        elif orderAction == OrderAction.Buy:
            startPreviousBar = self.currentBar
            if startPreviousBar.k >= self.minStochK and startPreviousBar.d >= self.minStochK and startPreviousBar.k > startPreviousBar.d:
                return True
        return False

    def engulfingState(self) -> Tuple[bool, OrderAction]:
        previousBar = self.previousBars[-1]
        
        if self.isRedCandle(self.currentBar) and self.isGreenCandle(previousBar):
            if ((self.currentBar.open >= previousBar.close) and
                (self.currentBar.close <= previousBar.open)):
                return (True, OrderAction.Sell)
        elif self.isGreenCandle(self.currentBar) and self.isRedCandle(previousBar):
            if ((self.currentBar.close >= previousBar.open) and
                (self.currentBar.open <= previousBar.close)):
                return (True, OrderAction.Buy)

        return (False, None)

    def isRedCandle(self, event: EventStochDiverge):
        return event.open > event.close

    def isGreenCandle(self, event: EventStochDiverge):
        return event.open < event.close

    # # Constructor

    def fetchInformation(self):
        strategyData: StrategyStochDivergeData = self.strategyData
        strategyConfig: StrategyStochDivergeConfig = self.strategyConfig

        # Event Data
        self.currentBar = strategyData.event
        self.previousBars = strategyData.previousEvents

        # Strategy Data
        self.minStochK = strategyConfig.minStochK
        self.maxStochK = strategyConfig.maxStochK

        self.crossMaxPeriods = strategyConfig.crossMaxPeriods
        self.divergenceMaxPeriods = strategyConfig.divergenceMaxPeriods

        self.maxPeriodsToHoldPosition = strategyConfig.maxPeriodsToHoldPosition
        self.takeProfitSafeMargin = strategyConfig.takeProfitSafeMargin
        self.minTakeProfitToEnterPosition = strategyConfig.minTakeProfitToEnterPosition

    # Validations

    def validateStrategy(self):
        if (not self.isConfigsValid() or not self.isStrategyDataValid()):
            log("🚨 Invalid data for %s 🚨" % self.currentBar.contract.symbol)
            return StrategyStochDivergeResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent)
        else:
            return None

    def isStrategyDataValid(self):
        currentBarValid = False
        if ((self.currentBar is not None) and 
            (self.currentBar.k is not None) and 
            (self.currentBar.d is not None) and
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
        return (self.minStochK > 0 and
                self.maxStochK > 0 and
                self.crossMaxPeriods > 0 and
                self.divergenceMaxPeriods > 0)
