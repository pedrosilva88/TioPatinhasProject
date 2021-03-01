import asyncio
import logging
from enum import Enum
from datetime import *
from ib_insync import *
from . import Vault
from portfolio import Portfolio

class Island:
    ib: IB
    host: str = '127.0.0.1'
    port: int = 7497
    clientId: int = 1
    connectTimeout: float = 2
    appStartupTime: float = 5
    appTimeout: float = 5
    retryDelay: float = 1
    readonly: bool = False
    account: str = ''

    vault: Vault

    def __init__(self):
        self.ib = IB()
        self.vault = None
        self._runner = None
        self._logger = logging.getLogger('TioPatinhas.Island')

    def __post_init__(self):
        if not self.ib:
            raise ValueError('No IB instance supplied')
        if self.ib.isConnected():
            raise ValueError('IB instance must not be connected')

    def start(self, vault: Vault):
        self._logger.info('Starting')
        self.vault = vault
        self._runner = asyncio.ensure_future(self.runAsync())
        self.ib.run()

    def stop(self):
        self._logger.info('Stopping')
        self.ib.disconnect()
        self._runner = None

    async def runAsync(self):
        def onOpenOrderEvent(trade):
            print(trade)
            self.vault.portfolio.updatePortfolio(self.ib)

        def onAccountSummaryEvent(accountValue: AccountValue):
            self.vault.portfolio.updatePortfolio(self.ib)

        def onUpdateEvent():
            self.vault.portfolio.updatePortfolio(self.ib)
            if not waiter.done():
                waiter.set_result(None)

        def onPendingTickersEvent(tickers):
            for ticker in tickers:
                data = self.buildStrategyData(ticker)
                self.vault.strategy.run(data)
                print(ticker)
    
        def onError(reqId, errorCode, errorString, contract):
            if errorCode in {100, 1100} and not waiter.done():
                waiter.set_exception(Warning(f'Error {errorCode}'))
            else:
                self._logger.debug(contract.symbol)

        def onTimeout(idlePeriod):
            if not waiter.done():
                waiter.set_result(None)

        def onDisconnected():
            if not waiter.done():
                waiter.set_exception(Warning('Disconnected'))

        while self._runner:
            try:
                await asyncio.sleep(self.appStartupTime)
                await self.ib.connectAsync(self.host, self.port, self.clientId, self.connectTimeout,
                    self.readonly, self.account)

                self.ib.setTimeout(self.appTimeout)
                self.ib.timeoutEvent += onTimeout
                self.ib.disconnectedEvent += onDisconnected
                self.ib.errorEvent += onError
                self.ib.pendingTickersEvent += onPendingTickersEvent
                self.ib.updateEvent += onUpdateEvent 
                self.ib.accountSummaryEvent += onAccountSummaryEvent
                self.ib.openOrderEvent += onOpenOrderEvent

                while self._runner:
                    waiter = asyncio.Future()
                    await waiter
                    self._logger.debug('Soft timeout')
                    self.vault.portfolio.updatePortfolio(self.ib)
                    contracts = [Stock(symbol, 'SMART', 'USD') for symbol in self.vault.scanner.tickers]
                    # for contract in contracts:
                    #     self.ib.reqMktData(contract)

            except ConnectionRefusedError:
                print("Connection Refused error")
            except Warning as w:
                self._logger.warning(w)
            except Exception as e:
                self._logger.exception(e)
            finally:
                self._logger.debug("Finishing")
                print("Finishing")
                self.ib.timeoutEvent -= onTimeout
                self.ib.disconnectedEvent -= onDisconnected
                self.ib.errorEvent -= onError
                self.ib.pendingTickersEvent -= onPendingTickersEvent
                self.ib.updateEvent -= onUpdateEvent
                self.ib.accountSummaryEvent -= onAccountSummaryEvent

                if self._runner:
                    await asyncio.sleep(self.retryDelay)

