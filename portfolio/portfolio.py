from country_config.models import Market
from provider_factory.models import ProviderClient
from models.base_models import BracketOrder, Contract, Order, Position, Trade
from typing import List
from models import OrderAction
from helpers import log

class Portfolio:
    cashBalance: float
    pendingOrdersMarketValue: float

    exchangeUSDRate: float = 1

    positions: List[Position]
    trades: List[Trade]

    @property
    def cashAvailable(self):
        return max(self.cashBalance - self.pendingOrdersMarketValue, 0)

    def __init__(self):
        self.positions = []
        self.trades = []
        self.cashBalance = 0
        self.totalCashBalance = 0
        self.totalCashBalanceLastUpdate = None

    # Account

    def updatePortfolio(self, client: ProviderClient, market: Market):
        self.positions = client.positions()
        self.trades = client.orders()
        self.cashBalance = client.cashBalance()
        self.exchangeUSDRate = client.currencyRateFor(market.country.currency)

        self.calcOpenTradesValue()
        log("💵 \nCash Balance: %s \nAvailable Cash: %s \n💵\n" % (self.cashBalance, self.cashAvailable))

    def calcOpenTradesValue(self):
        totalValue = 0
        for trade in self.trades:
            if trade.order.parentId == 0:
                totalValue += (trade.order.price * self.exchangeUSDRate) * abs(trade.order.size)
        self.pendingOrdersMarketValue = totalValue

    # Orders

    def canCreateOrder(self, contract: Contract, bracketOrder: BracketOrder):
        order = bracketOrder.parentOrder
        hasOrder = len([d for d in self.trades if d.contract.symbol == contract.symbol]) > 0
        canCreate = (order.price * order.size) <= self.cashAvailable
        if (not canCreate and 
            not hasOrder):
            log("❗️Can't create Order!❗️\n❗️Cause: already created or insufficient cash: %.2f❗️\n" % self.cashAvailable) 
        return canCreate

    def createOrder(self, ib: IB, contract: ibContract, order: ibOrder, profitOrder: LimitOrder = None, stopLossOrder: StopOrder = None):
        if (not profitOrder and not stopLossOrder):
            limitOrder = LimitOrder(order.action, order.totalQuantity, order.lmtPrice)
            ib.placeOrder(contract, limitOrder)
        else:
            if order.orderType == "MKT" or order.orderType == "MIDPRICE":
                assert order.action in ('BUY', 'SELL')
                reverseAction = 'BUY' if order.action == 'SELL' else 'SELL'
                parent = Order(
                    action=order.action, totalQuantity=order.totalQuantity,
                    orderId=ib.client.getReqId(),
                    orderType="MKT",
                    transmit=False)
                takeProfit = LimitOrder(reverseAction, profitOrder.totalQuantity, profitOrder.lmtPrice,
                                        orderId=ib.client.getReqId(),
                                        tif="GTC",
                                        transmit=False,
                                        parentId=parent.orderId)
                stopLoss = StopOrder(
                    reverseAction, stopLossOrder.totalQuantity, stopLossOrder.auxPrice,
                    orderId=ib.client.getReqId(),
                    tif="GTC",
                    transmit=True,
                    parentId=parent.orderId)

                bracket = BracketOrder(parent, takeProfit, stopLoss)
                for o in bracket:
                    ib.placeOrder(contract, o)
            else:
                bracket = ib.bracketOrder(order.action, order.totalQuantity, order.lmtPrice, profitOrder.lmtPrice, stopLossOrder.auxPrice)

                for o in bracket:
                    if ((isinstance(o, LimitOrder) and o.lmtPrice > 0) or
                        (isinstance(o, StopOrder) and o.auxPrice > 0)):
                        ib.placeOrder(contract, o)

        ib.reqAllOpenOrdersAsync()
        self.updatePortfolio(ib)
    
    def updateOrder(self, ib: IB, contract: ibContract, order: ibOrder, profitOrder: LimitOrder = None, stopLossOrder: StopOrder = None):
        o,p,s = self.getTradeOrders(contract)
        if ((isinstance(o, LimitOrder) or (isinstance(o, ibOrder) and o.lmtPrice > 0)) and o.lmtPrice != order.lmtPrice):
            ib.placeOrder(contract, order)
        if ((isinstance(p, LimitOrder) or (isinstance(p, ibOrder) and p.lmtPrice > 0)) and p.lmtPrice != profitOrder.lmtPrice):
            ib.placeOrder(contract, profitOrder)
        if ((isinstance(s, StopOrder) or (isinstance(s, ibOrder) and s.auxPrice > 0)) and s.auxPrice != stopLossOrder.auxPrice):
            ib.placeOrder(contract, stopLossOrder)
                
    def cancelOrder(self, ib: IB, contract: ibContract):
        log("🥊  Cancel Orders - %s 🥊" % contract.symbol)
        for trade in self.trades:
            if contract.symbol == trade.contract.symbol:
                log("🥊  Cancel Order - %s - %s - %s 🥊" % (trade.contract.symbol, trade.order.orderType, trade.orderStatus.status))
                ib.cancelOrder(trade.order)

    # Positions

    def getPosition(self, contract: ibContract):
        for position in self.positions:
            if position.contract.symbol == contract.symbol:
                return position
        return None
    
    def cancelPosition(self, ib: IB, orderAction: OrderAction, position: ibPosition):
        stock = Stock(position.contract.symbol, "SMART", position.contract.currency)
        order = MarketOrder(orderAction, abs(position.position))
        
        self.cancelOrder(ib, stock)
        ib.placeOrder(stock, order)        