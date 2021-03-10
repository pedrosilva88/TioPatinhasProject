from enum import Enum
from datetime import datetime
from ib_insync import IB, Ticker as ibTicker, Contract as ibContract, Order as ibOrder, LimitOrder, StopOrder, Position as ibPosition
from helpers import logExecutionTicker
from models import Order, OrderAction
from scanner import Scanner
from strategy import Strategy, StrategyOPG, StrategyData, StrategyResult, StrategyResultType
from portfolio import Portfolio
from earnings_calendar import EarningsCalendar

class VaultType(Enum):
    OPG_US_RTL = 1
    
    def __str__(self):
        if self == OPG_US_RTL: return "Opening Price Gap for US Retailers"

class Vault:
    type: VaultType
    ib: IB
    scanner: Scanner
    strategy: Strategy
    portfolio: Portfolio
    earningsCalendar: EarningsCalendar
    lastExecutions: dict()

    def __init__(self, type: VaultType, scanner: Scanner, strategy: Strategy, portfolio: Portfolio):
        self.type = type
        self.scanner = scanner
        self.strategy = strategy
        self.portfolio = portfolio
        self.earningsCalendar = EarningsCalendar()
        self.lastExecutions = {}

    # Strategy

    def runStrategy(self, data: StrategyData):
        return self.strategy.run(data)

    def executeTicker(self, ticker: ibTicker):
        #print("Volume(%.2f) - AVVolume(%.2f) - RTVolume(%.2f)" % (ticker.volume, ticker.avVolume, ticker.rtVolume))
        if self.shouldRunStrategy(ticker.contract, ticker.time):
            position = self.getPosition(ticker)
            order = self.getOrder(ticker)

            data = StrategyData(ticker, 
                                position, 
                                order, 
                                self.portfolio.totalCashBalance)

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

        elif result.type == StrategyResultType.StrategyDateWindowExpiredCancelOrder:
            return self.cancelOrder(result.ticker.contract)

        return

    def registerLastExecution(self, contract: ibContract, datetime: datetime):
        self.lastExecutions[contract.symbol] = datetime
    
    def shouldRunStrategy(self, contract: ibContract, newDatetime: datetime):
        if not contract.symbol in self.lastExecutions:
            return True
        newDatetime = newDatetime.replace(microsecond=0, tzinfo=None)
        datetime = self.lastExecutions[contract.symbol].replace(microsecond=0, tzinfo=None)
        return newDatetime > datetime
                # and (newDatetime.second - datetime.second) >= 2 # Caso queira dar um intervalo de 2 segundos por Ticker event

    # Earning Calendar

    def handleEarningsCalendar(self, contract: ibContract, date: datetime):
        today = datetime.today().date()
        if date.date() == today:
            print("%s have earnings today! Will be ignored" % contract.symbol)
            self.stocks.remove(contract)

    def getEraningsCalendarIfNecessary(self):
        if self.strategy.shouldGetStockEarnings():
            print("🗓  Requesting earnings calendar 🗓")
            self.earningsCalendar.requestEarnings(self.stocks, self.handleEarningsCalendar)
        print("🗓  Finished 🗓\n")

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

    def cancelOrder(self, contract: ibContract, order: Order):
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
        self.ib.cancelMktData(contract)
        # self.ib.cancelRealTimeBars()
        return 

    def subscribeTicker(self, contract: ibContract):
        self.ib.reqMktData(contract)
        #self.ib.reqHistoricalDataAsync(contract, '', '5 D', '1 min', "TRADES", True, 1, True)
        #self.ib.reqRealTimeBars(contract, 5, 'TRADES', True)

def createOPGRetailVault():
    scanner = Scanner()
    scanner.getOPGRetailers()
    strategy = StrategyOPG()
    portfolio = Portfolio()
    return Vault(VaultType.OPG_US_RTL, scanner, strategy, portfolio)