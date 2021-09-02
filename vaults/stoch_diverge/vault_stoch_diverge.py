import asyncio
from helpers.logs import logCounter
from strategy.stoch_diverge.strategy_stoch_diverge import StrategyStochDiverge
from strategy.configs.stoch_diverge.models import StrategyStochDivergeConfig
from typing import List, Union
from vaults.vault import Vault
from strategy.historical_data import HistoricalData
from strategy.stoch_diverge.models import StrategyStochDivergeData
from models.stoch_diverge.models import EventStochDiverge
from strategy.strategy import StrategyResult, StrategyResultType, StrategyConfig
from portfolio import Portfolio
from vaults.vaults_controller import VaultsControllerProtocol
from strategy.configs.models import StrategyAction
from helpers import log
from models.base_models import Contract
from helpers.array_helper import Helpers
from datetime import datetime

class VaultStochDiverge(Vault):
    historicalData: HistoricalData

    allContractsEvents: Union[str, List[EventStochDiverge]]
    resultsToTrade: List[StrategyResult] = []

    def __init__(self, strategyConfig: StrategyConfig, portfolio: Portfolio, delegate: VaultsControllerProtocol) -> None:
        super().__init__(strategyConfig, portfolio, delegate)
        
        self.historicalData = HistoricalData()
        self.strategy = StrategyStochDiverge()
        
    # Setup

    def setupVault(self):
        super().setupVault()
        log("🏃‍ Setup Stochastic Divergence Vault 🏃‍")
        self.allContractsEvents = {}
        self.resultsToTrade = []

    # Reset

    def resetVault(self):
        log("🤖 Reset Stochastic Divergence Vault 🤖")

    async def runNextOperationBlock(self, action: StrategyAction):
        if action == StrategyAction.runStrategy:
            await self.runMainStrategy()

    # Strategy

    async def runMainStrategy(self):
        log("🕐 Run Stochastic Divergence Strategy for %s market now 🕐" % self.strategyConfig.market.country.code)
        config: StrategyStochDivergeConfig = self.strategyConfig
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
                            previousEvents: List[EventStochDiverge], currentEvent: EventStochDiverge):
        data = StrategyStochDivergeData(contract=contract,
                                        totalCash= self.portfolio.getCashBalanceFor(self.strategyConfig.market),
                                        event=currentEvent,
                                        previousEvents=previousEvents)
        result = self.strategy.run(data, self.strategyConfig)
        #logExecutionZigZag(data, result)

    # Historical Data

    async def fetchHistoricalData(self):
        config: StrategyStochDivergeConfig = self.strategyConfig
        provider = self.delegate.controller.provider
        chunks = Helpers.grouper(self.contracts, 50)
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
                
            histData = HistoricalData.computeEventsForStochDivergeStrategy(events, self.strategyConfig)
            if len(histData) > 0:
                self.allContractsEvents[contract.symbol] = histData
                logCounter("🧶 Compute Historical Data 🧶", len(allEvents), index)
            else:
                log("🧶 ❗️ Invalid Historical Data for %s ❗️ 🧶" % (contract.symbol))
            index += 1 
