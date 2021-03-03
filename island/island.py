import asyncio
import logging
from enum import Enum
from datetime import *
from ib_insync import *
from .vaults import Vault
from ._events import *
from portfolio import Portfolio
from strategy import StrategyData, StrategyResult, StrategyResultType

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
        self._runner = asyncio.ensure_future(self.runAsync())
        self.ib.run()

    def stop(self):
        self._logger.info('Stopping')
        self.ib.disconnect()
        self._runner = None

    def excuteTicker(self, ticker: Ticker):
        position = self.vault.portfolio.getPosition(ticker)
        order = self.vault.portfolio.getOrder(ticker)
        data = StrategyData(ticker.contract.symbol, ticker.time, ticker.close, ticker.open, ticker.last, position, order, self.vault.portfolio.cashBalance)
        result = self.vault.strategy.run(data)
        self.handleStrategyResult(result)

    def handleStrategyResult(self, result: StrategyResult):
        if (result.type == StrategyResultType.Buy or result.type == StrategyResultType.Sell):
            return self.vault.portfolio.createOrder(self.ib, result.order) # Acabar esta function
        elif (result.type == StrategyResultType.StrategyDateWindowExpired or result.type == StrategyResultType.DoNothing):
            return self.unsubscribeTicker(result.ticker) # Validar esta function com real market data
        elif (result.type == StrategyResultType.PositionExpired_Buy or result.type == StrategyResultType.PositionExpired_Sell):
            return self.vault.portfolio.cancelPosition() # Tratar desta function
        elif result.type == StrategyResultType.KeepOrder:
            return self.vault.portfolio.updateOrder() # Tratar desta function
        elif result.type == StrategyResultType.StrategyDateWindowExpiredCancelOrder:
            return self.vault.portfolio.cancelOrder() # Tratar desta function
        return

    def unsubscribeTicker(self, ticker):
        stock = Stock(ticker, "SMART", "USD")
        self.ib.cancelMktData(stock)
    
    async def runAsync(self):
        while self._runner:
            try:
                await asyncio.sleep(self.appStartupTime)
                await self.ib.connectAsync(self.host, self.port, self.clientId, self.connectTimeout,
                    self.readonly, self.account)
                await self.ib.reqAllOpenOrdersAsync()
                await self.ib.reqCurrentTimeAsync()

                self.vault.portfolio.updatePortfolio(self.ib)
                ## This need to be removed
                self.ib.reqMarketDataType(3)
                ##

                self.ib.setTimeout(self.appTimeout)
                self.subscribeEvents(self.ib)

                while self._runner:
                    self.waiter = asyncio.Future()
                    await self.waiter
                    self._logger.debug('Soft timeout')
                    contracts = [Stock(symbol, 'SMART', 'USD') for symbol in self.vault.scanner.tickers]
                    for contract in contracts:
                        self.ib.reqMktData(contract)

            except ConnectionRefusedError:
                print("Connection Refused error")
            except Warning as w:
                self._logger.warning(w)
            except Exception as e:
                self._logger.exception(e)
            finally:
                self._logger.debug("Finishing")
                self.unsubscribeEvents(self.ib)

                if self._runner:
                    await asyncio.sleep(self.retryDelay)