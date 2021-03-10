from enum import Enum
from datetime import datetime
from models import Order
from ib_insync import Ticker as ibTicker, Position as ibPosition

class StrategyResultType(Enum):
    def __str__(self):
        if self.value == 0: return "Ignore Event"
        elif self.value == 1: return "Do nothing"
        elif self.value == 2: return "Buy Ticker"
        elif self.value == 3: return "Sell Ticker"
        elif self.value == 4: return "Time expired (12:30) Sell Ticker"
        elif self.value == 5: return "Time expired (12:30) Buy Ticker"
        elif self.value == 6: return "Keep Position"
        elif self.value == 7: return "Keep Order"
        elif self.value == 8: return "Invalid Time for this Strategy"
        elif self.value == 9: return "Invalid Time for this Strategy - Cancel Order"
        else: return "💀"

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
    CancelOrder = 10

class StrategyData:
    ticker: ibTicker
    position: ibPosition
    order: Order
    totalCash: float

    def __init__(self, ticker: ibTicker,
                        position: ibPosition,
                        order: Order,
                        totalCash: float):
        self.ticker = ticker
        self.position = position
        self.order = order
        self.totalCash = totalCash

class StrategyResult:
    ticker: ibTicker
    type: StrategyResultType
    order: Order = None
    position: ibPosition = None

    def __str__(self):
        return "Result for %s: %s\n" % (self.ticker, self.type.name)

    def __init__(self, ticker: ibTicker, type, order: Order = None, position: ibPosition = None):
        self.ticker = ticker
        self.type = type
        self.order = order
        self.position = position