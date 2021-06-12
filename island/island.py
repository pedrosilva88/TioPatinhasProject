import asyncio
from vaults.vaults_controller import VaultsController
from provider_factory.provider_module import ProviderModule
from provider_factory.models import ProviderController
from helpers import log
from configs.models import TioPatinhasConfigs

class IslandProtocol:
    controller: ProviderController
    vaultWaiter: asyncio.Future

class Island(IslandProtocol):
    vaultsController: VaultsController
    waiter: asyncio.Future

    def __init__(self):
        config = TioPatinhasConfigs()
        if config.providerConfigs.useController:
            self.initController()
    
        self.waiter = None
        self.vaultWaiter = None

    def __post_init__(self):
        if not self.controller.sessionController:
            raise ValueError('No controller supplied')
        if not self.controller.provider:
            raise ValueError('No Provider instance supplied')
        if self.controller.isConnected():
            raise ValueError('Provider instance must not be connected')

    def start(self):
        self.vaultsController = VaultsController(self)
        self.controller.runner = asyncio.ensure_future(self.runAsync())
        self.controller.run()

    def stop(self):
        self.controller.disconnect()

    def initController(self):
        config = TioPatinhasConfigs()
        self.controller = ProviderModule.createController(config.provider, config.providerConfigs)
    
    async def runAsync(self):
        config = TioPatinhasConfigs()
        while self.controller.runner:
            try:
                await self.controller.startAsync()
                await asyncio.sleep(config.providerConfigs.appStartupTime)
                await self.controller.provider.connectAsync()

                self.controller.provider.setTimeout()
                # self.subscribeSystemEvents(self.ib)

                while self.controller.runner:
                    self.waiter = asyncio.Future()
                    await self.waiter
                    await self.vaultsController.start()

            except ConnectionRefusedError:
                log("🚨 Connection Refused error 🚨 ")
            except Warning as w:
                self._logger.warning(w)
                log(w)
            except Exception as e:
                self._logger.exception(e)
                log(e)
            finally:
                log("🥺 Finishing 🥺")
                # self.unsubscribeEvents(self.ib)
                # self.vault.databaseModule.closeDatabaseConnection()
                await self.controller.terminateAsync()

                if self.controller.runner:
                    await asyncio.sleep(self.controller.provider.providerConfigs.appTimeout)