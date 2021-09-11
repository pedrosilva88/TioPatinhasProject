from datetime import datetime, time, timedelta
from models.base_models import OrderType
from country_config.models import Market
from strategy.configs.models import StrategyAction, StrategyConfig, StrategyType

class StrategyStochDivergeConfig(StrategyConfig):
    kPeriod: int
    dPeriod: int
    smooth: int

    minStochK: float
    maxStochK: float
    crossMaxPeriods: int
    divergenceMaxPeriods: int

    barSize: str
    # The number of days that you want to download. This is used to calculate the indicators.
    daysBeforeToDownload: int
    # The number of days to send to the strategy module
    daysBefore: int

    maxPeriodsToHoldPosition: int
    takeProfitSafeMargin: float
    minTakeProfitToEnterPosition: float
    winLossRatio: float

    def __init__(self, market: Market,
                        runStrategyTime: time,
                        willingToLose: float,
                        kPeriod: int, dPeriod: int,
                        smooth: int,
                        minStochK: float,
                        maxStochK: float,
                        crossMaxPeriods: int,
                        divergenceMaxPeriods: int,
                        daysBeforeToDownload: int,
                        daysBefore: int,
                        barSize: str,
                        maxPeriodsToHoldPosition: int,
                        takeProfitSafeMargin: float,
                        minTakeProfitToEnterPosition: float,
                        winLossRatio: float):

        StrategyConfig.__init__(self, market= market, runStrategyTime=runStrategyTime, 
                                willingToLose=willingToLose, stopToLosePercentage= None, profitPercentage= None, 
                                maxToInvestPerStockPercentage=None,
                                maxToInvestPerStrategy= None,
                                orderType= None)
                                
        self.type = StrategyType.stoch_diverge
        self.kPeriod = kPeriod
        self.dPeriod = dPeriod
        self.smooth = smooth

        self.minStochK = minStochK
        self.maxStochK = maxStochK
        self.crossMaxPeriods = crossMaxPeriods
        self.divergenceMaxPeriods = divergenceMaxPeriods

        self.daysBeforeToDownload = daysBeforeToDownload
        self.daysBefore = daysBefore

        self.barSize = barSize

        self.maxPeriodsToHoldPosition = maxPeriodsToHoldPosition
        self.takeProfitSafeMargin = takeProfitSafeMargin
        self.minTakeProfitToEnterPosition = minTakeProfitToEnterPosition
        self.winLossRatio = winLossRatio

    def nextProcessDatetime(self, now: datetime) -> datetime:
        currentTime = now.time()
        strategyTime = self.runStrategyTime

        if strategyTime > currentTime:
            return datetime.combine(now.date(), self.runStrategyTime, now.tzinfo)
        else:
            nextDay = now.date()+timedelta(days=1)
            return datetime.combine(nextDay, self.runStrategyTime, now.tzinfo)

    def nextAction(self, now: datetime) -> StrategyAction:
        currentTime = now.time()
        strategyTime = self.runStrategyTime

        if strategyTime > currentTime:
            return StrategyAction.runStrategy
        else:
            return StrategyAction.runStrategy