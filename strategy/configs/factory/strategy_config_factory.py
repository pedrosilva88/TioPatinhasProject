from datetime import timedelta
from pytz import timezone
from strategy.configs.zigzag.models import StrategyZigZagConfig
from strategy.configs.models import StrategyConfig, StrategyType
from country_config.models import Market

class StrategyConfigFactory:
    def createStrategyFor(strategyType: StrategyType, market: Market, tz: timezone) -> StrategyConfig:
        if strategyType == StrategyType.zigzag:
            return StrategyConfigFactory.createZigZagStrategyFor(market, tz)
        elif strategyType == StrategyType.opg:
            return None
        else:
            return None


    def createZigZagStrategyFor(market: Market, tz: timezone) -> StrategyConfig:
        if market.country == market.country.USA:
            openTime = (market.openTime.astimezone(tz)+timedelta(minutes=Constants.ZigZag.runStrategyAfterMinutes)).time()
            checkPositionsTime = (market.closeTime.astimezone(tz)-timedelta(hours=Constants.ZigZag.runPositionsCheckBeforeHours)).time()
            return StrategyZigZagConfig(market= market, runStrategyTime=openTime,
                                        willingToLose=Constants.ZigZag.willingToLose,
                                        stopToLosePercentage=Constants.ZigZag.stopToLosePercentage, 
                                        profitPercentage=Constants.ZigZag.profitPercentage, 
                                        maxToInvestPerStockPercentage=Constants.ZigZag.maxToInvestPerStockPercentage,
                                        minRSI=Constants.ZigZag.minRSI, maxRSI=Constants.ZigZag.maxRSI, 
                                        rsiOffsetDays=Constants.ZigZag.rsiOffsetDays, zigzagSpread=Constants.ZigZag.zigzagSpread,
                                        daysToHold= Constants.ZigZag.daysToHold,
                                        runPositionsCheckTime=checkPositionsTime,
                                        daysBeforeToDownload=Constants.ZigZag.daysBeforeToDownload, daysBefore=Constants.ZigZag.daysBefore,
                                        daysAfterZigZag=Constants.ZigZag.daysAfterZigZag,
                                        barSize=Constants.ZigZag.barSize)
        else:
            print("🚨 Cant Create ZigZag Strategy for this country - %s 🚨" % market.country)

class Constants:
    class ZigZag:
        runStrategyAfterMinutes = 1
        runPositionsCheckBeforeHours = 1
        willingToLose = 0.04
        stopToLosePercentage = 0.03
        profitPercentage = 0.04
        maxToInvestPerStockPercentage = 1
        minRSI = 30
        maxRSI = 70
        rsiOffsetDays = 14
        zigzagSpread = 0.05
        daysBeforeToDownload = 90
        daysBefore = 4
        daysToHold = 0
        daysAfterZigZag = 2
        barSize = "1 day"

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