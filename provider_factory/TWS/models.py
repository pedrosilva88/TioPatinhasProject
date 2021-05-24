from ib_insync import IB, IBC
from configs.models import Provider, ProviderConfigs
from provider_factory.models import ProviderClient, ProviderController

class TWSClient(ProviderClient):
    def __init__(self, providerConfigs: ProviderConfigs) -> None:
        super().__init__()
        self.provider = Provider.TWS

        ib = IB()
        ib.connect(providerConfigs.endpoint, providerConfigs.port, clientId=providerConfigs.clientID)

        self.session = ib

class TWSController(ProviderController):
    def __init__(self, providerConfigs: ProviderConfigs) -> None:
        super().__init__()
        self.provider = Provider.TWS

        self.runner = IBC(version= providerConfigs.version, 
                            tradingMode= providerConfigs.tradingMode, 
                            userid= providerConfigs.user, 
                            password= providerConfigs.password)