from enum import Enum
from datetime import datetime

class OrderType(Enum):
    Long = 1
    Short = 2

class OrderExecutionType(Enum):
    LimitOrder = 1
    MarketPrice = 2
    MidPrice = 3

class Order:
    type: OrderType
    ticker: str
    size: int
    price: float
    executionType: OrderExecutionType
    takeProfitPrice: float
    stopLossPrice: float

    def __init__(self, type, ticker, size, price, executionType, takeProfitPrice = None, stopLossPrice = None):
        self.type = type
        self.ticker = ticker
        self.size = int(size)
        self.price = round(price, 2)
        self.executionType = executionType
        self.takeProfitPrice = round(takeProfitPrice, 2) if not takeProfitPrice == None else takeProfitPrice
        self.stopLossPrice = round(stopLossPrice, 2) if not stopLossPrice == None else stopLossPrice


class StockPosition:
    type: OrderType
    ticker: str
    price: float
    date: datetime
    size: int
    
    def __init__(self, ticker, price, date, size, type):
        self.ticker = ticker
        self.price = price
        self.date = date
        self.size = size
        self.type = type
