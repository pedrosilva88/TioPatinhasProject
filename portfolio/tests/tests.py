from ib_insync import IB, Order as ibOrder, Stock as ibStock
from portfolio import *

def runIB():
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=99)
    return ib

def TestPortfolioCreateBracketOrder():
    ib = runIB()
    portfolio = Portfolio()
    contract = ibStock("CABK", "SMART", "EUR")
    order = LimitOrder("BUY", 100, 2.47)
    profitOrder = LimitOrder("SELL", 100, 10)
    stopOrder = StopOrder("SELL", 100, 1.8)

    portfolio.createOrder(ib, contract, order, profitOrder, stopOrder)

    if len(portfolio.trades()) > 0:
        printTestSuccess()
    else:
        printTestFailure()

def TestPortfolioUpdateOrder():
    ib = runIB()
    portfolio = Portfolio()
    contract = ibStock("CABK", "SMART", "EUR")
    order = LimitOrder("BUY", 4, 2.46)
    profitOrder = LimitOrder("SELL", 4, 11)
    stopOrder = StopOrder("SELL", 4, 1.7)

    portfolio.createOrder(ib, contract, order, profitOrder, stopOrder)

    portfolio.updatePortfolio(ib)
    o, p, s = portfolio.getTradeOrders(contract)

    profit = Order(orderId=p.orderId, action=p.action, type=p.orderType, totalQuantity=p.totalQuantity, price=p.lmtPrice, parentId=o.orderId)
    stopLoss = Order(orderId=s.orderId, action=s.action, type=s.orderType,totalQuantity=s.totalQuantity,price=s.auxPrice,parentId=o.orderId)
    order = Order(orderId=o.orderId, action=o.action, type=o.orderType, totalQuantity=o.totalQuantity, price=o.lmtPrice, takeProfitOrder=profit, stopLossOrder=stopLoss)
    order.lmtPrice = 2.46
    order.takeProfitOrder.lmtPrice = 11
    order.stopLossOrder.auxPrice = 1.7

    portfolio.updateOrder(ib, contract, order, order.takeProfitOrder, order.stopLossOrder)

    if len(portfolio.trades()) > 0:
        printTestSuccess()
    else:
        printTestFailure()

def TestPortfolioCancelOrder():
    ib = runIB()
    portfolio = Portfolio()
    contract = ibStock("CABK", "SMART", "EUR")
    portfolio.cancelOrder(ib, contract)

    if len(portfolio.trades()) == 0:
        printTestSuccess()
    else:
        printTestFailure()

def printTestSuccess():
    print ("Test Succeeded ✅")

def printTestFailure():
    print ("Test Failed ❌")


from ib_insync import IB, Order as ibOrder, Stock as ibStock, MarketOrder
from portfolio import *
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=3)
portfolio = Portfolio()
contract = ibStock("SAN1", "SMART", "EUR")
order = MarketOrder("SELL", 10)
profitOrder = LimitOrder("BUY", 10, 1)
stopOrder = StopOrder("BUY", 10, 10)
portfolio.createOrder(ib, contract, order, profitOrder, stopOrder)