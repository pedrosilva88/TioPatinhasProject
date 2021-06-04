import configparser, sys
from typing import List
from pytz import timezone
from helpers import log

from country_config.market_manager import MarketManager
from strategy.configs.factory.strategy_config_factory import StrategyConfigFactory
from strategy.configs.models import StrategyConfig, StrategyType
from models.base_models import Contract
from country_config.country_manager import getCountryFromCode
from provider_factory.models import ProviderConfigs, Provider
from country_config.models import Country
from backtest.models.base_models import BacktestAction, BacktestDownloadModel
from configs.interpreter.tws_interpreter import parseTWSConfigs
from backtest.scanner.scanner_manager import BacktestScannerManager

class BacktestConfigs:
    provider: Provider
    providerConfigs: ProviderConfigs
    timezone: timezone
    country: Country
    strategyType: StrategyType
    wallet: float

    action: BacktestAction
    contract: Contract
    downloadModel: BacktestDownloadModel

    strategy: StrategyConfig
    dynamicParameters: List[List[float]]

    def __init__(self) -> None:
        settingsConfig = configparser.ConfigParser()
        settingsConfig.read(sys.argv[1])

        providerConfig = configparser.ConfigParser()
        providerConfig.read(sys.argv[2])
        
        if settingsConfig['Default']['provider'] == 'TWS':
            self.provider = Provider.TWS
            self.providerConfigs = parseTWSConfigs(providerConfig)

        self.country = getCountryFromCode(settingsConfig['Default']['country'] )
        self.timezone = timezone(settingsConfig['Default']['timezone'])
        self.strategyType = StrategyType.strategyFromCode(settingsConfig['Default']['strategy'])
        self.wallet = settingsConfig['Default']['wallet']

        self.action = BacktestAction(int(settingsConfig['Options']['action']))
        self.contract = Contract(settingsConfig['Options']['symbol'], self.country)

        path  = BacktestScannerManager.getPathFileToScanStocks(self.provider, self.country, self.strategyType, self.action)
        nDays = int(settingsConfig['Options']['nDays'])
        barSize = settingsConfig['Options']['barSize']
        self.downloadModel = BacktestDownloadModel(path, nDays, barSize)

        market = MarketManager.getMarketFor(self.country)
        self.strategy = StrategyConfigFactory.createStrategyFor(strategyType=self.strategyType, market=market)
        self.dynamicParameters = settingsConfig['Options']['startegyDynamicConfigs']

        if self.provider is None or self.action is None:
            log("🚨 Unable to get the initial backtest configs 🚨")
            sys.exit()