
# TODO: Testar o updateOrder

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
    order = LimitOrder("BUY", 10, 1)
    profitOrder = LimitOrder("Sell", 10, 1.5)
    stopOrder = StopOrder("Sell", 10, 0.8)

    portfolio.createOrder(ib, contract, order, profitOrder, stopOrder)

    if len(portfolio.trades()) > 0:
        printTestSuccess()
    else:
        printTestFailure()

def TestPortfolioUpdateOrder():
    ib = runIB()
    portfolio = Portfolio()

    if len(portfolio.trades()) > 0:
        printTestSuccess()
    else:
        printTestFailure()

def printTestSuccess():
    print ("Test Succeeded ✅")

def printTestFailure():
    print ("Test Failed ❌")
