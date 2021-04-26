import asyncio
from enum import Enum
from typing import Protocol
from datetime import datetime
from ib_insync import IB, Ticker as ibTicker, Contract as ibContract, Order as ibOrder, LimitOrder, StopOrder, Position as ibPosition, BarData
from helpers import logExecutionZigZag, log, utcToLocal, logCounter
from models import Order, OrderAction, CustomBarData
from scanner import Scanner
from strategy import Strategy, StrategyZigZag, StrategyData, StrategyResult, StrategyResultType, HistoricalData, StrategyConfig, getStrategyConfigFor
from country_config import *
from portfolio import Portfolio
from earnings_calendar import EarningsCalendar

class IslandProtocol(Protocol):
    marketWaiter: asyncio.Future

    def subscribeStrategyEvents(self, ib: IB):
        """Subscribe Events"""

    def unsubscribeStrategyEvents(self, ib: IB):
        """Subscribe Events"""

class VaultZigZag:
    ib: IB
    countryConfig: CountryConfig
    strategyConfig: StrategyConfig
    scanner: Scanner
    strategy: Strategy
    portfolio: Portfolio
    historicalData: HistoricalData
    customBarsDataDict: [str, [CustomBarData]]

    delegate: IslandProtocol

    def __init__(self, delegate: IslandProtocol):
        self.setupVault()
        self.historicalData = HistoricalData()
        self.delegate = delegate
        self.customBarsDataDict = {}

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
            if len(customBars) >= 4:
                currentBar = customBars[-1]
                previousBars = [customBars[-4], customBars[-3], customBars[-2]]
                data = StrategyData(ticker=ticker, 
                                    position=None, 
                                    order=None, 
                                    totalCash=self.portfolio.totalCashBalance,
                                    previousBars=previousBars,
                                    currentBar=currentBar)
            result = self.strategy.run(data, self.strategyConfig, self.countryConfig)
            logExecutionZigZag(data, result)
            self.handleStrategyResult(result, ticker.contract)

    async def runStrategyForPositions(self):
        time = self.countryConfig.closeMarket-timedelta(hours=2)
        marketTime = time.astimezone(timezone('UTC'))
        nowTime = datetime.now().astimezone(timezone('UTC'))
        localMarketTime = marketTime.astimezone(timezone('Europe/Lisbon'))
        log("🕐 Validate current Positions scheduled for %d/%d %d:%d 🕐" % (localMarketTime.day, localMarketTime.month, localMarketTime.hour, localMarketTime.minute))
        difference = (marketTime - nowTime)
        coro = asyncio.sleep(difference.total_seconds())
        self.delegate.marketWaiter = asyncio.ensure_future(coro)
        await asyncio.wait([self.delegate.marketWaiter])
        self.delegate.marketWaiter = None

        log("⭐️ Checking Positions ⭐️")

        fills = self.portfolio.getFills(self.ib)
        
        for fill in fills:
            tick = ibTicker(contract=fill.contract)
            position = self.getPosition(tick)
            if (position is not None and
                position.position >=  fill.execution.shares):
                data = StrategyData(ticker=tick, 
                                    position=position, 
                                    order=None, 
                                    totalCash=None,
                                    fill=fill)
                result = self.strategy.run(data, self.strategyConfig, self.countryConfig)
                logExecutionZigZag(data, result)
                self.handleStrategyResult(result, ticker.contract)

    def handleStrategyResult(self, result: StrategyResult, contract: ibContract):
        if ((result.type == StrategyResultType.Buy or result.type == StrategyResultType.Sell) and
            self.canCreateOrder(contract, result.order)):
            if result.order.totalQuantity > 1:
                return self.createOrder(contract, result.order)
            else:
                log("❗️ (%s) Order Size is lower then 2 Shares❗️" % result.ticker.contract.symbol)
                return None

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

    # Historical Data
    
    async def fetchHistoricalData(self):
        total = len(self.stocks)
        current = 0
        for stock in self.stocks:
            current +=1
            logCounter("Historical Data", total, current)
            if stock.symbol not in self.customBarsDataDict:
                self.customBarsDataDict[stock.symbol] = []
            bars = await self.historicalData.downloadHistoricDataFromIB(self.ib, stock, 40, "1 day")
            self.customBarsDataDict[stock.symbol] = self.historicalData.createListOfCustomBarsData(bars)
            log("🧶 Historical Data for %s 🧶" % (stock.symbol))

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

    # Scanner

    @property
    def stocks(self):
        return self.scanner.stocks
