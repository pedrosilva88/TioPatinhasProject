from datetime import timedelta
from strategy.configs.zigzag.models import StrategyZigZagConfig
from strategy.configs.models import StrategyConfig, StrategyType
from country_config.models import Market

class StrategyConfigFactory:
    def createStrategyFor(strategyType: StrategyType, market: Market) -> StrategyConfig:
        if strategyType == StrategyType.zigzag:
            return StrategyConfigFactory.createZigZagStrategyFor(market)
        elif strategyType == StrategyType.opg:
            return None
        else:
            return None


    def createZigZagStrategyFor(market: Market) -> StrategyConfig:
        if market == market.country.USA:
            return StrategyZigZagConfig(market= market, runStrategyTime= market.openTime+timedelta(minutes=Constants.ZigZag.runStrategyAfterMinutes),
                                        willingToLose=Constants.ZigZag.willingToLose,
                                        stopToLosePercentage=Constants.ZigZag.stopToLosePercentage, 
                                        profitPercentage=Constants.ZigZag.profitPercentage, 
                                        maxToInvestPerStockPercentage=Constants.ZigZag.maxToInvestPerStockPercentage,
                                        minRSI=Constants.ZigZag.minRSI, maxRSI=Constants.ZigZag.maxRSI, 
                                        rsiOffsetDays=Constants.ZigZag.rsiOffsetDays, zigzagSpread=Constants.ZigZag.zigzagSpread,
                                        runPositionsCheckTime=market.closeTime-timedelta(hours=Constants.ZigZag.runPositionsCheckBeforeHours))

class Constants:
    class ZigZag:
        runStrategyAfterMinutes = 1
        runPositionsCheckBeforeHours = 1
        willingToLose = 0.04
        stopToLosePercentage = 0.02
        profitPercentage = 0.04
        maxToInvestPerStockPercentage = 1
        minRSI = 30
        maxRSI = 70
        rsiOffsetDays = 14
        zigzagSpread = 0.05


## OPG UK ##
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