from datetime import datetime, time, timedelta
from country_config.models import Market
from strategy.configs.models import StrategyAction, StrategyConfig, StrategyType

class StrategyCombinedConfig(StrategyConfig):
    barSize: str
    # The number of days that you want to download. This is used to calculate the indicators.
    daysBeforeToDownload: int

    impulsePullbackConfig: StrategyConfig
    bounceConfig: StrategyConfig

    def __init__(self, market: Market,
                    runStrategyTime: time,
                    daysBeforeToDownload: int,
                    barSize: str,
                    impulsePullbackConfig: StrategyConfig,
                    bounceConfig: StrategyConfig):

        StrategyConfig.__init__(self, market= market, runStrategyTime=runStrategyTime, 
                                willingToLose= None, stopToLosePercentage= None, profitPercentage= None,
                                maxToInvestPerStockPercentage= None,
                                maxToInvestPerStrategy= None,
                                orderType= None)
                                
        self.type = StrategyType.combined
        self.daysBeforeToDownload = daysBeforeToDownload
        self.barSize = barSize
        self.impulsePullbackConfig = impulsePullbackConfig
        self.bounceConfig = bounceConfig

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