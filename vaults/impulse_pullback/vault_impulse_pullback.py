import asyncio
from datetime import datetime
from vaults.vault import Vault
from helpers.array_helper import Helpers
from models.base_models import Contract
from strategy.configs.impulse_pullback.models import StrategyImpulsePullbackConfig
from strategy.models import StrategyResult
from vaults.vaults_protocol import VaultsControllerProtocol
from portfolio.portfolio import Portfolio
from strategy.configs.models import StrategyAction, StrategyConfig
from typing import List, Union
from strategy.historical_data import HistoricalData
from strategy.impulse_pullback.strategy_impulse_pullback import StrategyImpulsePullback
from strategy.impulse_pullback.models import EventImpulsePullback, StrategyImpulsePullbackData
from helpers.logs import log, logCounter

class VaultImpulsePullback(Vault):
    historicalData: HistoricalData

    allContractsEvents: Union[str, List[EventImpulsePullback]]
    resultsToTrade: List[StrategyResult] = []

    def __init__(self, strategyConfig: StrategyConfig, portfolio: Portfolio, delegate: VaultsControllerProtocol) -> None:
        super().__init__(strategyConfig, portfolio, delegate)
        
        self.historicalData = HistoricalData()
        self.strategy = StrategyImpulsePullback()
        
    # Setup

    def setupVault(self):
        super().setupVault()
        log("🏃‍ Setup Impulse Pullback Vault 🏃‍")
        self.allContractsEvents = {}
        self.resultsToTrade = []

    # Reset

    def resetVault(self):
        log("🤖 Reset Impulse Pullback Vault 🤖")

    async def runNextOperationBlock(self, action: StrategyAction):
        if action == StrategyAction.runStrategy:
            await self.runMainStrategy()

    # Strategy

    async def runMainStrategy(self):
        log("🕐 Run Impulse pullback Strategy for %s market now 🕐" % self.strategyConfig.market.country.code)
        config: StrategyImpulsePullbackConfig = self.strategyConfig
        self.setupVault()

        await self.syncProviderData()
        await self.fetchHistoricalData()
        
        for contract in self.contracts:
            events = self.allContractsEvents[contract.symbol]
            if len(events) >= config.daysBefore:
                currentEvent = events[-1]
                previousEvents = [] 
                index = -2
                while index >= -config.daysBefore:
                    event = events[index]
                    previousEvents.insert(0, event)
                    index -= 1
                self.runStrategy(contract, previousEvents, currentEvent)
        log("🏁 Finished to run Stochastic Divergence Strategy 🏁")

    def runStrategy(self, contract: Contract,
                            previousEvents: List[EventImpulsePullback], currentEvent: EventImpulsePullback):
        data = StrategyImpulsePullbackData(contract=contract,
                                            totalCash= self.portfolio.getCashBalanceFor(self.strategyConfig.market),
                                            event=currentEvent,
                                            previousEvents=previousEvents)
        result = self.strategy.run(data, self.strategyConfig)
        #logExecutionZigZag(data, result)

    # Historical Data

    async def fetchHistoricalData(self):
        config: StrategyImpulsePullbackConfig = self.strategyConfig
        provider = self.delegate.controller.provider
        chunks = Helpers.grouper(self.contracts, 10)
        today = datetime.today()
        allEvents = []
        index = 1
        for contracts in chunks:
            allEvents += await asyncio.gather(*[provider.downloadHistoricalDataAsync(contract, config.daysBeforeToDownload, config.barSize, today) for contract in contracts ])
            logCounter("Download Contracts in Chunks", len(chunks), index)
            index += 1

        index = 1
        for contract, events in zip(self.contracts, allEvents):
            if contract.symbol not in self.allContractsEvents:
                self.allContractsEvents[contract.symbol] = []
                
            histData = HistoricalData.computeEventsForImpulsePullbackStrategy(events, self.strategyConfig)
            if len(histData) > 0:
                self.allContractsEvents[contract.symbol] = histData
                logCounter("🧶 Compute Historical Data 🧶", len(allEvents), index)
            else:
                log("🧶 ❗️ Invalid Historical Data for %s ❗️ 🧶" % (contract.symbol))
            index += 1 