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
            openTime = (market.openTime.astimezone(tz)+timedelta(seconds=Constants.ZigZag.runStrategyAfterSeconds)).time()
            checkPositionsTime = (market.closeTime.astimezone(tz)-timedelta(minutes=Constants.ZigZag.runPositionsCheckBeforeMinutes)).time()
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
        runStrategyAfterSeconds = 30
        runPositionsCheckBeforeMinutes = 30
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