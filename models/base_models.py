from enum import Enum
from country_config.models import Country

class Contract:
    symbol: str
    country: Country
    exchange: str

    def __init__(self, symbol: str, country: Country, exchange: str = "SMART") -> None:
        self.symbol = symbol
        self.country = country
        self.exchange = exchange

    @property
    def currency(self):
        return self.country.currency

class Event:
    contract: Contract
    datetime: datetime

    open: float
    close: float
    high: float
    low: float
    volume: float

    def __init__(self, contract: Contract, 
                        datetime: datetime, 
                        open: float, 
                        close: float, 
                        high: float, 
                        low: float, 
                        volume: float) -> None:
        self.contract = contract
        self.datetime = datetime
        self.open = open
        self.close = close
        self.high = high
        self.low = low
        self.volume = volume

class OrderAction(Enum):
    Buy = "BUY"
    Sell = "SELL"

    @property
    def reverse(self):
        return OrderAction.Sell if self == OrderAction.Buy else OrderAction.Buy

    @property
    def code(self):
        return "Long" if self == OrderAction.Buy else "Short"

class OrderType(Enum):
    LimitOrder = "LMT"
    MarketOrder = "MKT"
    StopOrder = "STP"

class Order:
    action: OrderAction
    type: OrderType
    size: float
    price: float

    def __init__(self, action: OrderAction, type: OrderType, size: int, price: float = None, takeProfitOrder = None, stopLossOrder = None):
        self.action = action
        self.type = type
        self.size = size
        self.price = price

class BracketOrder:
    parentOrder: Order
    takeProfitOrder: Order
    stopLossOrder: Order

    def __init__(self, parentOrder, takeProfitOrder, stopLossOrder):
        self.parentOrder = parentOrder
        self.takeProfitOrder = takeProfitOrder
        self.stopLossOrder = stopLossOrder