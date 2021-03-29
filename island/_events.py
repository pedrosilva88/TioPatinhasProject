from datetime import *
from ib_insync import *
from portfolio import Portfolio
from .vaults import Vault
from helpers import log
import asyncio

class IslandEvents:
    def onUpdateEvent(self):
        None
        #self.vault.updatePortfolio()

    def onBarUpdate(self, bars, hasNewBar):
        self.vault.updateVolumeInFirstMinuteBar(bars, bars[-1].time)

    def onOpenOrderEvent(self, trade):
        self.vault.updatePortfolio()

    def onCancelOrderEvent(self, trade):
        self.vault.updatePortfolio()
      
    def onAccountSummaryEvent(self, accountValue: AccountValue):
        self.vault.updatePortfolio()

    def onPendingTickersEvent(self, tickers: [Ticker]):
        print("📈 Tickers Event 📈\n")
        for ticker in tickers:
            self.vault.executeTicker(ticker)
        print("\n📈               📈\n")

    def onError(self, reqId, errorCode, errorString, contract):
        log("🚨 onErrorEvent 🚨")
        if errorCode in {100, 1100} and not self.waiter.done():
            self.waiter.set_exception(Warning(f'Error {errorCode}'))
        else:
            log("🚨 %s 🚨" % errorString)
        self.vault.updatePortfolio()

    def onTimeout(self, idlePeriod):
        log("⏰ onTimeoutEvent ⏰")
        if not self.waiter.done():
            self.waiter.set_result(None)

    def onDisconnected(self):
        log("👋 onDisconnectEvent 👋 ")
        if not self.waiter.done():
            self.waiter.set_exception(Warning('Disconnected'))
        if self.marketWaiter is not None:
            self.marketWaiter.cancel()
            self.marketWaiter = None

    def subscribeEvents(self, ib: IB):
        self.subscribeSystemEvents(ib)
        self.subscribeStrategyEvents(ib)

    def unsubscribeEvents(self, ib: IB):
        self.unsubscribeSystemEvents(ib)
        self.unsubscribeStrategyEvents(ib)

    def subscribeSystemEvents(self, ib: IB):
        ib.timeoutEvent += self.onTimeout
        ib.disconnectedEvent += self.onDisconnected
        ib.errorEvent += self.onError
        ib.updateEvent += self.onUpdateEvent

    def subscribeStrategyEvents(self, ib: IB):
        ib.pendingTickersEvent += self.onPendingTickersEvent
        ib.accountSummaryEvent += self.onAccountSummaryEvent
        ib.openOrderEvent += self.onOpenOrderEvent
        ib.cancelOrderEvent += self.onCancelOrderEvent
        ib.barUpdateEvent += self.onBarUpdate

    def unsubscribeSystemEvents(self, ib: IB):
        ib.timeoutEvent -= self.onTimeout
        ib.disconnectedEvent -= self.onDisconnected
        ib.errorEvent -= self.onError
        ib.updateEvent -= self.onUpdateEvent
        
    def unsubscribeStrategyEvents(self, ib: IB):
        ib.pendingTickersEvent -= self.onPendingTickersEvent
        ib.accountSummaryEvent -= self.onAccountSummaryEvent
        ib.openOrderEvent -= self.onOpenOrderEvent
        ib.cancelOrderEvent -= self.onCancelOrderEvent 
        ib.barUpdateEvent -= self.onBarUpdate
