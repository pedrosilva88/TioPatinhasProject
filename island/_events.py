from datetime import *
from ib_insync import *
from portfolio import Portfolio
from .vaults import Vault

class IslandEvents:
    def onUpdateEvent(self):
        None
        #self.vault.updatePortfolio()

    def onBarUpdate(self, bars, hasNewBar):
        print("🕯 %s: %s 🕯" % (bars.contract.symbol, bars[-1]))

    def onOpenOrderEvent(self, trade):
        self.vault.updatePortfolio()

    def onAccountSummaryEvent(self, accountValue: AccountValue):
        self.vault.updatePortfolio()

    def onPendingTickersEvent(self, tickers: [Ticker]):
        print("📈 Tickers Event 📈\n")
        for ticker in tickers:
            self.vault.executeTicker(ticker)
        print("\n📈               📈\n")

    def onError(self, reqId, errorCode, errorString, contract):
        print("🚨 onErrorEvent 🚨")
        if errorCode in {100, 1100} and not waiter.done():
            self.waiter.set_exception(Warning(f'Error {errorCode}'))
        else:
            self._logger.debug(errorString)

    def onTimeout(self, idlePeriod):
        print("⏰ onTimeoutEvent ⏰")
        if not self.waiter.done():
            self.waiter.set_result(None)

    def onDisconnected(self):
        print("👋 onDisconnectEvent 👋 ")
        if not self.waiter.done():
            self.waiter.set_exception(Warning('Disconnected'))

    def subscribeEvents(self, ib: IB):
        ib.timeoutEvent += self.onTimeout
        ib.disconnectedEvent += self.onDisconnected
        ib.errorEvent += self.onError
        ib.pendingTickersEvent += self.onPendingTickersEvent
        ib.accountSummaryEvent += self.onAccountSummaryEvent
        ib.openOrderEvent += self.onOpenOrderEvent
        ib.updateEvent += self.onUpdateEvent
        ib.barUpdateEvent += self.onBarUpdate

    def unsubscribeEvents(self, ib: IB):
        ib.timeoutEvent -= self.onTimeout
        ib.disconnectedEvent -= self.onDisconnected
        ib.errorEvent -= self.onError
        ib.pendingTickersEvent -= self.onPendingTickersEvent
        ib.accountSummaryEvent -= self.onAccountSummaryEvent
        ib.openOrderEvent -= self.onOpenOrderEvent
        ib.updateEvent -= self.onUpdateEvent
        ib.barUpdateEvent -= self.onBarUpdate