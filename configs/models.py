import sys
import configparser
from pytz import timezone
from helpers import log
from configs.interpreter.tws_interpreter import parseTWSConfigs
from provider_factory.models import ProviderConfigs, Provider

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


