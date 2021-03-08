from datetime import datetime
from ib_insync import IB, Order as ibOrder, Position as ibPosition, Trade as ibTrade, Contract as ibContract, LimitOrder, StopOrder
from models import OrderType

class Portfolio:
    cashBalance: float
    grossPositionsValue: float
    pendingOrdersMarketValue: float

    exchangeUSDRate: float = 1

    positions: [ibPosition]
    trades: [ibTrade]

    @property
    def cashAvailable(self):
        return max(self.cashBalance - self.grossPositionsValue - self.pendingOrdersMarketValue - 400, 0)

    def __init__(self):
        self.positions = []
        self.trades = []
        self.cashBalance = 0
        self.totalCashBalance = 0
        self.totalCashBalanceLastUpdate = None

    # Account

    def updatePortfolio(self, ib: IB):
        self.positions = ib.positions()
        self.trades = ib.openTrades()

        for account in ib.accountValues():
            if account.tag == "AvailableFunds":
                self.cashBalance = float(account.value)
            elif account.tag == "GrossPositionValue":
                self.grossPositionsValue = float(account.value)
            elif (account.tag == "ExchangeRate" and account.currency == "USD"):
                self.exchangeUSDRate = float(account.value)

        self.calcOpenTradesValue()
        currentDatetime = datetime.now()
        if (not self.totalCashBalanceLastUpdate or currentDatetime.date != self.totalCashBalanceLastUpdate.date):
            self.totalCashBalance = float(self.cashBalance)
            self.totalCashBalanceLastUpdate = currentDatetime
        print("💵 \nTotal Cash: %s \nCash Balance: %s \nAvailable Cash: %s \n💵\n" % (self.totalCashBalance, self.cashBalance, self.cashAvailable))

    def calcOpenTradesValue(self):
        totalValue = 0
        for item in self.trades:
            if item.order.parentId == 0:
                totalValue += (item.order.lmtPrice * self.exchangeUSDRate) * abs(item.order.totalQuantity)
        self.pendingOrdersMarketValue = totalValue

    # Orders

    def canCreateOrder(self, ib: IB, contract: ibContract, order: ibOrder):
        #today = datetime.now() TODO: Tenho que validar se esta trade pertence ao dia de hoje
        hasOrder = len([d for d in ib.trades() if d.contract.symbol == contract.symbol]) > 0
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
                if (isinstance(order, LimitOrder) or (isinstance(order, ibOrder) and order.lmtPrice > 0)) and order.parentId == 0:
                    mainOrder = order
                elif (isinstance(order, LimitOrder) or (isinstance(order, ibOrder) and order.orderType ==
                OrderType.LimitOrder.value)) and order.parentId > 0:
                    profitOrder = order
                elif (isinstance(order, StopOrder) or (isinstance(order, ibOrder) and order.orderType == OrderType.StopOrder.value)) and order.parentId > 0:
                    stopLossOrder = order
        return mainOrder, profitOrder, stopLossOrder

    def createOrder(self, ib: IB, contract: ibContract, order: ibOrder, profitOrder: LimitOrder = None, stopLossOrder: StopOrder = None):
        if (not profitOrder and not stopLossOrder):
            limitOrder = LimitOrder(order.action, order.totalQuantity, order.lmtPrice)
            ib.placeOrder(contract, limitOrder)
        else:
            bracket = ib.bracketOrder(order.action, order.totalQuantity, order.lmtPrice, profitOrder.lmtPrice, stopLossOrder.auxPrice)

            for o in bracket:
                if ((isinstance(o, LimitOrder) and o.lmtPrice > 0) or
                    (isinstance(o, StopOrder) and o.auxPrice > 0)):
                    ib.placeOrder(contract, o)

        self.trades = ib.openTrades()
    
    def updateOrder(self, ib: IB, contract: ibContract, order: ibOrder, profitOrder: LimitOrder = None, stopLossOrder: StopOrder = None):
        o,p,s = self.getTradeOrders(contract)
        if ((isinstance(o, LimitOrder) or (isinstance(o, ibOrder) and o.lmtPrice > 0)) and o.lmtPrice != order.lmtPrice):
            ib.placeOrder(contract, order)
        if ((isinstance(p, LimitOrder) or (isinstance(p, ibOrder) and p.lmtPrice > 0)) and p.lmtPrice != profitOrder.lmtPrice):
            ib.placeOrder(contract, profitOrder)
        if ((isinstance(s, StopOrder) or (isinstance(s, ibOrder) and s.auxPrice > 0)) and s.auxPrice != stopLossOrder.auxPrice):
            ib.placeOrder(contract, stopLossOrder)
                
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