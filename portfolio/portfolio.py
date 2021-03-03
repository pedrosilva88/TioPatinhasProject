from datetime import datetime
from ib_insync import *
from order import Order, OrderType, OrderState, OrderExecutionType, StockPosition

class Portfolio:
    cashBalance: float
    positions: [StockPosition]
    orders: [Order]

    @property
    def cashAvailable(self):
        return max(self.cashBalance - 400, 0)

    def __init__(self):
        self.positions = []
        self.trades = []
        self.cashBalance = 0
        self.totalCashBalance = 0
        self.totalCashBalanceLastUpdate = None

    def updatePortfolio(self, ib: IB):
        self.positions = self.parsePositons(ib)
        self.orders = self.parseOrders(ib)
        
        accountValues: [AccountValue] = ib.accountValues()
        account = [d for d in accountValues if d.tag == "AvailableFunds"].pop()
        self.cashBalance = account.value

        currentDatetime = datetime.now()
        if (not self.totalCashBalanceLastUpdate or currentDatetime.date != self.totalCashBalanceLastUpdate.date):
            print("Total Cash: %s" % account.value)
            print(currentDatetime)
            self.totalCashBalance = account.value
            self.totalCashBalanceLastUpdate = currentDatetime

    def parsePositons(self, ib: IB):
        items = ib.positions()
        list = []
        for item in items:
            type = OrderType.Long if item.position > 0 else OrderType.Short
            position = StockPosition(item.contract.symbol, item.avgCost, item.position, type)
            list.append(position)
        
        return list

    def parseOrders(self, ib: IB):
        items = ib.trades()
        subItems = self.filterSubOrders(items)
        list: [Order] = []
        for item in items:
            if (item.orderStatus.status == OrderState.Submitted.value and not item.order.ocaGroup):
                type = OrderType.Long if item.order.totalQuantity > 0 else OrderType.Short
                profitPrice, stopLossPrice = self.parseSubOrders(item.order.permId, type, subItems)

                executionType = OrderExecutionType.LimitOrder if item.order.orderType == "LMT" else OrderExecutionType.MarketPrice
                order = Order(type, item.contract.symbol, item.order.totalQuantity, item.order.lmtPrice, executionType, profitPrice, stopLossPrice)
                list.append(order)
        return list

    def filterSubOrders(self, orders: [Trade]):
        list = []
        for item in orders:
            if item.order.ocaGroup:
                list.append(item)
        return list

    def parseSubOrders(self, permId: int, type: OrderType, subOrders: [Trade]):
        profitPrice = None
        stopLossPrice = None
        for item in subOrders:
            if int(item.order.ocaGroup) == permId:
                if item.order.orderType == 'STP':
                    stopLossPrice = item.order.auxPrice
                else:
                    profitPrice = item.order.lmtPrice
        return profitPrice, stopLossPrice

    def getPosition(self, ticker: Ticker):
        for position in self.positions:
            if position.ticker == ticker.contract.symbol:
                return position
        return None
    
    def getOrder(self, ticker: Ticker):
        for order in self.orders:
            if order.ticker == ticker.contract.symbol:
                return order
        return None

    def createOrder(self, ib: IB, order: Order):
        if len(self.positions) >= 3:
            return
        stock = Stock(order.ticker, "SMART", "USD")
        type = "BUY" if order.type == OrderType.Long else "SELL"
        ib.bracketOrder(type, order.size, order.price, order.takeProfitPrice, order.stopLossPrice)

            #      List<Order> bracket = OrderSamples.BracketOrder(nextOrderId++, "BUY", 100, 30, 40, 20);
            # foreach (Order o in bracket)
            #     client.placeOrder(o.OrderId, ContractSamples.EuropeanStock(), o);
    
    def updateOrder(self, ib: IB, order: Order):
        return None

    def cancelOrder(self, ib: IB, order: Order):
        return None



