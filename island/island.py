import asyncio
import logging
from enum import Enum
from datetime import datetime
from ib_insync import IB
from .vaults import Vault
from ._events import *

class Island(IslandEvents):
    ib: IB
    host: str = '127.0.0.1'
    port: int = 7497
    clientId: int = 1
    connectTimeout: float = 5
    appStartupTime: float = 5
    appTimeout: float = 10
    retryDelay: float = 5
    readonly: bool = False
    account: str = ''

    vault: Vault

    def __init__(self):
        self.ib = IB()
        self.vault = None
        self._runner = None
        self.waiter = None
        self._logger = logging.getLogger('TioPatinhas.Island')

    def __post_init__(self):
        if not self.ib:
            raise ValueError('No IB instance supplied')
        if self.ib.isConnected():
            raise ValueError('IB instance must not be connected')

    def start(self, vault: Vault):
        self._logger.info('Starting')
        self.vault = vault
        self.vault.ib = self.ib
        self._runner = asyncio.ensure_future(self.runAsync())
        self.ib.run()

    def stop(self):
        self._logger.info('Stopping')
        self.ib.disconnect()
        self._runner = None
    
    async def runAsync(self):
        while self._runner:
            try:
                await asyncio.sleep(self.appStartupTime)
                await self.ib.connectAsync(self.host, self.port, self.clientId, self.connectTimeout,
                    self.readonly, self.account)
                await self.ib.accountSummaryAsync()
                await self.ib.reqPositionsAsync()
                await self.ib.reqAllOpenOrdersAsync()

                self.vault.updatePortfolio()
                self.ib.setTimeout(self.appTimeout)
                self.subscribeEvents(self.ib)

                while self._runner:
                    self.waiter = asyncio.Future()
                    await self.waiter
                    self._logger.debug('Soft timeout')
                    self.vault.subscribeTickers()

            except ConnectionRefusedError:
                print("🚨 Connection Refused error 🚨 ")
            except Warning as w:
                self._logger.warning(w)
            except Exception as e:
                self._logger.exception(e)
            finally:
                self._logger.debug("Finishing")
                self.unsubscribeEvents(self.ib)

                if self._runner:
                    await asyncio.sleep(self.retryDelay)