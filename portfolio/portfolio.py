from datetime import datetime
from ib_insync import IB, Order as ibOrder, Position as ibPosition, Trade as ibTrade, Contract as ibContract, LimitOrder, StopOrder
from models import OrderType

class Portfolio:
    cashBalance: float
    stockMarketValue: float
    pendingOrdersMarketValue: float

    positions: [ibPosition]
    trades: [ibTrade]

    @property
    def cashAvailable(self):
        # TODO: Tenho que rever isto
        return max(self.cashBalance - self.stockMarketValue - self.pendingOrdersMarketValue - 400, 0)

        # GrossPositionValue - The sum of the absolute value of all stock and equity option positions
        # AvailableFunds - This value tells what you have available for trading
        # FullAvailableFunds - Available funds of whole portfolio with no discounts or intraday credits
        # TotalCashValue

        # AccruedCash — Total accrued cash value of stock, commodities and securities

    def __init__(self):
        self.positions = []
        self.trades = []
        self.cashBalance = 0
        self.totalCashBalance = 0
        self.totalCashBalanceLastUpdate = None

    # Account

    def updatePortfolio(self, ib: IB):
        # TODO: Validar se posso remover isto e a parte de baixo funciona
        # self.positions = self.parsePositons(ib)
        # self.trades = self.filterForCurrentOrders(ib)

        self.positions = ib.positions()
        self.trades = ib.openTrades()
        self.calcPositionsValue()
        self.calcOpenTradesValue()

        accountValues: [AccountValue] = ib.accountValues()
        account = [d for d in accountValues if d.tag == "AvailableFunds"].pop()
        self.cashBalance = float(account.value)

        currentDatetime = datetime.now()
        if (not self.totalCashBalanceLastUpdate or currentDatetime.date != self.totalCashBalanceLastUpdate.date):
            self.totalCashBalance = float(account.value)
            self.totalCashBalanceLastUpdate = currentDatetime
        print("💵 \nTotal Cash: %s \nCash Balance: %s \nAvailable Cash: %s \n💵\n" % (self.totalCashBalance, self.cashBalance, self.cashAvailable))

    def calcPositionsValue(self):
        totalValue = 0
        for item in self.positions:
            totalValue += item.avgCost * item.position        
        self.stockMarketValue = totalValue

    def calcOpenTradesValue(self):
        totalValue = 0
        for item in self.trades:
            if item.order.parentId == 0:
                totalValue += item.order.lmtPrice * item.order.totalQuantity
        self.pendingOrdersMarketValue = totalValue

    # Orders

    def canCreateOrder(self, ib: IB, contract: ibContract, order: ibOrder):
        hasOrder = len([d for d in self.trades if d.contract.symbol == contract.symbol]) > 0
        canCreate = (order.lmtPrice * order.totalQuantity) <= self.cashAvailable
        if (not canCreate and 
            not hasOrder):
            print("❗️Can't create Order!❗️\n❗️Cause: already created or insufficient cash: %.2f❗️\n" % self.cashAvailable) 
        return canCreate

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

    def createOrder(self, ib: IB, contract: ibContract, order: ibOrder, profitOrder: LimitOrder = None, stopLossOrder: StopOrder = None):
        ## self.orders.append(order) # TODO: Check if this is necessary

        if (not profitOrder and not stopLossOrder):
            limitOrder = LimitOrder(order.action, order.size, order.price)
            ib.placeOrder(stock, limitOrder)
        else:
            bracket = ib.bracketOrder(orderType, order.totalQuantity, order.lmtPrice, profitOrder.lmtPrice, stopLossOrder.auxPrice)

            for o in bracket:
                if ((isinstance(o, LimitOrder) and o.lmtPrice > 0) or
                    (isinstance(o, StopOrder) and o.auxPrice > 0)):
                    ib.placeOrder(contract, o)

        # TODO: Validar se o openTrades funciona tal como espero
        self.trades = ib.openTrades()
    
    def updateOrder(self, ib: IB, contract: ibContract, order: ibOrder, profitOrder: LimitOrder = None, stopLossOrder: StopOrder = None):
        o,p,s = self.getTradeOrders()
        if ((isinstance(o, LimitOrder) and o.lmtPrice != order.lmtPrice) or
            (isinstance(o, LimitOrder) and p.lmtPrice != profitOrder.lmtPrice) or
            (isinstance(s, StopOrder) and s.auxPrice != stopLossOrder.auxPrice)):
                self.createOrder(ib, contract, order, profitOrder, stopLossOrder)

    def cancelOrder(self, ib: IB, contract: ibContract):
        for trade in self.trades:
            if (trade.order.parentId == 0 and
                contract.symbol == trade.contract.symbol):
                ib.cancelOrder(trade.order)

    # Positions

    def getPosition(self, contract: ibContract):
        for position in self.positions:
            if position.contract.symbol == contract.symbol:
                return position
        return None
    
    def cancelPosition(self, ib: IB, orderType: OrderType, position: ibPosition):
        order = MarketOrder(orderType, position.size)
        ib.placeOrder(position.contract, order)