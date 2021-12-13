import asyncio
from datetime import datetime
from strategy.configs.stoch_diverge.models import StrategyStochDivergeConfig
from vaults.vault import Vault
from helpers.array_helper import Helpers
from models.base_models import Contract, Event
from strategy.configs.impulse_pullback.models import StrategyImpulsePullbackConfig
from strategy.configs.bounce.models import StrategyBounceConfig
from strategy.configs.combined.models import StrategyCombinedConfig
from strategy.models import StrategyResult, StrategyResultType
from vaults.vaults_protocol import VaultsControllerProtocol
from portfolio.portfolio import Portfolio
from strategy.configs.models import StrategyAction, StrategyConfig
from typing import List, Union
from strategy.historical_data import HistoricalData
from strategy.impulse_pullback.strategy_impulse_pullback import StrategyImpulsePullback
from strategy.impulse_pullback.models import EventImpulsePullback, StrategyImpulsePullbackData, StrategyImpulsePullbackResult
from strategy.bounce.strategy_bounce import StrategyBounce
from strategy.bounce.models import EventBounce, StrategyBounceData, StrategyBounceResult
from strategy.zigzag.strategy_zigzag import StrategyZigZag
from strategy.zigzag.models import EventZigZag, StrategyZigZagData, StrategyZigZagResult
from strategy.stoch_diverge.strategy_stoch_diverge import StrategyStochDiverge
from strategy.stoch_diverge.models import EventStochDiverge, StrategyStochDivergeData, StrategyResult, StrategyStochDivergeResult
from helpers.logs import log, logCounter, logImpulsePullbackReport, logBounceReport, createLogReports, logStochDivergeReport, logZigZagReport

class VaultCombined(Vault):
    historicalData: HistoricalData

    allContractsEventsImpulsePullback: Union[str, List[EventImpulsePullback]]
    allContractsEventsBounce: Union[str, List[EventBounce]]
    allContractsEventsZigZag: Union[str, List[EventZigZag]]
    allContractsEventsStochDiverge: Union[str, List[EventStochDiverge]]

    strategyImpulsePullback: StrategyImpulsePullback = StrategyImpulsePullback()
    strategyBounce: StrategyBounce = StrategyBounce()
    strategyZigZag: StrategyZigZag = StrategyZigZag()
    strategyStochDiverge: StrategyStochDiverge = StrategyStochDiverge()

    def __init__(self, strategyConfig: StrategyConfig, portfolio: Portfolio, delegate: VaultsControllerProtocol) -> None:
        super().__init__(strategyConfig, portfolio, delegate)
        
        self.historicalData = HistoricalData()
        self.strategy = None

        config: StrategyCombinedConfig = strategyConfig
        createLogReports(config.impulsePullbackConfig.type.value)
        createLogReports(config.bounceConfig.type.value)
        createLogReports(config.zigzagConfig.type.value)
        createLogReports(config.stochDivergeConfig.type.value)
        
    # Setup

    def setupVault(self):
        super().setupVault()
        log("🏃‍ Setup Combined Vault 🏃‍")
        self.allContractsEventsImpulsePullback = dict()
        self.allContractsEventsBounce = dict()
        self.allContractsEventsZigZag = dict()
        self.allContractsEventsStochDiverge = dict()

    # Reset

    def resetVault(self):
        log("🤖 Reset Combined Vault 🤖")
        self.allContractsEventsImpulsePullback = dict()
        self.allContractsEventsBounce = dict()
        self.allContractsEventsZigZag = dict()
        self.allContractsEventsStochDiverge = dict()

    async def runNextOperationBlock(self, action: StrategyAction):
        if action == StrategyAction.runStrategy:
            await self.runMainStrategy()

    # Strategy

    async def runMainStrategy(self):
        log("🕐 Run Impulse pullback Strategy for %s market now 🕐" % self.strategyConfig.market.country.code)
        config: StrategyCombinedConfig = self.strategyConfig
        self.setupVault()

        await self.syncProviderData()
        self.updatePortfolio()
        allEvents = await self.fetchHistoricalData()
        
        self.computeForImpulsePullback(allEvents)
        self.computeForBounce(allEvents)
        self.computeForZigZag(allEvents)
        self.computeForStochDiverge(allEvents)
        for contract in self.contracts:
            events = self.allContractsEventsImpulsePullback[contract.symbol]
            if len(events) >= config.impulsePullbackConfig.daysBefore:
                currentEvent = events[-1]
                previousEvents = [] 
                index = -2
                while index >= -config.impulsePullbackConfig.daysBefore:
                    event = events[index]
                    previousEvents.insert(0, event)
                    index -= 1
                self.runStrategyForImpulsePullback(contract, previousEvents, currentEvent)

            events = self.allContractsEventsBounce[contract.symbol]
            if len(events) >= config.bounceConfig.daysBefore:
                currentEvent = events[-1]
                previousEvents = [] 
                index = -2
                while index >= -config.bounceConfig.daysBefore:
                    event = events[index]
                    previousEvents.insert(0, event)
                    index -= 1
                self.runStrategyForBounce(contract, previousEvents, currentEvent)

            events = self.allContractsEventsZigZag[contract.symbol]
            if len(events) >= config.zigzagConfig.daysBefore:
                currentEvent = events[-1]
                previousEvents = [] 
                index = -2
                while index >= -config.zigzagConfig.daysBefore:
                    event = events[index]
                    previousEvents.insert(0, event)
                    index -= 1
                self.runStrategyForZigzag(contract, previousEvents, currentEvent)

            events = self.allContractsEventsStochDiverge[contract.symbol]
            if len(events) >= config.stochDivergeConfig.daysBefore:
                currentEvent = events[-1]
                previousEvents = [] 
                index = -2
                while index >= -config.stochDivergeConfig.daysBefore:
                    event = events[index]
                    previousEvents.insert(0, event)
                    index -= 1
                self.runStrategyForStochDiverge(contract, previousEvents, currentEvent)
        log("🏁 Finished to run Combined Strategy 🏁")

    def runStrategyForImpulsePullback(self, contract: Contract,
                                        previousEvents: List[EventImpulsePullback], currentEvent: EventImpulsePullback):
        config: StrategyCombinedConfig = self.strategyConfig
        data = StrategyImpulsePullbackData(contract=contract,
                                            totalCash= self.portfolio.getCashBalanceFor(self.strategyConfig.market),
                                            event=currentEvent,
                                            previousEvents=previousEvents)
        result: StrategyImpulsePullbackResult = self.strategyImpulsePullback.run(data, config.impulsePullbackConfig)
        if result.type == StrategyResultType.Buy or result.type == StrategyResultType.Sell:
            logResult = ("\t\t 🤴   %s   🤴\nSwing(%s)\t Pullback(%s)\n 📣Action(%s)\n💰 Price(%.2f) \t\tSize(%d)\n\t\tTP(%.2f)\n\t\tSL(%.2f)\n\n \t\t\t🥽🥽🥽🥽🥽🥽🥽 \n\n" % 
                        (result.contract.symbol, result.swingCandle.datetime.date(), 
                        result.pullbackCandle.datetime.date(), result.bracketOrder.parentOrder.action.code, 
                        result.bracketOrder.parentOrder.price, result.bracketOrder.parentOrder.size, 
                        result.bracketOrder.takeProfitOrder.price, result.bracketOrder.stopLossOrder.price))
            logImpulsePullbackReport(config.impulsePullbackConfig.type.value, logResult)

    def runStrategyForBounce(self, contract: Contract,
                                    previousEvents: List[EventBounce], currentEvent: EventBounce):
        config: StrategyCombinedConfig = self.strategyConfig
        data = StrategyBounceData(contract=contract,
                                            totalCash= self.portfolio.getCashBalanceFor(self.strategyConfig.market),
                                            event=currentEvent,
                                            previousEvents=previousEvents)
        result: StrategyBounceResult = self.strategyBounce.run(data, config.bounceConfig)
        if result.type == StrategyResultType.Buy or result.type == StrategyResultType.Sell:
            logResult = ("\t\t 🤴   %s   🤴\nConfirmationBar(%s)\t ReversalBar(%s)\t EMA(%s) \t Type(%s)\n 📣Action(%s)\n💰 Price(%.2f) \t\tSize(%d)\n\t\tTP(%.2f)\n\t\tSL(%.2f)\n\n \t\t\t🥽🥽🥽🥽🥽🥽🥽 \n\n" % 
                        (result.contract.symbol, result.confirmationCandle.datetime.date(), 
                        result.reversalCandle.datetime.date(), result.ema, result.reversalCandleType.code, 
                        result.bracketOrder.parentOrder.action.code, 
                        result.bracketOrder.parentOrder.price, result.bracketOrder.parentOrder.size, 
                        result.bracketOrder.takeProfitOrder.price, result.bracketOrder.stopLossOrder.price))
            logBounceReport(config.bounceConfig.type.value, logResult)

    def runStrategyForZigzag(self, contract: Contract,
                                    previousEvents: List[EventBounce], currentEvent: EventBounce):
        config: StrategyCombinedConfig = self.strategyConfig
        data = StrategyZigZagData(contract=contract,
                                            totalCash= self.portfolio.getCashBalanceFor(self.strategyConfig.market),
                                            event=currentEvent,
                                            previousEvents=previousEvents)
        result: StrategyZigZagResult = self.strategyZigZag.run(data, config.zigzagConfig)
        if result.type == StrategyResultType.Buy or result.type == StrategyResultType.Sell:
            logResult = ("\t\t 🤴   %s   🤴\n 📣Action(%s)\n💰 Price(%.2f) \t\tSize(%d)\n\t\tTP(%.2f)\n\t\tSL(%.2f)\n\n \t\t\t🥽🥽🥽🥽🥽🥽🥽 \n\n" % 
                        (result.contract.symbol, 
                        result.bracketOrder.parentOrder.action.code, 
                        result.bracketOrder.parentOrder.price, result.bracketOrder.parentOrder.size, 
                        result.bracketOrder.takeProfitOrder.price, result.bracketOrder.stopLossOrder.price))
            logZigZagReport(config.zigzagConfig.type.value, logResult)

    
    def runStrategyForStochDiverge(self, contract: Contract,
                                    previousEvents: List[EventBounce], currentEvent: EventBounce):
        config: StrategyCombinedConfig = self.strategyConfig
        data = StrategyStochDivergeData(contract=contract,
                                            totalCash= self.portfolio.getCashBalanceFor(self.strategyConfig.market),
                                            event=currentEvent,
                                            previousEvents=previousEvents)
        result: StrategyStochDivergeResult = self.strategyStochDiverge.run(data, config.stochDivergeConfig)
        if result.type == StrategyResultType.Buy or result.type == StrategyResultType.Sell:
            logResult = ("\t\t 🤴   %s   🤴\n\n \t\t\t🥽🥽🥽🥽🥽🥽🥽 \n\n" % 
                        (result.contract.symbol, 
                        result.bracketOrder.parentOrder.action.code, 
                        result.bracketOrder.parentOrder.price, result.bracketOrder.parentOrder.size, 
                        result.bracketOrder.takeProfitOrder.price, result.bracketOrder.stopLossOrder.price))
            logStochDivergeReport(config.zigzagConfig.type.value, logResult)

    # Historical Data

    async def fetchHistoricalData(self) -> List[List[Event]]:
        config: StrategyCombinedConfig = self.strategyConfig
        provider = self.delegate.controller.provider
        chunks = Helpers.grouper(self.contracts, 50)
        today = datetime.today()
        allEvents = []
        index = 1
        for contracts in chunks:
            allEvents += await asyncio.gather(*[provider.downloadHistoricalDataAsync(contract, config.daysBeforeToDownload, config.barSize, today) for contract in contracts ])
            logCounter("Download Contracts in Chunks", len(chunks), index)
            index += 1
        
        return allEvents
    
    def computeForImpulsePullback(self, allEvents: List[List[Event]]):
        index = 1
        config: StrategyCombinedConfig = self.strategyConfig
        for contract, events in zip(self.contracts, allEvents):
            if contract is None:
                break

            if contract.symbol not in self.allContractsEventsImpulsePullback:
                self.allContractsEventsImpulsePullback[contract.symbol] = []
                
            histData = HistoricalData.computeEventsForImpulsePullbackStrategy(events, config.impulsePullbackConfig)
            if len(histData) > 0:
                self.allContractsEventsImpulsePullback[contract.symbol] = histData
                logCounter("🧶 Compute Historical Data For Impulse Pullback 🧶", len(allEvents), index)
            else:
                log("🧶 ❗️ Invalid Historical Data for %s ❗️ 🧶" % (contract.symbol))
            index += 1

    def computeForBounce(self, allEvents: List[Event]):
        index = 1
        config: StrategyCombinedConfig = self.strategyConfig
        for contract, events in zip(self.contracts, allEvents):
            if contract is None:
                break

            if contract.symbol not in self.allContractsEventsBounce:
                self.allContractsEventsBounce[contract.symbol] = []
                
            histData = HistoricalData.computeEventsForBounceStrategy(events, config.bounceConfig)
            if len(histData) > 0:
                self.allContractsEventsBounce[contract.symbol] = histData
                logCounter("🧶 Compute Historical Data For Bounce 🧶", len(allEvents), index)
            else:
                log("🧶 ❗️ Invalid Historical Data for %s ❗️ 🧶" % (contract.symbol))
            index += 1

    def computeForZigZag(self, allEvents: List[Event]):
        index = 1
        config: StrategyCombinedConfig = self.strategyConfig
        for contract, events in zip(self.contracts, allEvents):
            if contract.symbol not in self.allContractsEventsZigZag:
                self.allContractsEventsZigZag[contract.symbol] = []
                
            histData = HistoricalData.computeEventsForZigZagStrategy(events, config.zigzagConfig)
            if len(histData) > 0:
                self.allContractsEventsZigZag[contract.symbol] = histData
                logCounter("🧶 Compute Historical Data For Zigzag 🧶", len(allEvents), index)
            else:
                log("🧶 ❗️ Invalid Historical Data for %s ❗️ 🧶" % (contract.symbol))
            index += 1

    def computeForStochDiverge(self, allEvents: List[Event]):
        index = 1
        config: StrategyCombinedConfig = self.strategyConfig
        for contract, events in zip(self.contracts, allEvents):
            if contract.symbol not in self.allContractsEventsStochDiverge:
                self.allContractsEventsStochDiverge[contract.symbol] = []
                
            histData = HistoricalData.computeEventsForStochDivergeStrategy(events, config.stochDivergeConfig)
            if len(histData) > 0:
                self.allContractsEventsStochDiverge[contract.symbol] = histData
                logCounter("🧶 Compute Historical Data For Stoch Diverge 🧶", len(allEvents), index)
            else:
                log("🧶 ❗️ Invalid Historical Data for %s ❗️ 🧶" % (contract.symbol))
            index += 1

    # Portfolio

    def updatePortfolio(self):
        return self.portfolio.updatePortfolio(self.delegate.controller.provider, self.strategyConfig.market)
