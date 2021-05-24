from provider_factory.TWS.models import TWSClient, TWSController
from configs.models import ProviderConfigs

class TWSModule:
    def createClient(providerConfigs: ProviderConfigs) -> TWSClient:
        return TWSClient(providerConfigs=providerConfigs)

    def createController(providerConfigs: ProviderConfigs) -> TWSClient:
        return TWSController(providerConfigs=providerConfigs)        