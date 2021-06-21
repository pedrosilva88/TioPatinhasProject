from country_config.models import Market
from provider_factory.models import ProviderClient
from models.base_models import BracketOrder, Contract, Position, Trade
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
        self.pendingOrdersMarketValue = 0

    # Account

    def updatePortfolio(self, client: ProviderClient, market: Market):
        self.positions = client.positions()
        self.trades = client.trades()
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

    def createOrder(self, client: ProviderClient, contract: Contract, bracketOrder: BracketOrder):
        client.createOrder(contract, bracketOrder)
                
    def cancelOrder(self, client: ProviderClient, contract: Contract):
        log("🥊  Cancel Orders - %s 🥊" % contract.symbol)
        for trade in self.trades:
            if contract.symbol == trade.contract.symbol:
                log("🥊  Cancel Order - %s - %s 🥊" % (trade.contract.symbol, trade.order.type.value))
                client.cancelOrder(trade.order)

    # Positions

    def getPosition(self, contract: Contract):
        for position in self.positions:
            if position.contract.symbol == contract.symbol:
                return position
        return None
    
    def cancelPosition(self, client: ProviderClient, action: OrderAction, position: Position):
        self.cancelOrder(client, position.contract)
        client.cancelPosition(action, position)