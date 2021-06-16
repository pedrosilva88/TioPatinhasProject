import asyncio
from strategy.configs.zigzag.models import StrategyZigZagConfig
from helpers.array_helper import Helpers
from vaults.vaults_controller import VaultsControllerProtocol
from models.base_models import BracketOrder, Contract, Position
from strategy.zigzag.models import StrategyZigZagData
from models.zigzag.models import EventZigZag
from strategy.configs.models import StrategyAction
from typing import List, Union
from datetime import date, datetime, timedelta
from vaults.vault import Vault
from helpers import logExecutionZigZag, log
from models import Order, OrderAction
from strategy import StrategyZigZag, StrategyResult, StrategyResultType, HistoricalData, StrategyConfig
from portfolio import Portfolio
from database import DatabaseModule, FillDB

class VaultZigZag(Vault):
    databaseModule: DatabaseModule
    historicalData: HistoricalData

    allContractsEvents: Union[str, List[EventZigZag]]
    resultsToTrade: List[StrategyResult] = []
    currentFills: List[FillDB] = []

    def __init__(self, strategyConfig: StrategyConfig, portfolio: Portfolio, delegate: VaultsControllerProtocol) -> None:
        super().__init__(strategyConfig, portfolio, delegate)
        
        self.databaseModule = DatabaseModule()
        self.historicalData = HistoricalData()
        self.strategy = StrategyZigZag()
        
    # Setup

    def setupVault(self):
        super().setupVault()
        log("🏃‍ Setup ZigZag Vault 🏃‍")
        self.allContractsEvents = {}
        self.resultsToTrade = []
        self.databaseModule.openDatabaseConnection()
        self.clearOldFills()
        self.currentFills = self.databaseModule.getFills()

    # Reset

    def resetVault(self):
        log("🤖 Reset ZigZag Vault 🤖")
        self.databaseModule.closeDatabaseConnection()

    async def runNextOperationBlock(self, now: datetime):
        action = self.strategyConfig.nextAction(now)
        if action == StrategyAction.runStrategy:
            await self.runMainStrategy()

        elif action == StrategyAction.checkPositions:
            await self.runStrategyToClosePositions()

    # Strategy

    async def runMainStrategy(self):
        log("🕐 Run ZigZag Strategy for %s market now 🕐" % self.countryConfig.key.code)
        self.setupVault()

        await self.syncProviderData()
        self.updatePortfolio()

        await self.fetchHistoricalData()
        
        for contract in self.contracts:
            events = self.allContractsEvents[contract.symbol]
            if len(events) >= 5:
                currentEvent = events[-1]
                previousEvents = [] 
                index = -2
                while index >= -5:
                    event = events[index]
                    previousEvents.insert(0, event)
                    index -= 1
                position = self.getPosition(contract)
                fill = self.getFill(contract)
                self.runStrategy(contract, position, previousEvents, currentEvent, fill)

        await self.handleResultsToTrade()

    async def runStrategyToClosePositions(self):
        log("⭐️ Checking Positions ⭐️")

        await self.syncProviderData()
        self.updatePortfolio()
            
        fills = self.currentFills
        for fill in fills:
            contract = Contract(fill.symbol, self.strategyConfig.market.country)
            position = self.getPosition(contract)
            if (position is not None):
                log("⭐️ Checking Position for (%s) ⭐️" % contract.symbol)
                self.runStrategy(contract, position, None, None, fill)        
        self.resetVault()

    def runStrategy(self, contract: Contract, position: Position,
                            previousEvents: List[EventZigZag], currentEvent: EventZigZag,
                            fill: FillDB):
        data = StrategyZigZagData(contract=contract,
                                    totalCash= self.portfolio.totalCashBalance,
                                    event=currentEvent,
                                    previousEvents=previousEvents,
                                    position=position,
                                    fill=fill)
        result = self.strategy.run(data, self.strategyConfig)
        logExecutionZigZag(data, result)
        self.handleStrategyResult(result, contract)

    # Strategy Handle Results

    def handleStrategyResult(self, result: StrategyResult, contract: Contract):
        if (result.type == StrategyResultType.Buy or result.type == StrategyResultType.Sell):
            self.resultsToTrade.append(result)

        elif (result.type == StrategyResultType.PositionExpired_Buy or result.type == StrategyResultType.PositionExpired_Sell):
            orderAction = OrderAction.Buy.value if result.type == StrategyResultType.PositionExpired_Buy else OrderAction.Sell.value
            return self.cancelPosition(orderAction, result.position)
        else:
            log("🤨 %s " % result)

        return

    async def handleResultsToTrade(self):
        self.resultsToTrade.sort(key=lambda x: x.priority, reverse=True)
        for result in self.resultsToTrade:
            if self.canCreateOrder(result.ticker.contract, result.bracketOrder):
                if result.order.totalQuantity > 1:

                    self.createOrder(result.ticker.contract, result.bracketOrder)
                    self.saveFill(result.ticker)
                    await self.syncProviderData()
                    self.updatePortfolio()

                else:
                    log("❗️ (%s) Order Size is lower then 2 Shares❗️" % result.ticker.contract.symbol)
                    None

    # Historical Data

    async def fetchHistoricalData(self):
        config: StrategyZigZagConfig = self.strategyConfig
        provider = self.delegate.controller.provider
        chunks = Helpers.grouper(self.contracts, 50)
        allEvents = []

        for contracts in chunks:
            allEvents += await asyncio.gather(*[provider.downloadHistoricalDataAsync(contract, config.daysBeforeToDownload, config.barSize) for contract in contracts ])

        for contract, events in zip(self.contracts, allEvents):
            if contract.symbol not in self.allContractsEvents:
                self.allContractsEvents[contract.symbol] = []
                
            histData = HistoricalData.computeEventsForZigZagStrategy(events)
            if len(histData) > 0:
                self.allContractsEvents[contract.symbol] = histData
                log("🧶 Historical Data for %s 🧶" % (contract.symbol))
            else:
                log("🧶 ❗️ Invalid Historical Data for %s ❗️ 🧶" % (contract.symbol))

    # Database

    def getFill(self, contract: Contract):
        fills = self.currentFills
        filteredFills = list(filter(lambda x: contract.symbol == x.symbol, fills))
        filteredFills.sort(key=lambda x: x.date, reverse=True)
        if len(filteredFills) > 0:
            log("🧶 Fill Found %s - %s 🧶" % (filteredFills[0].symbol, filteredFills[0].date))
            return filteredFills[0]
        return None

    def saveFill(self, contract: Contract):
        fill = FillDB(contract.symbol, date.today())
        self.databaseModule.createFill(fill)
        self.currentFills = self.databaseModule.getFills()

    def clearOldFills(self):
        fills = self.databaseModule.getFills()
        limitDate = date.today()-timedelta(days=40)
        filteredFills = list(filter(lambda x: x.date < limitDate, fills))
        self.databaseModule.deleteFills(filteredFills)

    # Portfolio

    def updatePortfolio(self):
        return self.portfolio.updatePortfolio()

    def getPosition(self, contract: Contract):
        return self.portfolio.getPosition(contract)

    # Portfolio - Manage Orders

    def canCreateOrder(self, contract: Contract, bracketOrder: BracketOrder):
        return self.portfolio.canCreateOrder(self.delegate.controller.provider, contract, bracketOrder)

    def createOrder(self, contract: Contract, bracketOrder: BracketOrder):
        return self.portfolio.createOrder(self.delegate.controller.provider, contract, bracketOrder)

    def cancelOrder(self, contract: Contract):
        return self.portfolio.cancelOrder(self.delegate.controller.provider, contract)

    # Portfolio - Manage Positions

    def cancelPosition(self, orderAction: OrderAction, position: Position):
        return self.portfolio.cancelPosition(self.delegate.controller.provider, orderAction, position)