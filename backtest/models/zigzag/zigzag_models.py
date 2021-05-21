from datetime import datetime
from models.base_models import Contract
from models.zigzag.models import EventZigZag
from backtest.models.base_models import BacktestItem, BacktestResult

class BacktestZigZagItem(BacktestItem):
    event: EventZigZag

    def __init__(self, contract: Contract, 
                        datetime: datetime, 
                        open: float,
                        close: float,
                        high: float,
                        low: float,
                        volume: float,
                        zigzag= bool, 
                        rsi= float, 
                        lastPrice= float) -> None:
        self.event = EventZigZag(contract= contract, datetime=datetime, 
                                open=open, close=close, high=high, low=low, volume=volume,
                                zigzag= zigzag, rsi= rsi, lastPrice= lastPrice)

class BacktestZigZagResult(BacktestResult):
    pass