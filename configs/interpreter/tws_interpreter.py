import configparser
from helpers import log
from provider_factory.models import ProviderConfigs

def parseTWSConfigs(config: configparser) -> ProviderConfigs:
    try:
        return ProviderConfigs(version=config['Default']['version'],
                                tradingMode=config['Default']['mode'],
                                user=config['Default']['user'], 
                                password=config['Default']['password'],
                                endpoint=config['Default']['endpoint'],
                                port=config['Default']['port'],
                                clientID=config['Default']['clientID'],
                                connectTimeout=int(config['Default']['connectTimeout']),
                                appStartupTime=int(config['Default']['appStartUpTime']),
                                appTimeout=int(config['Default']['appTimeout']),
                                readOnly=config['Default']['readOnly'],
                                useController=config['TioPatinhas']['useController'])
    except Exception as e:
        print(e)
        log("🚨 Unable to parse Provider Settings 🚨")