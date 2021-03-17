from enum import Enum
from datetime import datetime, date, time
from models import Order
from ib_insync import Ticker as ibTicker, Position as ibPosition
from country_config import CountryKey, CountryConfig
from pytz import timezone

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
    averageVolume: float
    volumeFirstMinute: float
    position: ibPosition
    order: Order
    totalCash: float

    def __init__(self, ticker: ibTicker,
                        position: ibPosition,
                        order: Order,
                        totalCash: float,
                        averageVolume: float = None,
                        volumeFirstMinute: float = None):
        self.ticker = ticker
        self.position = position
        self.order = order
        self.totalCash = totalCash
        self.averageVolume = averageVolume
        self.volumeFirstMinute = volumeFirstMinute

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

class StrategyConfig():
    startRunningStrategy: datetime
    strategyValidPeriod: datetime
    strategyMaxTime: datetime
    minGap: int
    maxGap: int
    maxLastGap: int = 9
    gapProfitPercentage: float
    willingToLose: float
    stopToLosePercentage: float
    maxToInvestPerStockPercentage: float
    averageVolumePercentage: float #= 1.2 # This means 120% above

    def __init__(self, startRunningStrategy: datetime, strategyValidPeriod: datetime, strategyMaxTime: datetime,
                        minGap: int, maxGap: int, maxLastGap: int, gapProfitPercentage: float,
                        willingToLose: float, stopToLosePercentage: float, 
                        maxToInvestPerStockPercentage: float, averageVolumePercentage: float):
        self.startRunningStrategy = startRunningStrategy
        self.strategyValidPeriod = strategyValidPeriod
        self.strategyMaxTime = strategyMaxTime
        self.minGap = minGap
        self.maxGap = maxGap
        self.maxLastGap = maxLastGap
        self.gapProfitPercentage = gapProfitPercentage
        self.willingToLose = willingToLose
        self.stopToLosePercentage = stopToLosePercentage
        self.maxToInvestPerStockPercentage = maxToInvestPerStockPercentage
        self.averageVolumePercentage = averageVolumePercentage

def getStrategyConfigFor(key: CountryKey, timezone: timezone) -> StrategyConfig:
    if key == CountryKey.USA:
        return StrategyConfig(startRunningStrategy=timezone.localize(datetime.combine(date.today(),time(9,31)), is_dst=None), 
                                strategyValidPeriod=timezone.localize(datetime.combine(date.today(),time(9,45)), is_dst=None),
                                strategyMaxTime=timezone.localize(datetime.combine(date.today(),time(12,30)), is_dst=None), 
                                minGap= 3, maxGap= 8, maxLastGap= 9, gapProfitPercentage= 0.75,
                                willingToLose= 0.05, 
                                stopToLosePercentage= 0.1, 
                                maxToInvestPerStockPercentage= 0.5, 
                                averageVolumePercentage= 1.2)
    if key == CountryKey.UK:
        return StrategyConfig(startRunningStrategy=timezone.localize(datetime.combine(date.today(),time(8,1)), is_dst=None), 
                                strategyValidPeriod=timezone.localize(datetime.combine(date.today(),time(8,15)), is_dst=None),
                                strategyMaxTime=timezone.localize(datetime.combine(date.today(),time(12,0)), is_dst=None), 
                                minGap= 3, maxGap= 8, maxLastGap= 9, gapProfitPercentage= 0.75,
                                willingToLose= 0.05, 
                                stopToLosePercentage= 0.1, 
                                maxToInvestPerStockPercentage= 0.5, 
                                averageVolumePercentage= 1.2)
    else:
        return None