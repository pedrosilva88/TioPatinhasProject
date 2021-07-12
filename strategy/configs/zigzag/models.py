from datetime import time, datetime, timedelta

from pytz import timezone
from country_config.models import Market
from strategy.configs.models import StrategyAction, StrategyConfig, StrategyType

class StrategyZigZagConfig(StrategyConfig):
    minRSI: float
    maxRSI: float
    rsiOffsetDays: int
    zigzagSpread: float

    daysToHold: int
    runPositionsCheckTime: time

    barSize: str
    # The number of days that you want to download. This is used to calculate the indicators.
    daysBeforeToDownload: int
    # The number of days to send to the strategy module
    daysBefore: int
    # The number of days after the Zigzag to start to analyze
    daysAfterZigZag: int

    def __init__(self, market: Market,
                        runStrategyTime: time,
                        willingToLose: float, stopToLosePercentage: float, profitPercentage: float,
                        maxToInvestPerStockPercentage: float,
                        maxToInvestPerStock: float,
                        maxToInvestPerStrategy: float,
                        minRSI: float, maxRSI: float,
                        rsiOffsetDays: int, zigzagSpread:float,
                        daysToHold: int,
                        runPositionsCheckTime: time,
                        daysBeforeToDownload: int,
                        daysBefore: int,
                        daysAfterZigZag: int,
                        barSize: str):

        StrategyConfig.__init__(self, market= market, runStrategyTime=runStrategyTime, 
                                willingToLose=willingToLose, stopToLosePercentage= stopToLosePercentage, profitPercentage= profitPercentage, 
                                maxToInvestPerStockPercentage=maxToInvestPerStockPercentage,
                                maxToInvestPerStock= maxToInvestPerStock,
                                maxToInvestPerStrategy= maxToInvestPerStrategy)
                                
        self.type = StrategyType.zigzag
        self.minRSI = minRSI
        self.maxRSI = maxRSI
        self.rsiOffsetDays = rsiOffsetDays
        self.zigzagSpread = zigzagSpread

        self.daysToHold = daysToHold
        self.runPositionsCheckTime = runPositionsCheckTime

        self.daysBeforeToDownload = daysBeforeToDownload
        self.daysBefore = daysBefore

        self.daysAfterZigZag = daysAfterZigZag
        self.barSize = barSize

    def nextProcessDatetime(self, now: datetime) -> datetime:
        currentTime = now.time()
        strategyTime = self.runStrategyTime
        checkPositionsTime = self.runPositionsCheckTime

        if strategyTime > currentTime:
            return datetime.combine(now.date(), self.runStrategyTime, now.tzinfo)
        elif checkPositionsTime > currentTime:
            return datetime.combine(now.date(), self.runPositionsCheckTime, now.tzinfo)
        else:
            nextDay = now.date()+timedelta(days=1)
            return datetime.combine(nextDay, self.runStrategyTime, now.tzinfo)

    def nextAction(self, now: datetime) -> StrategyAction:
        currentTime = now.time()
        strategyTime = self.runStrategyTime
        checkPositionsTime = self.runPositionsCheckTime

        if strategyTime > currentTime:
            return StrategyAction.runStrategy
        elif checkPositionsTime > currentTime:
            return StrategyAction.checkPositions
        else:
            return StrategyAction.runStrategy