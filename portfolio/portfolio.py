from datetime import datetime
from ib_insync import IB, Trade, Ticker, Stock, LimitOrder, MarketOrder, StopOrder
from order import Ticker as Tick, Order, OrderType, OrderState, OrderExecutionType, StockPosition

class Portfolio:
    cashBalance: float
    stockMarketValue: float
    pendingOrdersMarketValue: float
    positions: [StockPosition]
    orders: [Order]

    @property
    def cashAvailable(self):
        return max(self.cashBalance - self.stockMarketValue - self.pendingOrdersMarketValue - 400, 0)

    def __init__(self):
        self.positions = []
        self.trades = []
        self.cashBalance = 0
        self.totalCashBalance = 0
        self.totalCashBalanceLastUpdate = None

    def updatePortfolio(self, ib: IB, getTicker):
        self.positions = self.parsePositons(ib, getTicker)
        self.orders = self.parseOrders(ib, getTicker)
        
        accountValues: [AccountValue] = ib.accountValues()
        account = [d for d in accountValues if d.tag == "AvailableFunds"].pop()
        self.cashBalance = float(account.value)

        currentDatetime = datetime.now()
        if (not self.totalCashBalanceLastUpdate or currentDatetime.date != self.totalCashBalanceLastUpdate.date):
            self.totalCashBalance = float(account.value)
            self.totalCashBalanceLastUpdate = currentDatetime
        print("💵 \nTotal Cash: %s \nCash Balance: %s \nAvailable Cash: %s \n💵\n" % (self.totalCashBalance, self.cashBalance, self.cashAvailable))

    def parsePositons(self, ib: IB, getTicker):
        items = ib.positions()
        list = []
        totalValue = 0
        for item in items:
            type = OrderType.Long if item.position > 0 else OrderType.Short
            position = StockPosition(getTicker(item.contract.symbol), item.avgCost, item.position, type)
            totalValue += item.avgCost * item.position
            list.append(position)
        
        self.stockMarketValue = totalValue
        return list

    def parseOrders(self, ib: IB, getTicker):
        items = ib.trades()
        subItems = self.filterSubOrders(items)
        list: [Order] = []
        totalValue = 0
        for item in items:
            if (item.orderStatus.status == OrderState.Submitted.value and not item.order.ocaGroup):
                type = OrderType.Long if item.order.totalQuantity > 0 else OrderType.Short
                profitPrice, stopLossPrice = self.parseSubOrders(item.order.permId, type, subItems)

                executionType = OrderExecutionType.LimitOrder if item.order.orderType == "LMT" else OrderExecutionType.MarketPrice
                order = Order(type, getTicker(item.contract.symbol), item.order.totalQuantity, item.order.lmtPrice, executionType, profitPrice, stopLossPrice)
                totalValue += item.order.lmtPrice * item.order.totalQuantity
                list.append(order)

        self.pendingOrdersMarketValue = totalValue
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
            if position.ticker.symbol == ticker.contract.symbol:
                return position
        return None
    
    def getOrder(self, ticker: Ticker):
        for order in self.orders:
            if order.ticker.symbol == ticker.contract.symbol:
                return order
        return None

    def createOrder(self, ib: IB, order: Order):
        ## self.orders.append(order) Check if this is necessary
        stock = Stock(order.ticker.symbol, "SMART", "USD")
        type = "BUY" if order.type == OrderType.Long else "SELL"
        if (not order.takeProfitPrice and not order.stopLossPrice):
            limitOrder = LimitOrder(type, order.size, order.price)
            ib.placeOrder(stock, limitOrder)
        else:
            bracket = ib.bracketOrder(type, order.size, order.price, order.takeProfitPrice, order.stopLossPrice)

            for o in bracket:
                if ((isinstance(o, LimitOrder) and o.lmtPrice > 0) or
                    (isinstance(o, StopOrder) and o.auxPrice > 0)):
                    ib.placeOrder(stock, o)
        self.orders = self.parseOrders(ib)
    
    def updateOrder(self, ib: IB, order: Order):
        self.createOrder(ib, order) # Isto ainda tem que ser bem testado

    def cancelOrder(self, ib: IB, order: Order):
        for trade in ib.trades():
            if (trade.orderStatus.status == OrderState.PendingSubmit.value and 
                not trade.order.ocaGroup and
                order.ticker.symbol == trade.contract.symbol):
                ib.cancelOrder(trade.order)

    def cancelPosition(self, ib: IB, position: StockPosition):
        stock = Stock(position.ticker.symbol, 'SMART', 'USD')
        type = "BUY" if order.type == OrderType.Long else "SELL"
        order = MarketOrder(type, position.size)
        ib.placeOrder(stock, order)

    def canCreateOrder(self, ib: IB, order: Order):
        hasOrder = len([d for d in self.orders if d.ticker.symbol == order.ticker.symbol]) > 0
        canCreate = (order.price * order.size) <= self.cashAvailable
        if (not canCreate and 
            not hasOrder):
            print("❗️Can't create Order!❗️\n❗️Cause: already created or insufficient cash: %.2f❗️\n" % self.cashAvailable) 
        return canCreate