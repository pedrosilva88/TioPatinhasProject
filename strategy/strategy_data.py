from enum import Enum
from datetime import datetime
from order import Order, OrderType, StockPosition

class GapType(Enum):
    Long = 1
    Short = 2

class StrategyResultType(Enum):
    DoNothing = 1
    Buy = 2
    Sell = 3
    PositionExpired_Sell = 4
    PositionExpired_Buy = 5
    KeepPosition = 6
    StrategyDateWindowExpired = 7
    StrategyDateWindowExpiredCancelOrder = 8

class StrategyData:
    def __init__(self, ticker: str,
                       datetime: datetime, 
                       ystdClosePrice: float, 
                       openPrice: float, 
                       lastPrice: float, 
                       position: StockPosition, 
                       order: Order):
        self.ticker = ticker
        self.datetime = datetime
        self.ystdClosePrice = ystdClosePrice
        self.openPrice = openPrice
        self.lastPrice = lastPrice
        self.position = position
        self.order = order

class StrategyResult:
    type: StrategyResultType
    order: Order

    def __init__(self, type, order = None):
        self.type = type
        self.order = order