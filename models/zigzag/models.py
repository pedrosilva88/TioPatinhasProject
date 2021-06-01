from datetime import datetime
from enum import Enum
from typing import Any, Union
from models.base_models import Contract, Event

class ZigZagType(Enum):
    high = 1
    low = -1

class EventZigZag(Event):
    zigzag: bool
    zigzagType: ZigZagType
    rsi: float
    lastPrice: float

    def __init__(self, contract: Contract, 
                        datetime: datetime, 
                        open: float, 
                        close: float, 
                        high: float, 
                        low: float, 
                        volume: float, zigzag: bool, zigzagType: ZigZagType, rsi: float, lastPrice = None):
        Event.__init__(self, contract= contract, datetime= datetime,
                        open= open, close= close, high= high, low= low, volume= volume)

        self.lastPrice = lastPrice if lastPrice is not None else close
        self.zigzag = zigzag
        self.zigzagType = zigzagType
        self.rsi = rsi

    def to_dict(self):
        dict: Union[str, Any] = super().to_dict() 
        dict['zigzag'] = self.zigzag
        dict['zigzagType'] = self.zigzagType
        dict['rsi'] = self.rsi
        dict['lastPrice'] = self.lastPrice