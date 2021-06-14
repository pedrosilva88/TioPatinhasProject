import asyncio
from provider_factory.models import ProviderController

class IslandProtocol:
    controller: ProviderController
    vaultWaiter: asyncio.Future
