from datetime import datetime, time
from enum import Enum

class StrategyType(Enum):
    zigzag = 'zigzag'
    opg = 'opg'
    stochi = 'stochi'

class StrategyConfig:
    runStrategyTime: time

    willingToLose: float
    maxToInvestPerStockPercentage: float

    def __init__(self, runStrategyTime: time, willingToLose: float, maxToInvestPerStockPercentage: float) -> None:
        self.runStrategyTime = runStrategyTime
        self.willingToLose = willingToLose
        self.maxToInvestPerStockPercentage = maxToInvestPerStockPercentage

    def nextProcessDatetime(self, now: datetime) -> datetime:
        pass
# def getStrategyConfigFor(key: CountryKey, timezone: timezone) -> StrategyConfig:
#     if key == CountryKey.USA:
#         return StrategyConfig(startRunningStrategy=timezone.localize(datetime.combine(date.today(),time(9,30,45)), is_dst=None), 
#                                 strategyValidPeriod=timezone.localize(datetime.combine(date.today(),time(9,45)), is_dst=None),
#                                 strategyMaxTime=timezone.localize(datetime.combine(date.today(),time(14,0)), is_dst=None), 
#                                 minGap= 2, maxGap= 8, maxLastGap= 9, gapProfitPercentage= 0.75,
#                                 willingToLose= 0.04,
#                                 stopToLosePercentage= 0.02, 
#                                 maxToInvestPerStockPercentage= 1, 
#                                 averageVolumePercentage= 1.8,
#                                 profitPercentage = 0.04,
#                                 minRSI = 30,
#                                 maxRSI = 70)
#     if key == CountryKey.UK:
#         return StrategyConfig(startRunningStrategy=timezone.localize(datetime.combine(date.today(),time(8,0,45)), is_dst=None), 
#                                 strategyValidPeriod=timezone.localize(datetime.combine(date.today(),time(8,15)), is_dst=None),
#                                 strategyMaxTime=timezone.localize(datetime.combine(date.today(),time(13,0)), is_dst=None), 
#                                 minGap= 2, maxGap= 8, maxLastGap= 9, gapProfitPercentage= 0.75,
#                                 willingToLose= 0.04, 
#                                 stopToLosePercentage= 0.08, 
#                                 maxToInvestPerStockPercentage= 1, 
#                                 averageVolumePercentage= 1.8)
#     else:
#         return None