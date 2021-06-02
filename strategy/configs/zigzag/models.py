from datetime import time, datetime, timedelta
from country_config.models import Market
from strategy.configs.models import StrategyConfig

class StrategyZigZagConfig(StrategyConfig):
    minRSI: float
    maxRSI: float
    rsiOffsetDays: int
    zigzagSpread: float
    stopToLosePercentage: float
    profitPercentage: float

    daysToHold: int
    runPositionsCheckTime: time

    # The number of days that you want to download. This is used to calculate the indicators.
    daysBeforeToDownload: int
    # The number of days to send to the strategy module
    daysBefore: int

    def __init__(self, market: Market,
                        runStrategyTime: time,
                        willingToLose: float, stopToLosePercentage: float, profitPercentage: float,
                        maxToInvestPerStockPercentage: float, 
                        minRSI: float, maxRSI: float,
                        rsiOffsetDays: int, zigzagSpread:float,
                        daysToHold: int,
                        runPositionsCheckTime: time,
                        daysBeforeToDownload: int,
                        daysBefore: int):

        StrategyConfig.__init__(self, market= market, runStrategyTime=runStrategyTime, willingToLose=willingToLose, maxToInvestPerStockPercentage=maxToInvestPerStockPercentage)
        self.willingToLose = willingToLose
        self.stopToLosePercentage = stopToLosePercentage
        self.maxToInvestPerStockPercentage = maxToInvestPerStockPercentage
        self.profitPercentage = profitPercentage

        self.minRSI = minRSI
        self.maxRSI = maxRSI
        self.rsiOffsetDays = rsiOffsetDays
        self.zigzagSpread = zigzagSpread

        self.daysToHold = daysToHold
        self.runPositionsCheckTime = runPositionsCheckTime

        self.daysBeforeToDownload = daysBeforeToDownload
        self.daysBefore = daysBefore

    def nextProcessDatetime(self, now: datetime) -> datetime:
        currentTime = now.time
        if self.runStrategyTime > currentTime:
            return datetime.combine(now.date, self.runStrategyTime)
        elif self.runPositionsCheckTime > currentTime:
            return datetime.combine(now.date, self.runPositionsCheckTime)
        else:
            nextDay = now.date+timedelta(days=1)
            return datetime.combine(nextDay, self.runStrategyTime)