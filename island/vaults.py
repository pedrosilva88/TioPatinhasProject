import asyncio
from enum import Enum
from typing import Protocol
from datetime import datetime
from ib_insync import IB, Ticker as ibTicker, Contract as ibContract, Order as ibOrder, LimitOrder, StopOrder, Position as ibPosition, BarData
from helpers import logExecutionTicker
from models import Order, OrderAction, StockInfo
from scanner import Scanner
from strategy import Strategy, StrategyOPG, StrategyData, StrategyResult, StrategyResultType, HistoricalData, StrategyConfig, getStrategyConfigFor
from country_config import *
from portfolio import Portfolio
from earnings_calendar import EarningsCalendar
from helpers import log, utcToLocal, logCounter

class IslandProtocol(Protocol):
    marketWaiter: asyncio.Future

    def subscribeStrategyEvents(self, ib: IB):
        """Subscribe Events"""

    def unsubscribeStrategyEvents(self, ib: IB):
        """Subscribe Events"""

class Vault:
    ib: IB
    countryConfig: CountryConfig
    strategyConfig: StrategyConfig
    scanner: Scanner
    strategy: Strategy
    portfolio: Portfolio
    earningsCalendar: EarningsCalendar
    historicalData: HistoricalData
    stocksExtraInfo: [str, StockInfo]

    delegate: IslandProtocol

    def __init__(self, delegate: IslandProtocol):
        self.setupVault()
        self.earningsCalendar = EarningsCalendar()
        self.historicalData = HistoricalData()
        self.delegate = delegate

    # Setup

    def setupVault(self):
        self.countryConfig = getCurrentMarketConfig()
        log("🏃‍ Setup Vault for %s 🏃‍"% self.countryConfig.key.code)
        key = self.countryConfig.key
        path = ("scanner/Data/CSV/%s/OPG_Retails_SortFromBackTest.csv" % key.code)

        self.scanner = Scanner()
        self.scanner.getOPGRetailers(path=path, nItems=self.countryConfig.nItems)
        self.strategy = StrategyOPG()
        self.strategyConfig = getStrategyConfigFor(key=key, timezone=self.countryConfig.timezone)
        self.portfolio = Portfolio()
        self.stocksExtraInfo = {}

    async def resetVault(self):
        log("🤖 Reset Vault 🤖")
        for stock in self.stocks:
            self.unsubscribeTicker(stock)
        self.delegate.unsubscribeStrategyEvents(self.ib)
        self.setupVault()
        await self.runMarket()

    async def runMarket(self):
        await self.runMarketAt(self.countryConfig.startSetupData)

        await self.ib.accountSummaryAsync()
        await self.ib.reqPositionsAsync()
        await self.ib.reqAllOpenOrdersAsync()
        await self.getDataFromStocks()
        self.getEraningsCalendarIfNecessary() # Isto aqui pode ser async. Preciso de estudar melhor
        self.updatePortfolio()

        self.delegate.subscribeStrategyEvents(self.ib)
        self.subscribeTickers()
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

    def runStrategy(self, data: StrategyData):
        return self.strategy.run(data, self.strategyConfig, self.countryConfig)

    def executeTicker(self, ticker: ibTicker):
        if self.shouldRunStrategy(ticker.contract, ticker.time):
            if ticker.contract.symbol in self.stocksExtraInfo:
                model = self.stocksExtraInfo[ticker.contract.symbol]
                self.updateVolumeInFirstMinuteBar(model.realTimeBarList, ticker.time)

            position = self.getPosition(ticker)
            order = self.getOrder(ticker)
            averageVolume = None
            volumeFirstMinute = None
            contractDetails = None
            if ticker.contract.symbol in self.stocksExtraInfo:
                stockInfo = self.stocksExtraInfo[ticker.contract.symbol]
                contractDetails = stockInfo.contractDetails
                if (stockInfo.averageVolume is not None):
                    log("🧶 🕯 Sending Avg Volume for %s: %.2f 🕯 🧶" % (ticker.contract.symbol, stockInfo.averageVolume))
                    averageVolume = stockInfo.averageVolume
                if (stockInfo.volumeFirstMinute is not None):
                    log("🧶 🧶 Sending Volume First minute for %s: %.2f 🧶 🧶" % (ticker.contract.symbol, stockInfo.volumeFirstMinute))
                    volumeFirstMinute = stockInfo.volumeFirstMinute

            data = StrategyData(ticker, 
                                position, 
                                order, 
                                self.portfolio.totalCashBalance,
                                averageVolume,
                                volumeFirstMinute,
                                contractDetails)

            result = self.runStrategy(data)
            self.registerLastExecution(ticker.contract, ticker.time)
            logExecutionTicker(data, result)
            self.handleStrategyResult(result, ticker.contract)

    def handleStrategyResult(self, result: StrategyResult, contract: ibContract):
        if ((result.type == StrategyResultType.Buy or result.type == StrategyResultType.Sell) and
            self.canCreateOrder(contract, result.order)):
            if result.order.totalQuantity > 1:
                return self.createOrder(contract, result.order)
            else:
                log("❗️ (%s) Order Size is lower then 2 Shares❗️" % result.ticker.contract.symbol)
                return None

        elif (result.type == StrategyResultType.StrategyDateWindowExpired or result.type == StrategyResultType.DoNothing):
            return self.unsubscribeTicker(contract)

        elif (result.type == StrategyResultType.PositionExpired_Buy or result.type == StrategyResultType.PositionExpired_Sell):
            orderAction = OrderAction.Buy.value if result.type == StrategyResultType.PositionExpired_Buy else OrderAction.Sell.value
            return self.cancelPosition(orderAction, result.position)

        elif result.type == StrategyResultType.KeepOrder:
            return self.updateOrder(result.ticker.contract, result.order)

        elif (result.type == StrategyResultType.CancelOrder or result.type == StrategyResultType.StrategyDateWindowExpiredCancelOrder):
            self.unsubscribeTicker(contract)
            return self.cancelOrder(result.ticker.contract)

        return

    def registerLastExecution(self, contract: ibContract, datetime: datetime):
        if contract.symbol in self.stocksExtraInfo:
            model = self.stocksExtraInfo[contract.symbol]
            model.lastExecution = utcToLocal(datetime, self.countryConfig.timezone)
        else:
            self.stocksExtraInfo[contract.symbol] = StockInfo(symbol=contract.symbol, lastExecution=utcToLocal(datetime, self.countryConfig.timezone))
    
    def shouldRunStrategy(self, contract: ibContract, newDatetime: datetime):
        if not contract.symbol in self.stocksExtraInfo:
            return True
        elif self.stocksExtraInfo[contract.symbol].lastExecution:
            newDatetime = utcToLocal(newDatetime.replace(microsecond=0), self.countryConfig.timezone)
            datetime = self.stocksExtraInfo[contract.symbol].lastExecution.replace(microsecond=0)
            return newDatetime > datetime
        else:
            return True

    # Get extra data from stocks - Volume & Contract Details

    async def getDataFromStocks(self):
        total = len(self.stocks)
        current = 0
        for stock in self.stocks:
            current +=1
            logCounter("Volumes & Contract Details", total, current)
            if stock.symbol not in self.stocksExtraInfo:
                self.stocksExtraInfo[stock.symbol] = StockInfo(symbol=stock.symbol)
            model = self.stocksExtraInfo[stock.symbol]
            await self.getAverageVolumeOfStock(stock, model)
            await self.getContractDetailsOfStock(stock, model)

    async def getAverageVolumeOfStock(self, stock: ibContract, model: StockInfo):
        averageVolume = await self.historicalData.getAverageVolume(self.ib, stock, 5)
        if averageVolume is not None:
            log("🧶 Volume for %s: %.2f 🧶" % (stock.symbol, averageVolume))
            model.averageVolume = averageVolume
        else:
            log("🚨 Error getting AVG Volume for %s: 🚨" % (stock.symbol))

    async def getContractDetailsOfStock(self, stock: ibContract, model: StockInfo):
        contractDetails = await self.historicalData.getContractDetails(self.ib, stock)
        if (len(contractDetails)> 0 and (contractDetails[0] is not None)):
            details = contractDetails[0]
            log("🧶 Contract Details for %s: MinTick(%.2f) 🧶" % (stock.symbol, details.minTick))
            model.contractDetails = contractDetails[0]
        else:
            log("🚨 Error getting Contract Details for %s: 🚨" % (stock.symbol))

    def updateVolumeInFirstMinuteBar(self, bars: [BarData], time: datetime):
        model = None
        stock = bars.contract
        barDatetime = time
        if stock.symbol in self.stocksExtraInfo:
            model = self.stocksExtraInfo[stock.symbol]  

        time = utcToLocal(barDatetime, self.countryConfig.timezone)
        if (time.hour == self.strategyConfig.startRunningStrategy.hour and 
            time.minute >= self.strategyConfig.startRunningStrategy.minute and
            ((model is None) or (model.volumeFirstMinute is None))):
            volume = 0
            for bar in bars:
                dataTime = utcToLocal(bar.time, self.countryConfig.timezone)
                if (dataTime.time().hour == self.strategyConfig.startRunningStrategy.hour and
                    dataTime.time().minute == self.strategyConfig.startRunningStrategy.minute-1):
                    volume += bar.volume
            if volume >= 0:
                log("🧶 Volume first minute for %s: %.2f 🧶" % (stock.symbol, volume))
                if (model is None):
                    model = StockInfo(symbol=stock.symbol, volumeFirstMinute=volume)
                    self.stocksExtraInfo[stock.symbol] = model
                if (model.volumeFirstMinute is None):
                    model.volumeFirstMinute = volume
                    self.stocksExtraInfo[stock.symbol] = model

    # Earning Calendar

    def handleEarningsCalendar(self, contract: ibContract, date: datetime):
        today = datetime.today().date()
        if date.date() == today:
            log("%s have earnings today! Will be ignored" % contract.symbol)
            self.stocks.remove(contract)

    def getEraningsCalendarIfNecessary(self):
        if self.strategy.shouldGetStockEarnings():
            log("🗓  Requesting earnings calendar 🗓")
            self.earningsCalendar.requestEarnings(self.stocks, self.handleEarningsCalendar)
        log("🗓  Finished 🗓\n")

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

    def updateOrder(self, contract: ibContract, order: Order):
        newOrder = order
        profitOrder = order.takeProfitOrder
        stopLossOrder = order.stopLossOrder
        return self.portfolio.updateOrder(self.ib, contract, newOrder, profitOrder, stopLossOrder)

    def cancelOrder(self, contract: ibContract):
        return self.portfolio.cancelOrder(self.ib, contract)

    # Portfolio - Manage Positions

    def cancelPosition(self, orderAction: OrderAction, position: ibPosition):
        return self.portfolio.cancelPosition(self.ib, orderAction, position)

    # Scanner

    @property
    def stocks(self):
        return self.scanner.stocks

    def subscribeTickers(self):
        contracts = [stock for stock in self.stocks]
        for contract in contracts:
            self.subscribeTicker(contract)

    # IB

    def unsubscribeTicker(self, contract: ibContract):
        log("👋 Unsubscribe Contract %s 👋" % contract.symbol) 
        self.ib.cancelMktData(contract)
        if contract.symbol in self.stocksExtraInfo:
            model = self.stocksExtraInfo[contract.symbol]
            if (model.realTimeBarList is not None):
                self.ib.cancelRealTimeBars(model.realTimeBarList)
        self.scanner.removeTicker(contract.symbol)
        return 

    def subscribeTicker(self, contract: ibContract):
        self.ib.reqMktData(contract)
        model = None
        if contract.symbol in self.stocksExtraInfo:
            model = self.stocksExtraInfo[contract.symbol]  
        else:
            model = StockInfo(contract.symbol)
            self.stocksExtraInfo[contract.symbol] = model
        model.realTimeBarList = self.ib.reqRealTimeBars(contract, 5, 'TRADES', True)

def createOPGRetailVault():
    return Vault()
