from enum import Enum
from datetime import datetime, date, time
from typing import List
from models import Order, CustomBarData
from ib_insync import Ticker as ibTicker, Position as ibPosition, PriceIncrement
from country_config import CountryKey, CountryConfig
from pytz import timezone
from database import FillDB

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
    priceRules: List[PriceIncrement]
    averageVolume: float
    volumeFirstMinute: float
    position: ibPosition
    order: Order
    fill: FillDB
    totalCash: float
    previousBars: List[CustomBarData]
    currentBar: CustomBarData

    def __init__(self, ticker: ibTicker,
                        position: ibPosition,
                        order: Order,
                        totalCash: float,
                        averageVolume: float = None,
                        volumeFirstMinute: float = None,
                        priceRules: List[PriceIncrement] = None,
                        previousBars: List[CustomBarData] = None,
                        currentBar: CustomBarData = None,
                        fill: FillDB = None):
        self.ticker = ticker
        self.position = position
        self.order = order
        self.totalCash = totalCash
        self.averageVolume = averageVolume
        self.volumeFirstMinute = volumeFirstMinute
        self.priceRules = priceRules
        self.previousBars = previousBars
        self.currentBar = currentBar
        self.fill = fill

class StrategyResult:
    ticker: ibTicker
    type: StrategyResultType
    priority: int = None
    order: Order = None
    position: ibPosition = None

    def __str__(self):
        return "Result for %s: %s %s\n" % (self.ticker.contract.symbol, self.ticker.time, self.type.name)

    def __init__(self, ticker: ibTicker, type, order: Order = None, position: ibPosition = None, priority: int = None):
        self.ticker = ticker
        self.type = type
        self.order = order
        self.position = position
        self.priority = priority
