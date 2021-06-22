from island.island_protocol import IslandProtocol
from provider_factory.models import ProviderClient, ProviderEvents
from helpers import log

class IslandEvents(IslandProtocol):
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






    def onError(self, reqId, errorCode, errorString, contract):
        log("🚨 onErrorEvent 🚨")
        if errorCode in {100, 1100} and not self.waiter.done():
            self.waiter.set_exception(Warning(f'Error {errorCode}'))
        else:
            log("🚨 %s 🚨" % errorString)

    def onTimeout(self, idlePeriod):
        log("⏰ onTimeoutEvent ⏰")
        if not self.waiter.done():
            self.waiter.set_result(None)

    def onDisconnected(self):
        log("👋 onDisconnectEvent 👋 ")
        if not self.waiter.done():
            self.waiter.set_exception(Warning('Disconnected'))
        if self.vaultWaiter is not None:
            self.vaultWaiter.cancel()
            self.vaultWaiter = None

    def subscribeEvents(self, client: ProviderClient):
        client.subscribeEvent(ProviderEvents.didTimeOut, self.onTimeout)
        client.subscribeEvent(ProviderEvents.didDisconnect, self.onDisconnected)
        client.subscribeEvent(ProviderEvents.didGetError, self.onError)

    def unsubscribeEvents(self, client: ProviderClient):
        client.unsubscribeEvent(ProviderEvents.didTimeOut, self.onTimeout)
        client.unsubscribeEvent(ProviderEvents.didDisconnect, self.onDisconnected)
        client.unsubscribeEvent(ProviderEvents.didGetError, self.onError)