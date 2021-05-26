import configparser
from helpers import log
from provider_factory.models import ProviderConfigs

def parseTWSConfigs(config: configparser) -> ProviderConfigs:
    try:
        return ProviderConfigs(version=config['Default']['ibVersion'],
                                tradingMode=config['Default']['TradingMode'],
                                user=config['Default']['IbLoginId'], 
                                password=config['Default']['IbPassword'],
                                endpoint=config['Default']['endpoint'],
                                port=config['Default']['port'],
                                clientID=config['Default']['clientID'],
                                connectTimeout=config['Default']['connectTimeout'],
                                appStartupTime=config['Default']['appStartUpTime'],
                                appTimeout=config['Default']['appTimeout'],
                                readOnly=config['Default']['readOnly'],
                                useController=config['TioPatinhas']['useController'])
    except Exception as e:
        print("ERRRRRO")
        print(e)
        log("🚨 Unable to parse Provider Settings 🚨")