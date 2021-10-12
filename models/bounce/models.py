from datetime import datetime
from typing import Any, Union
from models.base_models import Contract, Event

class EventBounce(Event):
    stochK: float
    stochD: float
    ema50: float
    ema100: float
    ema200: float
    ema6: float
    ema18: float
    bollingerBandHigh: float
    bollingerBandLow: float
    macd: float
    macdEMA: float 

    def __init__(self, contract: Contract, 
                        datetime: datetime, 
                        open: float, close: float, 
                        high: float, low: float,
                        stochK: float, stochD: float,
                        ema50: float, ema100: float, ema200: float, ema6: float, ema18: float,
                        bollingerBandHigh: float, bollingerBandLow: float,
                        macd: float, macdEMA: float):
        Event.__init__(self, contract= contract, datetime= datetime,
                        open= open, close= close, high= high, low= low)
        self.stochK = stochK
        self.stochD = stochD
        self.ema50 = ema50
        self.ema100 = ema100
        self.ema200 = ema200
        self.ema6 = ema6
        self.ema18 = ema18
        self.bollingerBandHigh = bollingerBandHigh
        self.bollingerBandLow = bollingerBandLow
        self.macd = macd
        self.macdEMA = macdEMA

    def to_dict(self):
        dict: Union[str, Any] = super().to_dict() 
        dict['stochK'] = self.stochK
        dict['stochD'] = self.stochD
        dict['ema50'] = self.ema50
        dict['ema100'] = self.ema100
        dict['ema200'] = self.ema200
        dict['ema6'] = self.ema6
        dict['ema18'] = self.ema18
        dict['bollingerBandHigh'] = self.bollingerBandHigh
        dict['bollingerBandLow'] = self.bollingerBandLow
        dict['macd'] = self.macd
        dict['macdEMA'] = self.macdEMA

        return dict