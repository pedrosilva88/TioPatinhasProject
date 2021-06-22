import asyncio
from provider_factory.models import ProviderController

class IslandProtocol:
    controller: ProviderController
    waiter: asyncio.Future
    vaultWaiter: asyncio.Future
