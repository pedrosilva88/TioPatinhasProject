import asyncio
import logging
from ib_insync import IB, IBC

from helpers import log
from .zigzag.vault_zigzag import VaultZigZag
from ._events import *
from configs.models import TioPatinhasConfigs
    
class Island(IslandEvents):
    controller: IBC
    ib: IB
    host: str = '127.0.0.1'
    port: int = 7497
    clientId: int = 1
    connectTimeout: float = 5
    appStartupTime: float = 50
    appTimeout: float = 10
    retryDelay: float = 5
    readonly: bool = False
    account: str = ''

    vault: VaultZigZag
    marketWaiter: asyncio.Future

    def __init__(self):
        self.ib = IB()
        self.createIBController()
        self.vault = None
        self._runner = None
        self.waiter = None
        self.marketWaiter = None
        self._logger = logging.getLogger('Tio Patinhas')

    def __post_init__(self):
        if not self.controller:
            raise ValueError('No controller supplied')
        if not self.ib:
            raise ValueError('No IB instance supplied')
        if self.ib.isConnected():
            raise ValueError('IB instance must not be connected')

    def start(self, vault: VaultZigZag):
        self._logger.info('Starting')
        self.vault = vault
        self.vault.ib = self.ib
        self._runner = asyncio.ensure_future(self.runAsync())
        self.ib.run()

    def stop(self):
        self._logger.info('Stopping')
        self.ib.disconnect()
        self._runner = None

    def createIBController(self):
        config = TioPatinhasConfigs()
        self.controller = IBC(version= config.providerConfigs.version, 
                                tradingMode= config.providerConfigs.tradingMode, 
                                userid= config.providerConfigs.user, 
                                password= config.providerConfigs.password)
    
    async def runAsync(self):
        while self._runner:
            try:
                await self.controller.startAsync()
                await asyncio.sleep(self.appStartupTime)
                await self.ib.connectAsync(self.host, self.port, self.clientId, self.connectTimeout,
                    self.readonly, self.account)

                self.ib.setTimeout(self.appTimeout)
                self.subscribeSystemEvents(self.ib)

                while self._runner:
                    self.waiter = asyncio.Future()
                    await self.waiter
                    self._logger.debug('Soft timeout')
                    await self.vault.runMarket()

            except ConnectionRefusedError:
                log("🚨 Connection Refused error 🚨 ")
            except Warning as w:
                self._logger.warning(w)
                log(w)
            except Exception as e:
                self._logger.exception(e)
                log(e)
            finally:
                self._logger.debug("Finishing")
                log("🥺 Finishing 🥺")
                self.unsubscribeEvents(self.ib)
                self.vault.databaseModule.closeDatabaseConnection()
                await self.controller.terminateAsync()

                if self._runner:
                    await asyncio.sleep(self.retryDelay)