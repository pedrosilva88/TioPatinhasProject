import asyncio
from enum import Enum
from typing import Protocol
from itertools import zip_longest
from datetime import datetime
from ib_insync import IB, Ticker as ibTicker, Contract as ibContract, Order as ibOrder, LimitOrder, StopOrder, Position as ibPosition, BarData, Stock as ibStock
from helpers import logExecutionZigZag, log, utcToLocal, logCounter
from models import Order, OrderAction, CustomBarData
from scanner import Scanner
from strategy import Strategy, StrategyZigZag, StrategyData, StrategyResult, StrategyResultType, HistoricalData, StrategyConfig, getStrategyConfigFor
from country_config import *
from portfolio import Portfolio
from earnings_calendar import EarningsCalendar
from database import DatabaseModule, FillDB

class IslandProtocol(Protocol):
    marketWaiter: asyncio.Future

    def subscribeStrategyEvents(self, ib: IB):
        """Subscribe Events"""

    def unsubscribeStrategyEvents(self, ib: IB):
        """Subscribe Events"""

class VaultZigZag:
    ib: IB
    databaseModule: DatabaseModule
    countryConfig: CountryConfig
    strategyConfig: StrategyConfig
    scanner: Scanner
    strategy: Strategy
    portfolio: Portfolio
    historicalData: HistoricalData
    customBarsDataDict: [str, [CustomBarData]]

    resultsToTrade: [StrategyResult] = []
    currentFills: [FillDB] = []

    delegate: IslandProtocol

    def __init__(self, delegate: IslandProtocol):
        self.databaseModule = DatabaseModule()
        self.historicalData = HistoricalData()
        self.delegate = delegate

        self.setupVault()
        
    # Setup

    def setupVault(self):
        self.countryConfig = getCurrentMarketConfig()
        log("🏃‍ Setup ZigZag Vault for %s 🏃‍"% self.countryConfig.key.code)
        key = self.countryConfig.key
        path = ("scanner/Data/CSV/%s/ZigZag/ZigZagScan.csv" % key.code)

        self.scanner = Scanner()
        self.scanner.fetchStocksFromCSVFile(path=path, nItems=self.countryConfig.nItems)
        self.strategy = StrategyZigZag()
        self.strategyConfig = getStrategyConfigFor(key=key, timezone=self.countryConfig.timezone)
        self.portfolio = Portfolio()
        self.customBarsDataDict = {}
        self.resultsToTrade = []
        self.databaseModule.openDatabaseConnection()
        self.clearOldFills()
        self.currentFills = self.databaseModule.getFills()

    async def resetVault(self):
        log("🤖 Reset ZigZag Vault 🤖")
        self.delegate.unsubscribeStrategyEvents(self.ib)
        self.setupVault()
        await self.runMarket()

    async def runMarket(self):
        await self.runMarketAt(self.countryConfig.startSetupData)

        await self.ib.accountSummaryAsync()
        await self.ib.reqPositionsAsync()
        await self.ib.reqAllOpenOrdersAsync()
        self.updatePortfolio()

        self.delegate.subscribeStrategyEvents(self.ib)
        await self.fetchHistoricalData()
        self.runStrategy()
        await self.handleResultsToTrade()
        await self.ib.reqPositionsAsync()
        await self.ib.reqAllOpenOrdersAsync()
        await self.runStrategyForPositions()
        await self.closeMarketAt(self.countryConfig.closeMarket)
        
    async def runMarketAt(self, time: datetime):
        marketTime = time.astimezone(timezone('UTC'))
        nowTime = datetime.now().astimezone(timezone('UTC'))
        difference = (marketTime - nowTime)
        if difference.total_seconds() < 0:
            print("😉 See you Tomorrow 😉")
            marketTime += timedelta(days=1)
            difference = (marketTime - nowTime)
            self.countryConfig = updateMarketConfigForNextDay(self.countryConfig)
        if difference.total_seconds() > 900: # Maior do que 15 minutos
            localTime = marketTime.astimezone(timezone('Europe/Lisbon'))
            log("🕐 Run Market for %s at %d/%d %d:%d 🕐" % (self.countryConfig.key.code, localTime.day, localTime.month, localTime.hour, localTime.minute))
            coro = asyncio.sleep(difference.total_seconds())
            self.delegate.marketWaiter = asyncio.ensure_future(coro)
            await asyncio.wait([self.delegate.marketWaiter])
            self.delegate.marketWaiter = None
        log("🕐 Run Market for %s now 🕐" % self.countryConfig.key.code)
            
    async def closeMarketAt(self, time: datetime):
        marketTime = time.astimezone(timezone('UTC'))
        nowTime = datetime.now().astimezone(timezone('UTC'))
        localMarketTime = marketTime.astimezone(timezone('Europe/Lisbon'))
        log("🕐 Closing Market for %s scheduled to %d/%d %d:%d 🕐" % (self.countryConfig.key.code, localMarketTime.day, localMarketTime.month, localMarketTime.hour, localMarketTime.minute))
        difference = (marketTime - nowTime)
        coro = asyncio.sleep(difference.total_seconds())
        self.delegate.marketWaiter = asyncio.ensure_future(coro)
        await asyncio.wait([self.delegate.marketWaiter])
        self.delegate.marketWaiter = None
        await self.resetVault()

    # Strategy

    def runStrategy(self):
        for stock in self.stocks:
            ticker = ibTicker(contract=stock)
            customBars = self.customBarsDataDict[stock.symbol]
            zigzagFound = False
            if len(customBars) >= 5:
                currentBar = customBars[-1]
                #log("😳 [%s] CurrentBar-> High(%.2f) Low(%s) 😳" % (currentBar.date, currentBar.high, currentBar.low))
                previousBars = [] 
                index = -2
                while index >= -5:
                    #log("😳 [%d] 😳" % (index))
                    bar, zigzagFound = self.getCustomBarData(customBars[index], zigzagFound)
                    previousBars.insert(0, bar)
                    index -= 1
                position = self.getPosition(ticker)
                fill = self.getFill(ticker)
                data = StrategyData(ticker=ticker, 
                                    position=position, 
                                    order=None, 
                                    totalCash=self.portfolio.totalCashBalance,
                                    previousBars=previousBars,
                                    currentBar=currentBar,
                                    fill=fill)
            # if self.isValidToRunStrategy(currentBar, previousBars):
            result = self.strategy.run(data, self.strategyConfig, self.countryConfig)
            logExecutionZigZag(data, result)
            self.handleStrategyResult(result, ticker.contract)
            # else:
            # log("🧐 Invalid previousBars for %s. (Probably because this zigzag match was found in the past)🧐" % ticker.contract.symbol)

    def getCustomBarData(self, bar: CustomBarData, found: bool):
        #log("😳 [%s] Bar-> High(%.2f) Low(%.2f) RSI(%.2f) ZigZag(%s) 😳" % (bar.date, bar.high, bar.low, bar.rsi, bar.zigzag))
        if found:
            bar.zigzag = False
        elif bar.zigzag == True:
            found = True
        return (bar, found)

    async def runStrategyForPositions(self):
        time = self.countryConfig.closeMarket-timedelta(hours=1)
        marketTime = time.astimezone(timezone('UTC'))
        nowTime = datetime.now().astimezone(timezone('UTC'))
        localMarketTime = marketTime.astimezone(timezone('Europe/Lisbon'))
        log("🕐 Validate current Positions scheduled for %d/%d %d:%d 🕐" % (localMarketTime.day, localMarketTime.month, localMarketTime.hour, localMarketTime.minute))
        difference = (marketTime - nowTime)
        safe_margin = 5
        coro = asyncio.sleep(difference.total_seconds()+safe_margin)
        self.delegate.marketWaiter = asyncio.ensure_future(coro)
        await asyncio.wait([self.delegate.marketWaiter])
        self.delegate.marketWaiter = None

        log("⭐️ Checking Positions ⭐️")

        fills = self.currentFills
        
        for fill in fills:
            stock = ibStock(symbol=fill.symbol, exchange="SMART", currency="USD")
            tick = ibTicker(contract=stock)
            position = self.getPosition(tick)
            if (position is not None):
                log("⭐️ Checking Position for (%s) ⭐️" % stock.symbol)
                data = StrategyData(ticker=tick, 
                                    position=position, 
                                    order=None, 
                                    totalCash=None,
                                    fill=fill)
                result = self.strategy.run(data, self.strategyConfig, self.countryConfig)
                logExecutionZigZag(data, result)
                self.handleStrategyResult(result, tick.contract)

    def handleStrategyResult(self, result: StrategyResult, contract: ibContract):
        if (result.type == StrategyResultType.Buy or result.type == StrategyResultType.Sell):
            self.resultsToTrade.append(result)

        elif (result.type == StrategyResultType.PositionExpired_Buy or result.type == StrategyResultType.PositionExpired_Sell):
            orderAction = OrderAction.Buy.value if result.type == StrategyResultType.PositionExpired_Buy else OrderAction.Sell.value
            return self.cancelPosition(orderAction, result.position)
        else:
            log("🤨 %s " % result)

        return

    def shouldRunStrategy(self, contract: ibContract, newDatetime: datetime):
        if not contract.symbol in self.stocksExtraInfo:
            return True
        elif self.stocksExtraInfo[contract.symbol].lastExecution:
            newDatetime = utcToLocal(newDatetime.replace(microsecond=0), self.countryConfig.timezone)
            datetime = self.stocksExtraInfo[contract.symbol].lastExecution.replace(microsecond=0)
            return newDatetime > datetime
        else:
            return True

    async def handleResultsToTrade(self):
        self.resultsToTrade.sort(key=lambda x: x.priority, reverse=True)
        for result in self.resultsToTrade:
            if self.canCreateOrder(result.ticker.contract, result.order):
                if result.order.totalQuantity > 1:
                    await self.createOrder(result.ticker.contract, result.order)
                    self.saveFill(result.ticker)
                else:
                    log("❗️ (%s) Order Size is lower then 2 Shares❗️" % result.ticker.contract.symbol)
                    None

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
            if stock.symbol not in self.customBarsDataDict:
                self.customBarsDataDict[stock.symbol] = []
            histData = self.historicalData.createListOfCustomBarsData(bars)
            if len(histData) > 0:
                self.customBarsDataDict[stock.symbol] = histData
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

    def getFill(self, ticker: ibTicker):
        fills = self.currentFills
        filteredFills = list(filter(lambda x: ticker.contract.symbol == x.symbol, fills))
        filteredFills.sort(key=lambda x: x.date, reverse=True)
        if len(filteredFills) > 0:
            log("🧶 Fill Found %s - %s 🧶" % (filteredFills[0].symbol, filteredFills[0].date))
            return filteredFills[0]
        return None

    def saveFill(self, ticker: ibTicker):
        fill = FillDB(ticker.contract.symbol, date.today())
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

    def getPosition(self, ticker: ibTicker):
        return self.portfolio.getPosition(ticker.contract)

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

    async def createOrder(self, contract: ibContract, order: Order):
        newOrder = order
        profitOrder = order.takeProfitOrder
        stopLossOrder = order.stopLossOrder
        await self.portfolio.createOrder(self.ib, contract, newOrder, profitOrder, stopLossOrder)

    def cancelOrder(self, contract: ibContract):
        return self.portfolio.cancelOrder(self.ib, contract)

    # Portfolio - Manage Positions

    def cancelPosition(self, orderAction: OrderAction, position: ibPosition):
        return self.portfolio.cancelPosition(self.ib, orderAction, position)

    # Scanner

    @property
    def stocks(self):
        return self.scanner.stocks
