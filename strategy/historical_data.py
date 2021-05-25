from datetime import *
from typing import Any, List, Tuple
from pandas import util
from zigzag import peak_valley_pivots_candlestick
from strategy.configs.zigzag.models import StrategyZigZagConfig
from models.zigzag.models import EventZigZag
from models.base_models import Event

class HistoricalData:
    def computeEventsForZigZagStrategy(events: List[Event], strategyConfigs: StrategyZigZagConfig) -> List[EventZigZag]:
        zigzagValues = HistoricalData.calculateZigZag(events, strategyConfigs)
        rsiValues = HistoricalData.calculateRSI(events, strategyConfigs)

        if zigzagValues is None or rsiValues is None:
            return []

        zigzagEvents = []
        i = 0
        for event in events:
            zigzag = True if zigzagValues[i] != 0 else False
            rsi = None
            if i > 0:
                rsi = rsiValues[i-1]

            eventZigZag = EventZigZag(date=event.date,
                                        open=event.open,
                                        high=event.high,
                                        low=event.low,
                                        close=event.close,
                                        volume=event.volume, zigzag=zigzag, rsi=rsi)
            
            zigzagEvents.append(eventZigZag)
            i += 1

        return zigzagEvents

    def computeEventsForOPGStrategy(events: List[Event]) -> Tuple[Any, List[Any]]: #Tuple[ContractDetails, List[PriceIncrement]]
        pass

    def calculateRSI(events: List[Event], strategyConfigs: StrategyZigZagConfig) -> List[float]:
        try:
            RSI = HistoricalData.computeRSI(util.df(events)['close'], strategyConfigs.rsiOffsetDays)
            return RSI.values
        except TypeError as e:
            print(e)
            return None

    def calculateZigZag(events: List[Event], strategyConfigs: StrategyZigZagConfig) -> List[float]:
        try:
            closes = util.df(events)['close']
            lows = util.df(events)['low']
            highs = util.df(events)['high']
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