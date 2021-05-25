import configparser, sys
from country_config.market_manager import getMarketFor
from strategy.configs.factory.strategy_config_factory import StrategyConfigFactory
from strategy.configs.models import StrategyConfig, StrategyType
from strategy.strategy import Strategy
from pytz import timezone
from helpers import log
from models.base_models import Contract
from backtest.scanner.scanner_manager import getPathFileToScanStocks
from country_config.country_manager import getCountryFromCode
from provider_factory.models import ProviderConfigs, Provider
from country_config.models import Country
from backtest.models.base_models import BacktestAction, BacktestDownloadModel, BacktestStrategy, getBacktestStrategyFromCode

class BacktestConfigs:
    provider: Provider
    providerConfigs: ProviderConfigs
    timezone: timezone
    country: Country
    strategyType: BacktestStrategy
    wallet: float

    action: BacktestAction
    contract: Contract
    downloadModel: BacktestDownloadModel

    strategy: StrategyConfig

    def __init__(self) -> None:
        settingsConfig = configparser.ConfigParser()
        settingsConfig.read(sys.argv[1])

        providerConfig = configparser.ConfigParser()
        providerConfig.read(sys.argv[2])
        
        if settingsConfig['Default']['provider'] == 'TWS':
            self.provider = Provider.TWS

        self.country = getCountryFromCode(settingsConfig['Default']['country'] )
        self.timezone = timezone(settingsConfig['Default']['timezone'])
        self.strategyType = getBacktestStrategyFromCode(settingsConfig['Default']['strategy'])
        self.wallet = settingsConfig['Default']['wallet']

        self.action = BacktestAction(settingsConfig['Options']['action'])
        self.contract = Contract(settingsConfig['Options']['symbol'], self.country)

        path  = getPathFileToScanStocks(self.provider, self.country, self.strategy, self.action)
        nDays = ['Options']['nDays']
        barSize = ['Options']['barSize']
        self.downloadModel = BacktestDownloadModel(path, nDays, barSize)

        market = getMarketFor(self.country)
        self.strategy = StrategyConfigFactory(strategyType=self.strategyType, market=market)

        if self.provider is None or self.action is None:
            log("🚨 Unable to get the initial backtest configs 🚨")
            sys.exit()