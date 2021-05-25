
from typing import List
from helpers import log
from provider_factory.TWS.tws_module import TWSModule
from models.base_models import Event
from provider_factory.models import ProviderClient, ProviderController
from configs.models import Provider, ProviderConfigs

class ProviderModule:
    def createClient(provider: Provider, providerConfigs: ProviderConfigs) -> ProviderClient:
        if provider == Provider.TWS:
            TWSModule.createClient(providerConfigs)
        else:
            log("🚨 Dont know this Provider - %s 🚨" % provider)

    def createController(provider: Provider, providerConfigs: ProviderConfigs) -> ProviderController:
        if provider == Provider.TWS:
            TWSModule.createController(providerConfigs)
        else:
            log("🚨 Dont know this Provider - %s 🚨" % provider)