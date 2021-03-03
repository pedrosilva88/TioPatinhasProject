from ib_insync import *
from portfolio import Portfolio
from .vaults import Vault

class IslandEvents:
    def onOpenOrderEvent(self, trade):
        self.vault.portfolio.updatePortfolio(self.ib)

    def onAccountSummaryEvent(self, accountValue: AccountValue):
        self.vault.portfolio.updatePortfolio(self.ib)

    def onPendingTickersEvent(self, tickers: [Ticker]):
        for ticker in tickers:
            self.excuteTicker(ticker)

    def onError(self, reqId, errorCode, errorString, contract):
        if errorCode in {100, 1100} and not waiter.done():
            self.waiter.set_exception(Warning(f'Error {errorCode}'))
        else:
            self._logger.debug(errorString)

    def onTimeout(self, idlePeriod):
        if not self.waiter.done():
            self.waiter.set_result(None)

    def onDisconnected(self):
        if not self.waiter.done():
            self.waiter.set_exception(Warning('Disconnected'))

    def subscribeEvents(self, ib: IB):
        ib.timeoutEvent += self.onTimeout
        ib.disconnectedEvent += self.onDisconnected
        ib.errorEvent += self.onError
        ib.pendingTickersEvent += self.onPendingTickersEvent
        ib.accountSummaryEvent += self.onAccountSummaryEvent
        ib.openOrderEvent += self.onOpenOrderEvent

    def unsubscribeEvents(self, ib: IB):
        ib.timeoutEvent -= self.onTimeout
        ib.disconnectedEvent -= self.onDisconnected
        ib.errorEvent -= self.onError
        ib.pendingTickersEvent -= self.onPendingTickersEvent
        ib.accountSummaryEvent -= self.onAccountSummaryEvent
        ib.openOrderEvent -= self.onOpenOrderEvent


