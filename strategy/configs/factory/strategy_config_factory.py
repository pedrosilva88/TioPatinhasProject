from datetime import timedelta
from models.base_models import OrderType
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
        constants = Constants.ZigZag.Default()

        if market.country == market.country.USA:
            constants = Constants.ZigZag.US()
        elif market.country == market.country.UK:
            constants = Constants.ZigZag.UK()
        else:
            print("🚨 Cant Create ZigZag Strategy for this country - %s 🚨" %
                  market.country)

        openTime = (market.openTime.astimezone(
            tz)+timedelta(seconds=constants.runStrategyAfterSeconds)).time()
        checkPositionsTime = (market.closeTime.astimezone(
            tz)-timedelta(minutes=constants.runPositionsCheckBeforeMinutes)).time()

        return StrategyZigZagConfig(market=market, runStrategyTime=openTime,
                                    willingToLose=constants.willingToLose,
                                    stopToLosePercentage=constants.stopToLosePercentage,
                                    profitPercentage=constants.profitPercentage,
                                    maxToInvestPerStockPercentage=constants.maxToInvestPerStockPercentage,
                                    maxToInvestPerStrategy=constants.maxToInvestPerStrategy,
                                    orderType=constants.orderType,
                                    minRSI=constants.minRSI, maxRSI=constants.maxRSI,
                                    rsiOffsetDays=constants.rsiOffsetDays, zigzagSpread=constants.zigzagSpread,
                                    daysToHold=constants.daysToHold,
                                    runPositionsCheckTime=checkPositionsTime,
                                    daysBeforeToDownload=constants.daysBeforeToDownload, daysBefore=constants.daysBefore,
                                    daysAfterZigZag=constants.daysAfterZigZag,
                                    barSize=constants.barSize)


class Constants:
    class ZigZag:
        class Default:
            runStrategyAfterSeconds = ((60*2) + 10)
            runPositionsCheckBeforeMinutes = 38
            willingToLose = 0.03
            stopToLosePercentage = 0.03
            profitPercentage = 0.04
            maxToInvestPerStockPercentage = 1
            maxToInvestPerStrategy = -1
            orderType = OrderType.LimitOrder
            minRSI = 30
            maxRSI = 70
            rsiOffsetDays = 14
            zigzagSpread = 0.05
            daysBeforeToDownload = 90
            daysBefore = 4
            daysToHold = 0
            daysAfterZigZag = 2
            barSize = "1 day"

            def __init__(self):
                None


        class US(Default):
            def __init__(self):
                Constants.ZigZag.Default.__init__(self)
                self.maxToInvestPerStrategy = 1500

        class UK(Default):
            def __init__(self):
                Constants.ZigZag.Default.__init__(self)
                self.maxToInvestPerStrategy = 1500
                self.orderType = OrderType.MarketOrder
