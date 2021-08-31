from datetime import datetime
import numpy as np
from numpy.lib import npyio
from strategy.configs.stoch_diverge.models import StrategyStochDivergeConfig
from models.stoch_diverge.models import EventStochDiverge
from typing import Any, List, Tuple, Union
from pandas import DataFrame
import pandas_ta as ta
from zigzag import peak_valley_pivots_candlestick
from strategy.configs.zigzag.models import StrategyZigZagConfig
from models.zigzag.models import EventZigZag, ZigZagType
from models.base_models import Event
from scipy.signal import argrelextrema
from collections import deque

class HistoricalData:
    def computeEventsForZigZagStrategy(events: List[Event], strategyConfigs: StrategyZigZagConfig) -> List[EventZigZag]:
        if len(events) <= 0:
            return []

        zigzagValues = HistoricalData.calculateZigZag(events, strategyConfigs)
        rsiValues = HistoricalData.calculateRSI(events, strategyConfigs)

        if zigzagValues is None or rsiValues is None:
            return []

        zigzagEvents = []
        i = 0
        for event in events:
            zigzag = True if zigzagValues[i] != 0 else False
            zigzagType = None
            if zigzagValues[i] == 1:
                zigzagType = ZigZagType.high
            elif zigzagValues[i] == -1:
                zigzagType = ZigZagType.low
            rsi = None
            if i > 0:
                rsi = rsiValues[i-1]

            eventZigZag = EventZigZag(contract=event.contract,
                                        datetime=event.datetime,
                                        open=event.open,
                                        high=event.high,
                                        low=event.low,
                                        close=event.close,
                                        zigzag=zigzag, zigzagType=zigzagType, rsi=rsi)
            
            zigzagEvents.append(eventZigZag)
            i += 1

        return zigzagEvents

    def computeEventsForOPGStrategy(events: List[Event]) -> Tuple[Any, List[Any]]: #Tuple[ContractDetails, List[PriceIncrement]]
        pass

    def computeEventsForStochDivergeStrategy(events: List[Event], strategyConfigs: StrategyStochDivergeConfig) -> List[EventStochDiverge]:
        if len(events) <= 0:
            return []

        stochDF: DataFrame = HistoricalData.calculateStochasticOscillators(events, strategyConfigs)
        stochOscillatorsValues: Union[datetime, Union[str, float]] = HistoricalData.getStochasticOscillatorsValues(stochDF)

        if stochOscillatorsValues is None:
            return []

        hhCloseValues = HistoricalData.getHigherHighs(stochDF['close'].values)
        llCloseValues = HistoricalData.getLowerLows(stochDF['close'].values)
        hlStochValues = HistoricalData.getHigherLows(stochDF['%K'].values)
        lhStochValues = HistoricalData.getLowerHighs(stochDF['%K'].values)

        stochDivergeEvents = []
        for j, event in enumerate(events):
            stochiValues = stochOscillatorsValues[event.datetime]
            priceDivergenceOverbought=None
            kDivergenceOverbought=None

            priceDivergenceOversold=None
            kDivergenceOversold=None

            for item in lhStochValues:
                if j == item[1]:
                    kDivergenceOverbought = events[item[0]].datetime

            for item in hhCloseValues:
                if j == item[1]:
                    priceDivergenceOverbought = events[item[0]].datetime

            for item in hlStochValues:
                if j == item[1]:
                    kDivergenceOversold = events[item[0]].datetime

            for item in llCloseValues:
                if j == item[1]:
                    priceDivergenceOversold = events[item[0]].datetime

            eventStochDiverge = EventStochDiverge(contract=event.contract,
                                            datetime=event.datetime,
                                            open=event.open,
                                            high=event.high,
                                            low=event.low,
                                            close=event.close,
                                            k=None if np.isnan(stochiValues['%K']) else stochiValues['%K'],
                                            d=None if np.isnan(stochiValues['%D']) else stochiValues['%D'],
                                            priceDivergenceOverbought=priceDivergenceOverbought,
                                            kDivergenceOverbought=kDivergenceOverbought,
                                            priceDivergenceOversold=priceDivergenceOversold,
                                            kDivergenceOversold=kDivergenceOversold)
            
            stochDivergeEvents.append(eventStochDiverge)

        return stochDivergeEvents
    
    def calculateStochasticOscillators(events: List[Event], strategyConfigs: StrategyStochDivergeConfig) -> DataFrame:
        df = ta.DataFrame.from_records([event.to_dict() for event in events], index ="datetime")
        _kName = f'STOCHk_{strategyConfigs.kPeriod}_{strategyConfigs.dPeriod}_{strategyConfigs.smooth}'
        _dName = f'STOCHd_{strategyConfigs.kPeriod}_{strategyConfigs.dPeriod}_{strategyConfigs.smooth}'
        try:
            df.ta.stoch(high='high', low='low', k=strategyConfigs.kPeriod, 
                                            d=strategyConfigs.dPeriod, 
                                            smooth_k=strategyConfigs.smooth, 
                                            append=True)
            return df.rename(columns={_kName: '%K', _dName: '%D'})
        except TypeError as e:
            print(e)
            return None
        except AttributeError as e:
            print(e)
            return None

    def getStochasticOscillatorsValues(df: DataFrame) -> Union[datetime, Union[str, float]]:
        if df is None:
            return None

        return df.filter(items=['%K', '%D']).to_dict('index')

    def calculateRSI(events: List[Event], strategyConfigs: StrategyZigZagConfig) -> List[float]:
        dfEvents = DataFrame.from_records([event.to_dict() for event in events])
        try:
            RSI = HistoricalData.computeRSI(dfEvents['close'], strategyConfigs.rsiOffsetDays)
            return RSI.values
        except TypeError as e:
            print(e)
            return None

    def calculateZigZag(events: List[Event], strategyConfigs: StrategyZigZagConfig) -> List[float]:
        dfEvents = DataFrame.from_records([event.to_dict() for event in events])
        try:
            closes = dfEvents['close']
            lows = dfEvents['low']
            highs = dfEvents['high']
            pivots = peak_valley_pivots_candlestick(closes.values, highs.values, lows.values, strategyConfigs.zigzagSpread, -strategyConfigs.zigzagSpread)
            return pivots
        except TypeError as e:
            print(e)
            return None

    def computeRSI(data, time_window):
        diff = data.diff(1).dropna()

        up_chg = 0 * diff
        down_chg = 0 * diff

        up_chg[diff > 0] = diff[ diff>0 ]

        down_chg[diff < 0] = diff[ diff < 0 ]

        up_chg_avg   = up_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
        down_chg_avg = down_chg.ewm(com=time_window-1 , min_periods=time_window).mean()

        rs = abs(up_chg_avg/down_chg_avg)
        rsi = 100 - 100/(1+rs)
        return rsi

    def getHigherLows(data: np.array, order=5, K=2):
        '''
        Finds consecutive higher lows in price pattern.
        Must not be exceeded within the number of periods indicated by the width 
        parameter for the value to be confirmed.
        K determines how many consecutive lows need to be higher.
        '''
        # Get lows
        low_idx = argrelextrema(data, np.less, order=order)[0]
        lows = data[low_idx]
        # Ensure consecutive lows are higher than previous lows
        extrema = []
        ex_deque = deque(maxlen=K)
        for i, idx in enumerate(low_idx):
            if i == 0:
                ex_deque.append(idx)
                continue
            if lows[i] < lows[i-1]:
                ex_deque.clear()
            ex_deque.append(idx)
            if len(ex_deque) == K:
                extrema.append(ex_deque.copy())
        return extrema

    def getLowerHighs(data: np.array, order=5, K=2):
        '''
        Finds consecutive lower highs in price pattern.
        Must not be exceeded within the number of periods indicated by the width 
        parameter for the value to be confirmed.
        K determines how many consecutive highs need to be lower.
        '''
        # Get highs
        high_idx = argrelextrema(data, np.greater, order=order)[0]
        highs = data[high_idx]
        # Ensure consecutive highs are lower than previous highs
        extrema = []
        ex_deque = deque(maxlen=K)
        for i, idx in enumerate(high_idx):
            if i == 0:
                ex_deque.append(idx)
                continue
            if highs[i] > highs[i-1]:
                ex_deque.clear()
            ex_deque.append(idx)
            if len(ex_deque) == K:
                extrema.append(ex_deque.copy())
        return extrema
    
    def getHigherHighs(data: np.array, order=5, K=2):
        '''
        Finds consecutive higher highs in price pattern.
        Must not be exceeded within the number of periods indicated by the width 
        parameter for the value to be confirmed.
        K determines how many consecutive highs need to be higher.
        '''
        # Get highs
        high_idx = argrelextrema(data, np.greater, order=order)[0]
        highs = data[high_idx]
        # Ensure consecutive highs are higher than previous highs
        extrema = []
        ex_deque = deque(maxlen=K)
        for i, idx in enumerate(high_idx):
            if i == 0:
                ex_deque.append(idx)
                continue
            if highs[i] < highs[i-1]:
                ex_deque.clear()
            ex_deque.append(idx)
            if len(ex_deque) == K:
                extrema.append(ex_deque.copy())
        return extrema
    
    def getLowerLows(data: np.array, order=5, K=2):
        '''
        Finds consecutive lower lows in price pattern.
        Must not be exceeded within the number of periods indicated by the width 
        parameter for the value to be confirmed.
        K determines how many consecutive lows need to be lower.
        '''
        # Get lows
        low_idx = argrelextrema(data, np.less, order=order)[0]
        lows = data[low_idx]
        # Ensure consecutive lows are lower than previous lows
        extrema = []
        ex_deque = deque(maxlen=K)
        for i, idx in enumerate(low_idx):
            if i == 0:
                ex_deque.append(idx)
                continue
            if lows[i] > lows[i-1]:
                ex_deque.clear()
            ex_deque.append(idx)
            if len(ex_deque) == K:
                extrema.append(ex_deque.copy())
        return extrema


        # async def getContractDetails(self, ib: IB, stock: ibContract) -> Tuple[ContractDetails, List[PriceIncrement]]:
        #     contractDetails = await ib.reqContractDetailsAsync(stock)
        #     ruleId = contractDetails[0].marketRuleIds.split(',')[0]
        #     priceIncrementRules = await ib.reqMarketRuleAsync(ruleId)
        #     return (contractDetails, priceIncrementRules)

        # async def getAverageVolume(self, ib: IB, stock: ibContract, days: int = 5):
        #     minute_bars = await self.downloadHistoricDataFromIB(ib=ib, stock=stock, days=days)
        #     value = self.calculateAverageVolume(minute_bars)
        #     return value

        # def calculateAverageVolume(self, datas: List[BarData]):
        #     nBars = len(datas)
        #     if nBars > 0:
        #         sum = 0
        #         for data in datas:
        #             sum += data.volume

        #         return sum/nBars
        #     else:
        #         return None
