import asyncio
from enum import Enum
from models.base_models import Contract, Position
from strategy.zigzag.models import StrategyZigZagData
from models.zigzag.models import EventZigZag
from strategy.configs.models import StrategyAction
from typing import Protocol, Union
from itertools import zip_longest
from datetime import datetime
from vaults.models import Vault
from helpers import logExecutionZigZag, log, utcToLocal, logCounter
from models import Order, OrderAction, CustomBarData
from scanner import Scanner
from strategy import Strategy, StrategyZigZag, StrategyData, StrategyResult, StrategyResultType, HistoricalData, StrategyConfig, getStrategyConfigFor
from country_config import *
from portfolio import Portfolio
from earnings_calendar import EarningsCalendar
from database import DatabaseModule, FillDB

class VaultZigZag(Vault):
    databaseModule: DatabaseModule
    historicalData: HistoricalData

    allContractsEvents: Union[str, List[EventZigZag]]
    resultsToTrade: List[StrategyResult] = []
    currentFills: List[FillDB] = []

    def __init__(self, strategyConfig: StrategyConfig, portfolio: Portfolio) -> None:
        super().__init__(strategyConfig, portfolio)
        
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

    async def syncProviderData(self):
        log("📣 Sync Provider Data 📣")
        await self.ib.accountSummaryAsync()
        await self.ib.reqPositionsAsync()
        await self.ib.reqAllOpenOrdersAsync()

    async def runMainStrategy(self):
        log("🕐 Run ZigZag Strategy for %s market now 🕐" % self.countryConfig.key.code)
        self.setupVault()

        await self.syncProviderData()
        self.updatePortfolio()

        await self.fetchHistoricalData()
        
        for contract in self.contracts:
            events = self.allContractsEvents[contract.symbol]
            zigzagFound = False
            if len(events) >= 5:
                currentEvent = events[-1]
                previousEvents = [] 
                index = -2
                while index >= -5:
                    bar, zigzagFound = self.getEvent(events[index], zigzagFound)
                    previousEvents.insert(0, bar)
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
            if self.canCreateOrder(result.ticker.contract, result.order):
                if result.order.totalQuantity > 1:
                    self.createOrder(result.ticker.contract, result.order)
                    self.saveFill(result.ticker)
                    await self.syncProviderData()
                else:
                    log("❗️ (%s) Order Size is lower then 2 Shares❗️" % result.ticker.contract.symbol)
                    None

    def getEvent(self, event: EventZigZag, found: bool):
        if found:
            event.zigzag = False
        elif event.zigzag == True:
            found = True
        return (event, found)

    # Historical Data

    def grouper(self, iterable, n, fillvalue=None):
        args = [iter(iterable)] * n
        return list(zip_longest(*args, fillvalue=fillvalue))

    async def fetchHistoricalData(self):
        chunks = self.grouper(self.stocks, 50)
        all_bars = []
        for stocks in chunks:
            all_bars += await asyncio.gather(*[self.historicalData.downloadHistoricDataFromIB(self.ib, stock, 90, "1 day") for stock in stocks ])
        for stock, bars in zip(self.stocks, all_bars):
            if stock.symbol not in self.allContractsEvents:
                self.allContractsEvents[stock.symbol] = []
            histData = self.historicalData.createListOfCustomBarsData(bars)
            if len(histData) > 0:
                self.allContractsEvents[stock.symbol] = histData
                log("🧶 Historical Data for %s 🧶" % (stock.symbol))
            else:
                log("🧶 ❗️ Invalid Historical Data for %s ❗️ 🧶" % (stock.symbol))

    def getPercentageChange(self, current, previous):
        if current == previous:
            return 100.0
        try:
            return (abs(current - previous) / previous) * 100.0
        except ZeroDivisionError:
            return 0

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
        return self.portfolio.updatePortfolio(self.ib)

    def getPosition(self, contract: Contract):
        return self.portfolio.getPosition(contract)

    # Portfolio - Manage Orders

    def canCreateOrder(self, contract: ibContract, order: Order):
        return self.portfolio.canCreateOrder(self.ib, contract, order)

    def getOrder(self, ticker: ibTicker):
        mainOrder, profitOrder, stopLossOrder = self.portfolio.getTradeOrders(ticker.contract)

        if not mainOrder:
            return None

        profit = None
        stopLoss = None

        if profitOrder is not None:
            profit = Order(orderId=profitOrder.orderId, 
                            action=profitOrder.action, 
                            type=profitOrder.orderType,
                            totalQuantity=profitOrder.totalQuantity,
                            price=profitOrder.lmtPrice,
                            parentId=mainOrder.parentId)

        if stopLossOrder is not None:
            stopLoss = Order(orderId=stopLossOrder.orderId, 
                            action=stopLossOrder.action, 
                            type=stopLossOrder.orderType,
                            totalQuantity=stopLossOrder.totalQuantity,
                            price=stopLossOrder.auxPrice,
                            parentId=mainOrder.parentId)

        return Order(orderId=mainOrder.orderId, 
                        action=mainOrder.action, 
                        type=mainOrder.orderType,
                        totalQuantity=mainOrder.totalQuantity,
                        price=mainOrder.lmtPrice,
                        takeProfitOrder=profit,
                        stopLossOrder=stopLoss)

    def createOrder(self, contract: ibContract, order: Order):
        newOrder = order
        profitOrder = order.takeProfitOrder
        stopLossOrder = order.stopLossOrder
        return self.portfolio.createOrder(self.ib, contract, newOrder, profitOrder, stopLossOrder)

    def cancelOrder(self, contract: ibContract):
        return self.portfolio.cancelOrder(self.ib, contract)

    # Portfolio - Manage Positions

    def cancelPosition(self, orderAction: OrderAction, position: ibPosition):
        return self.portfolio.cancelPosition(self.ib, orderAction, position)