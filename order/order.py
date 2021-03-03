from enum import Enum
from datetime import datetime

class OrderType(Enum):
    Long = 1
    Short = 2

class OrderExecutionType(Enum):
    LimitOrder = 1
    MarketPrice = 2
    MidPrice = 3

class OrderState(Enum):
    Submitted = "Submitted"
    Filled = "Filled"
    Cancelled = "Cancelled"
    Inactive = "Inactive"

    PendingSubmit = "PendingSubmit"
    PendingCancel = "PendingCancel"
    PreSubmitted = "PreSubmitted"
    ApiPending = "ApiPending"
    ApiCancelled = "ApiCancelled"

class Order:
    type: OrderType
    ticker: str
    size: int
    price: float
    executionType: OrderExecutionType
    takeProfitPrice: float
    stopLossPrice: float
    state: OrderState

    def __init__(self, type, ticker, size, price, executionType, takeProfitPrice = None, stopLossPrice = None, state = OrderState.Submitted):
        self.type = type
        self.ticker = ticker
        self.size = int(size)
        self.price = round(price, 2)
        self.executionType = executionType
        self.takeProfitPrice = round(takeProfitPrice, 2) if not takeProfitPrice == None else takeProfitPrice
        self.stopLossPrice = round(stopLossPrice, 2) if not stopLossPrice == None else stopLossPrice
        self.state = state

class StockPosition:
    type: OrderType
    ticker: str
    price: float
    size: int
    
    def __init__(self, ticker, price, size, type):
        self.ticker = ticker
        self.price = price
        self.size = size
        self.type = type
