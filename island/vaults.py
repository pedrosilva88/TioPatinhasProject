from enum import Enum
from datetime import datetime
from ib_insync import IB, Ticker as ibTicker, Contract as ibContract, Order as ibOrder, LimitOrder, StopOrder, Position as ibPosition
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
            self.updateVolumeInFirstMinuteBar(ticker)
            position = self.getPosition(ticker)
            order = self.getOrder(ticker)
            averageVolume = None
            volumeFirstMinute = None
            if ticker.contract.symbol in self.stocksExtraInfo:
                stockInfo = self.stocksExtraInfo[ticker.contract.symbol]
                if stockInfo.averageVolume:
                    averageVolume = stockInfo.averageVolume
                if stockInfo.volumeFirstMinute:
                    log("🧶 🧶 Sending Volume First minute for %s: %.2f 🧶 🧶" ,(ticker.contract.symbol, ticker.volume))
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
            return self.createOrder(contract, result.order)

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
                if stock.symbol in self.stocksExtraInfo:
                    model = self.stocksExtraInfo[stock.symbol]
                    model.averageVolume = averageVolume
                else:
                    self.stocksExtraInfo[stock.symbol] = StockInfo(symbol=stock.symbol, averageVolume=averageVolume)

    def updateVolumeInFirstMinuteBar(self, ticker: ibTicker):
        model = None
        stock = ticker.contract
        if stock.symbol in self.stocksExtraInfo:
            model = self.stocksExtraInfo[stock.symbol]  

        time = utcToLocal(ticker.time, self.countryConfig.timezone)
        if (time.hour == self.strategyConfig.startRunningStrategy.hour and 
            time.minute == self.strategyConfig.startRunningStrategy.minute and
            ticker.volume >= 0 and
            (not model or not model.volumeFirstMinute)):
            log("🧶 Volume first minute for %s: %.2f 🧶" ,(ticker.contract.symbol, ticker.volume))
            if not model:
                model = StockInfo(symbol=stock.symbol, volumeFirstMinute=ticker.volume)
                self.stocksExtraInfo[stock.symbol] = model
            if not model.volumeFirstMinute:
                model.volumeFirstMinute = ticker.volume
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
        # self.ib.cancelRealTimeBars()
        return 

    def subscribeTicker(self, contract: ibContract):
        self.ib.reqMktData(contract)
        #self.ib.reqHistoricalDataAsync(contract, '', '5 D', '1 min', "TRADES", True, 1, True)
        #self.ib.reqRealTimeBars(contract, 5, 'TRADES', True)

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
