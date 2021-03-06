from datetime import datetime
from ib_insync import IB, Order as ibOrder, Position as ibPosition, Trade as ibTrade, Contract as ibContract, LimitOrder, StopOrder
from models import OrderType

class Portfolio:
    cashBalance: float
    stockMarketValue: float
    pendingOrdersMarketValue: float

    positions: [ibPosition]
    trades: [ibTrade]

    getTicker = None

    @property
    def cashAvailable(self):
        # TODO: Tenho que rever isto
        return max(self.cashBalance - self.stockMarketValue - self.pendingOrdersMarketValue - 400, 0)

    def __init__(self):
        self.positions = []
        self.trades = []
        self.cashBalance = 0
        self.totalCashBalance = 0
        self.totalCashBalanceLastUpdate = None

    def updatePortfolio(self, ib: IB):
        # TODO: Validar se posso remover isto e a parte de baixo funciona
        # self.positions = self.parsePositons(ib)
        # self.trades = self.filterForCurrentOrders(ib)

        self.positions = ib.positions()
        self.trades = ib.openTrades()
        
        accountValues: [AccountValue] = ib.accountValues()
        account = [d for d in accountValues if d.tag == "AvailableFunds"].pop()
        self.cashBalance = float(account.value)

        currentDatetime = datetime.now()
        if (not self.totalCashBalanceLastUpdate or currentDatetime.date != self.totalCashBalanceLastUpdate.date):
            self.totalCashBalance = float(account.value)
            self.totalCashBalanceLastUpdate = currentDatetime
        print("💵 \nTotal Cash: %s \nCash Balance: %s \nAvailable Cash: %s \n💵\n" % (self.totalCashBalance, self.cashBalance, self.cashAvailable))

    def calcPositionsValue(self, ib: IB):
        totalValue = 0
        for item in self.positions:
            totalValue += item.avgCost * item.position        
        self.stockMarketValue = totalValue

    def calcOpenTradesValue(self, ib: IB):
        totalValue = 0
        for item in self.trades:
            if item.order.parentId == 0:
                totalValue += item.order.lmtPrice * item.order.totalQuantity
        self.pendingOrdersMarketValue = totalValue

    def getPosition(self, contract: Contract):
        for position in self.positions:
            if position.contract.symbol == contract.symbol:
                return position
        return None
    
    def getTradeOrders(self, contract: ibContract):
        mainOrder = None
        profitOrder = None
        stopLossOrder = None

        for trade in self.trades:
            if trade.contract.symbol == contract.symbol:
                order = trade.order
                if isinstance(order, LimitOrder) and order.parentId == 0:
                    mainOrder = order
                elif isinstance(order, LimitOrder) and order.parentId > 0:
                    profitOrder = order
                elif isinstance(order, StopOrder) and order.parentId > 0:
                    stopLossOrder = order
        return mainOrder, profitOrder, stopLossOrder

    def createOrder(self, ib: IB, contract: ibContract, orderType: OrderType, order: ibOrder, profitOrder: ibOrder = None, stopLossOrder: ibOrder = None):
        ## self.orders.append(order) Check if this is necessary

        if (not profitOrder and not stopLossOrder):
            limitOrder = LimitOrder(orderType, order.size, order.price)
            ib.placeOrder(stock, limitOrder)
        else:
            bracket = ib.bracketOrder(orderType, order.totalQuantity, order.lmtPrice, profitOrder.lmtPrice, stopLossOrder.auxPrice)

            for o in bracket:
                if ((isinstance(o, LimitOrder) and o.lmtPrice > 0) or
                    (isinstance(o, StopOrder) and o.auxPrice > 0)):
                    ib.placeOrder(stock, o)

        self.trades = self.openTrades(ib)
    
    def updateOrder(self, ib: IB, contract: ibContract):
        self.createOrder(ib, order) # Isto ainda tem que ser bem testado

    def cancelOrder(self, ib: IB, order: Order):
        for trade in self.trades:
            if (trade.order.parentId == 0 and
                contract.symbol == trade.contract.symbol):
                ib.cancelOrder(trade.order)

    def cancelPosition(self, ib: IB, orderType: OrderType, position: ibPosition):
        order = MarketOrder(orderType, position.size)
        ib.placeOrder(position.contract, order)

    def canCreateOrder(self, ib: IB, contract: ibContract, order: ibOrder):
        hasOrder = len([d for d in self.trades if d.contract.symbol == contract.symbol]) > 0
        canCreate = (order.lmtPrice * order.totalQuantity) <= self.cashAvailable
        if (not canCreate and 
            not hasOrder):
            print("❗️Can't create Order!❗️\n❗️Cause: already created or insufficient cash: %.2f❗️\n" % self.cashAvailable) 
        return canCreate