from datetime import date, datetime
from enum import Enum
from typing import Any, Union
from models.base_models import Contract, Event

class EventStochDiverge(Event):
    k: float
    d: float
    priceDivergenceOverbought: datetime
    kDivergenceOverbought: datetime
    priceDivergenceOversold: datetime
    kDivergenceOversold: datetime

    def __init__(self, contract: Contract, 
                        datetime: datetime, 
                        open: float, 
                        close: float, 
                        high: float, 
                        low: float,
                        k: float,
                        d: float,
                        priceDivergenceOverbought: datetime,
                        kDivergenceOverbought: datetime,
                        priceDivergenceOversold: datetime,
                        kDivergenceOversold: datetime):
        Event.__init__(self, contract= contract, datetime= datetime,
                        open= open, close= close, high= high, low= low)
        self.k = k
        self.d = d
        self.priceDivergenceOverbought = priceDivergenceOverbought
        self.kDivergenceOverbought = kDivergenceOverbought
        self.priceDivergenceOversold = priceDivergenceOversold
        self.kDivergenceOversold = kDivergenceOversold

    def to_dict(self):
        dict: Union[str, Any] = super().to_dict() 
        dict['k'] = self.k
        dict['d'] = self.d
        dict['priceDivergenceOverbought'] = self.priceDivergenceOverbought
        dict['kDivergenceOverbought'] = self.kDivergenceOverbought
        dict['priceDivergenceOversold'] = self.priceDivergenceOversold
        dict['kDivergenceOversold'] = self.kDivergenceOversold
        return dict