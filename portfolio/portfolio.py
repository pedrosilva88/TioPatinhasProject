from ib_insync import *
from order import Order, StockPosition

class Portfolio:
    cashBalance: float
    positions: [StockPosition]
    orders: [Order]

    def __init__(self):
        self.positions = []
        self.orders = []
        self.cashBalance = 0

    def updatePortfolio(self, ib: IB):
        self.positions = ib.positions()
        self.orders = ib.openOrders()
        accountValues: [AccountValue] = ib.accountValues()
        account = [d for d in accountValues if d.tag == "AvailableFunds"].pop()
        self.cashBalance = account.value
        print(self.cashBalance)
        print(self.positions)
        print(self.orders)

