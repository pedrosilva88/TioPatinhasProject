import configparser, sys
from pytz import timezone
from helpers import log
from models.base_models import Contract
from country_config.country_manager import getCountryFromCode
from country_config.models import Country
from configs.models import Provider
from backtest.models.base_models import BacktestAction, BacktestDownloadModel, BacktestStrategy, getBacktestStrategyFromCode

class BacktestConfigs:
    provider: Provider
    timezone: timezone
    country: Country
    strategy: BacktestStrategy
    wallet: float

    action: BacktestAction
    contract: Contract
    downloadModel: BacktestDownloadModel

    def __init__(self) -> None:
        settingsConfig = configparser.ConfigParser()
        settingsConfig.read(sys.argv[1])
        
        if settingsConfig['Default']['provider'] == 'TWS':
            self.provider = Provider.TWS

        self.country = getCountryFromCode(settingsConfig['Default']['country'] )
        self.timezone = timezone(settingsConfig['Default']['timezone'])
        self.strategy = getBacktestStrategyFromCode(settingsConfig['Default']['strategy'])
        self.wallet = settingsConfig['Default']['wallet']

        self.action = BacktestAction(settingsConfig['Options']['action'])
        self.contract = Contract(settingsConfig['Options']['symbol'], self.country)

        # TODO: Só falta criar este objecto, já tenho tudo para o poder construir
        #self.downloadModel = BacktestDownloadModel()

        # if self.providerConfigs is None or self.timezone is None:
        #     log("🚨 Unable to get the initial configs 🚨")
        #     sys.exit()