import sys
import configparser
from typing import List, Tuple
from pytz import timezone
from helpers import log
from configs.interpreter.tws_interpreter import parseTWSConfigs
from provider_factory.models import ProviderConfigs, Provider
from strategy.configs.factory.strategy_config_factory import StrategyConfigFactory
from country_config.market_manager import MarketManager
from country_config.models import Country
from strategy.configs.models import StrategyConfig, StrategyType

class TioPatinhasConfigs:
    providerConfigs: ProviderConfigs
    provider: Provider
    timezone: timezone
    strategies: List[StrategyConfig]

    def __init__(self) -> None:
        settingsConfig = configparser.ConfigParser()
        settingsConfig.read(sys.argv[1])
        
        providerConfig = configparser.ConfigParser()
        providerConfig.read(sys.argv[2])

        if settingsConfig['Default']['provider'] == 'TWS':
            self.provider = Provider.TWS
            self.providerConfigs = parseTWSConfigs(providerConfig)

        self.timezone = timezone(settingsConfig['Default']['timezone'])
        dummyStrategies = eval(settingsConfig.get("Default", "strategies"), {}, {})
        self.strategies = TioPatinhasConfigs.parseStrategies(dummyStrategies, self.timezone)
        if self.providerConfigs is None or self.timezone is None:
            log("🚨 Unable to get the initial configs 🚨")
            sys.exit()

    def parseStrategies(items: List[Tuple[str, str]], tz: timezone) -> List[StrategyConfig]:
        strategies = []
        for item in items:
            keyStrategy = item[0]
            keyCountry = item[1]
            strategyType = None
            country = None
            if keyStrategy == StrategyType.zigzag.value:
                strategyType = StrategyType.zigzag

            if keyCountry == Country.USA.code:
                country = Country.USA

            if strategyType is not None and country is not None:
                market = MarketManager.getMarketFor(country)
                if market is not None:
                    strategy = StrategyConfigFactory.createStrategyFor(strategyType=strategyType, market=market, tz=tz)
                    if strategy is not None:
                        strategies.append(strategy)
                    else:
                        log("🚨 Cant create Strategy for - %s 🚨" % strategyType)
                else:
                    log("🚨 Invalid Market for country - %s 🚨" % country)
            else:
               log("🚨 Invalid strategy or country - %s, %s 🚨" % (keyStrategy, keyCountry))
        return strategies


