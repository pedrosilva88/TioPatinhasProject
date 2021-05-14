import configparser
from helpers import log
from configs.models import ProviderConfigs

def parseTWSConfigs(config: configparser) -> ProviderConfigs:
    try:
        return ProviderConfigs(version=config['Default']['ibVersion'],
                                tradingMode=config['Default']['TradingMode'],
                                user=config['Default']['IbLoginId'], 
                                password=config['Default']['IbPassword'])
    except Exception as e:
        log("🚨 Unable to parse Provider Settings 🚨")