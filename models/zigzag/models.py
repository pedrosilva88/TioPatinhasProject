from datetime import datetime
from models.base_models import Contract, Event

class EventZigZag(Event):
    zigzag: bool
    rsi: float
    lastPrice: float

    def __init__(self, contract: Contract, 
                        datetime: datetime, 
                        open: float, 
                        close: float, 
                        high: float, 
                        low: float, 
                        volume: float, zigzag: bool, rsi: float, lastPrice = None):
        Event.__init__(self, contract= contract, datetime= datetime,
                        open= open, close= close, high= high, low= low, volume= volume)

        self.lastPrice = lastPrice if lastPrice is not None else close
        self.zigzag = zigzag
        self.rsi = rsi
        