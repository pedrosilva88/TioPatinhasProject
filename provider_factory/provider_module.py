from typing import Any
from configs.models import Provider, ProviderConfigs

class ProviderClient:
    session: Any

class ProviderClientTWS(ProviderClient):
    def __init__(self, Provide: Provider, providerConfigs: ProviderConfigs) -> None:
        super().__init__()

class ProviderModule:
    def createClient(provider: Provider, providerConfigs: ProviderConfigs) -> ProviderClient:
        pass