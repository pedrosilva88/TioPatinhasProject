from strategy.configs.zigzag.models import StrategyZigZagConfig
from strategy.configs.models import StrategyConfig, StrategyType
from country_config.models import Market

class StrategyConfigFactory:
    def createStrategyFor(strategyType: StrategyType, market: Market) -> StrategyConfig:
        if strategyType == StrategyType.zigzag:
            return StrategyConfigFactory.createZigZagStrategyFor(market)
        elif strategyType == StrategyType.opg:
            pass
        else:
            pass


    def createZigZagStrategyFor(market: Market) -> StrategyConfig:
        if market == market.country.USA:
            return StrategyZigZagConfig(runStrategyTime= market.openTime)