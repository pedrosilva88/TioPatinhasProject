from provider_factory.models import ProviderClient
from helpers import log

class IslandEvents:
    # def onUpdateEvent(self):
    #     None
    #     #self.vault.updatePortfolio()

    # def onBarUpdate(self, bars, hasNewBar):
    #     self.vault.updateVolumeInFirstMinuteBar(bars, bars[-1].time)

    # def onOpenOrderEvent(self, trade):
    #     self.vault.updatePortfolio()

    # def onCancelOrderEvent(self, trade):
    #     self.vault.updatePortfolio()
      
    # def onAccountSummaryEvent(self, accountValue: AccountValue):
    #     self.vault.updatePortfolio()

    # def onPendingTickersEvent(self, tickers: [Ticker]):
    #     print("📈 Tickers Event 📈\n")
    #     for ticker in tickers:
    #         self.vault.executeTicker(ticker)
    #     print("\n📈               📈\n")











    # def onError(self, reqId, errorCode, errorString, contract):
    #     log("🚨 onErrorEvent 🚨")
    #     if errorCode in {100, 1100} and not self.waiter.done():
    #         self.waiter.set_exception(Warning(f'Error {errorCode}'))
    #     else:
    #         log("🚨 %s 🚨" % errorString)
    #     self.vault.updatePortfolio()

    def onTimeout(self, idlePeriod):
        log("⏰ onTimeoutEvent ⏰")
        if not self.waiter.done():
            self.waiter.set_result(None)

    # def onDisconnected(self):
    #     log("👋 onDisconnectEvent 👋 ")
    #     if not self.waiter.done():
    #         self.waiter.set_exception(Warning('Disconnected'))
    #     if self.marketWaiter is not None:
    #         self.marketWaiter.cancel()
    #         self.marketWaiter = None

    def subscribeEvents(self, client: ProviderClient):
        client.subscribeOnTimeoutEvent(self.onTimeout)

    def unsubscribeEvents(self, client: ProviderClient):
        client.unsubscribeOnTimeoutEvent(self.onTimeout)