from datetime import timedelta
from strategy.configs.stoch_diverge.models import StrategyStochDivergeConfig
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
        elif strategyType == StrategyType.stoch_diverge:
            return StrategyConfigFactory.createStochasticDivergeStrategyFor(market, tz)
        elif strategyType == StrategyType.stoch_sma:
            return StrategyConfigFactory.createStochasticDivergeStrategyFor(market, tz)
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

    def createStochasticDivergeStrategyFor(market: Market, tz: timezone) -> StrategyConfig:
        constants = Constants.StochasticDivergence.Default()

        if market.country == market.country.USA:
            constants = Constants.StochasticDivergence.US()
        elif market.country == market.country.UK:
            constants = Constants.StochasticDivergence.UK()
        else:
            print("🚨 Cant Create Stochastic Divergence Strategy for this country - %s 🚨" %
                  market.country)

        openTime = (market.openTime.astimezone(
            tz)-timedelta(seconds=constants.runStrategyBeforeHours)).time()

        return StrategyStochDivergeConfig(market=market, runStrategyTime=openTime,
                                    kPeriod=constants.kPeriod, dPeriod=constants.dPeriod,
                                    smooth=constants.smooth,
                                    minStochK=constants.minStochK, maxStochK=constants.maxStochK,
                                    crossMaxPeriods= constants.crossMaxPeriods, divergenceMaxPeriods=constants.divergenceMaxPeriods,
                                    daysBeforeToDownload=constants.daysBeforeToDownload, daysBefore=constants.daysBefore,
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
                self.maxToInvestPerStrategy = 4000

        class UK(Default):
            def __init__(self):
                Constants.ZigZag.Default.__init__(self)
                self.maxToInvestPerStrategy = 1500
                self.orderType = OrderType.MarketOrder

    class StochasticDivergence:
        class Default:
            runStrategyBeforeHours = 3
            daysBeforeToDownload = 120
            daysBefore = 90
            barSize = "1 day"
            kPeriod = 8
            dPeriod = 3
            smooth = 5
            maxStochK = 80
            minStochK = 20
            crossMaxPeriods = 3
            divergenceMaxPeriods = 6

            def __init__(self):
                None


        class US(Default):
            def __init__(self):
                Constants.StochasticDivergence.Default.__init__(self)

        class UK(Default):
            def __init__(self):
                Constants.StochasticDivergence.Default.__init__(self)
