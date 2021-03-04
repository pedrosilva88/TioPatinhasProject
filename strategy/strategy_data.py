from enum import Enum
from datetime import datetime
from order import Ticker, Order, OrderType, StockPosition

class GapType(Enum):
    Long = 1
    Short = 2

class StrategyResultType(Enum):
    IgnoreEvent = 0
    DoNothing = 1
    Buy = 2
    Sell = 3
    PositionExpired_Sell = 4
    PositionExpired_Buy = 5
    KeepPosition = 6
    KeepOrder = 7
    StrategyDateWindowExpired = 8
    StrategyDateWindowExpiredCancelOrder = 9

class StrategyData:
    def __init__(self, ticker: Ticker,
                       datetime: datetime, 
                       ystdClosePrice: float, 
                       openPrice: float, 
                       lastPrice: float, 
                       position: StockPosition, 
                       order: Order,
                       totalCash: float):
        self.ticker = ticker
        self.datetime = datetime
        self.ystdClosePrice = ystdClosePrice
        self.openPrice = openPrice
        self.lastPrice = lastPrice
        self.position = position
        self.order = order
        self.totalCash = totalCash

class StrategyResult:
    ticker: Ticker
    type: StrategyResultType
    order: Order
    position: StockPosition

    def __str__(self):
        return "Result for %s: %s\n" % (self.ticker, self.type.name)

    def __init__(self, ticker: Ticker, type, order: Order = None, position: StockPosition = None):
        self.ticker = ticker
        self.type = type
        self.order = order
        self.position = position