import sys
import configparser
from enum import Enum
from pytz import timezone
from helpers import log
from configs.interpreter.tws_interpreter import parseTWSConfigs

class Provider(Enum):
    TWS = "TWS"
    Coinbase = "Coinbase"
    Binance = "Binance"

class ProviderConfigs:
    version: str
    tradingMode: str
    user: str
    password: str

    endpoint: str
    port: str
    clientID: str

    connectTimeout: int
    appStartupTime: int
    appTimeout: int
    readOnly: bool

class TioPatinhasConfigs:
    providerConfigs: ProviderConfigs
    provider: Provider
    timezone: timezone

    def __init__(self) -> None:
        settingsConfig = configparser.ConfigParser()
        settingsConfig.read(sys.argv[1])
        
        providerConfig = configparser.ConfigParser()
        providerConfig.read(sys.argv[2])

        if settingsConfig['Default']['provider'] == 'TWS':
            self.provider = Provider.TWS
            self.providerConfigs = parseTWSConfigs(providerConfig)

        self.timezone = timezone(settingsConfig['Default']['timezone'])

        if self.providerConfigs is None or self.timezone is None:
            log("🚨 Unable to get the initial configs 🚨")
            sys.exit()


