from enum import Enum
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

class VaultType(Enum):
    OPG_US_RTL = 1
    OPG_UK_RTL = 2
    
    def __str__(self):
        if self == OPG_US_RTL: return "Opening Price Gap for US Retailers"
        if self == OPG_UK_RTL: return "Opening Price Gap for UK Retailers"

class Vault:
    type: VaultType
    ib: IB
    countryConfig: CountryConfig
    strategyConfig: StrategyConfig
    scanner: Scanner
    strategy: Strategy
    portfolio: Portfolio
    earningsCalendar: EarningsCalendar
    historicalData: HistoricalData
    stocksExtraInfo: [str, StockInfo]

    def __init__(self, type: VaultType, countryConfig: CountryConfig, scanner: Scanner, strategy: Strategy, strategyConfig: StrategyConfig, portfolio: Portfolio):
        self.type = type
        self.countryConfig = countryConfig
        self.scanner = scanner
        self.strategy = strategy
        self.strategyConfig = strategyConfig
        self.portfolio = portfolio
        self.earningsCalendar = EarningsCalendar()
        self.historicalData = HistoricalData()
        self.stocksExtraInfo = {}

    # Strategy

    def runStrategy(self, data: StrategyData):
        return self.strategy.run(data, self.strategyConfig, self.countryConfig)

    def executeTicker(self, ticker: ibTicker):
        if self.shouldRunStrategy(ticker.contract, ticker.time):
            position = self.getPosition(ticker)
            order = self.getOrder(ticker)
            averageVolume = None
            volumeFirstMinute = None
            if ticker.contract.symbol in self.stocksExtraInfo:
                stockInfo = self.stocksExtraInfo[ticker.contract.symbol]
                if stockInfo.averageVolume:
                    log("🧶 🕯 Sending Avg Volume for %s: %.2f 🕯 🧶" % (ticker.contract.symbol, stockInfo.averageVolume))
                    averageVolume = stockInfo.averageVolume
                if stockInfo.volumeFirstMinute:
                    log("🧶 🧶 Sending Volume First minute for %s: %.2f 🧶 🧶" % (ticker.contract.symbol, stockInfo.volumeFirstMinute))
                    volumeFirstMinute = stockInfo.volumeFirstMinute

            data = StrategyData(ticker, 
                                position, 
                                order, 
                                self.portfolio.totalCashBalance,
                                averageVolume,
                                volumeFirstMinute)

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
                log("❗️ (%s) Order Size is lower then 2 Shares❗️", result.ticker.contract.symbol)
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

    # Volumes

    async def getAverageVolumeOfStocks(self):
        total = len(self.stocks)
        current = 0
        for stock in self.stocks:
            current +=1
            logCounter("Volumes", total, current)
            averageVolume = await self.historicalData.getAverageVolume(self.ib, stock, 5)
            if averageVolume:
                log("🧶 Volume for %s: %.2f 🧶" % (stock.symbol, averageVolume))
                if stock.symbol in self.stocksExtraInfo:
                    model = self.stocksExtraInfo[stock.symbol]
                    model.averageVolume = averageVolume
                else:
                    self.stocksExtraInfo[stock.symbol] = StockInfo(symbol=stock.symbol, averageVolume=averageVolume)
            else:
                log("🚨 Error getting AVG Volume for %s: 🚨" % (stock.symbol))

    def updateVolumeInFirstMinuteBar(self, bars: [BarData]):
        model = None
        stock = bars.contract
        barDatetime = bars[-1].time
        if stock.symbol in self.stocksExtraInfo:
            model = self.stocksExtraInfo[stock.symbol]  

        time = utcToLocal(barDatetime, self.countryConfig.timezone)
        if (time.hour == self.strategyConfig.startRunningStrategy.hour and 
            time.minute >= self.strategyConfig.startRunningStrategy.minute and
            ((model is None) or (model.volumeFirstMinute is None))):
            volume = -1
            hasMatch = False
            for bar in bars:
                dataTime = utcToLocal(bar.time, self.countryConfig.timezone)
                if (dataTime.time().hour == self.strategyConfig.startRunningStrategy.hour and
                    dataTime.time().minute == self.strategyConfig.startRunningStrategy.minute-1):
                    if not hasMatch:
                        hasMatch = True
                        volume = 0
                    volume += bar.volume
            if volume >= 0:
                log("🧶 Volume first minute for %s: %.2f 🧶" % (stock.symbol, volume))
                if not model:
                    model = StockInfo(symbol=stock.symbol, volumeFirstMinute=volume)
                    self.stocksExtraInfo[stock.symbol] = model
                if not model.volumeFirstMinute:
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

        if profitOrder:
            profit = Order(orderId=profitOrder.orderId, 
                            action=profitOrder.action, 
                            type=profitOrder.orderType,
                            totalQuantity=profitOrder.totalQuantity,
                            price=profitOrder.lmtPrice,
                            parentId=mainOrder.parentId)

        if stopLossOrder:
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

    def getTicker(self, symbol: str):
        return self.scanner.getTicker(symbol)

    def subscribeTickers(self):
        contracts = [stock for stock in self.stocks]
        for contract in contracts:
            self.subscribeTicker(contract)

    # IB

    def unsubscribeTicker(self, contract: ibContract):
        ## Além de fazer cancelmarketData também devia de limpar na list de stocks que tenho no scanner
        log("👋 Unsubscribe Contract %s 👋" % contract.symbol) 
        self.ib.cancelMktData(contract)
        if contract.symbol in self.stocksExtraInfo:
            model = self.stocksExtraInfo[contract.symbol]  
            self.ib.cancelRealTimeBars(model.realTimeBarList)
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

def createOPGRetailVault(key: CountryKey = CountryKey.USA):
    scanner = Scanner()
    countryConfig = getConfigFor(key=key)
    path = ("scanner/Data/CSV/%s/OPG_Retails_SortFromBackTest.csv" % key.code)
    scanner.getOPGRetailers(path=path)
    strategy = StrategyOPG()
    strategyConfig = getStrategyConfigFor(key=key, timezone=countryConfig.timezone)
    portfolio = Portfolio()
    vaultType = VaultType.OPG_UK_RTL if key == CountryKey.UK else VaultType.OPG_US_RTL
    return Vault(vaultType, countryConfig, scanner, strategy, strategyConfig, portfolio)
