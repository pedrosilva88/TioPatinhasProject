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
contract = ibStock("AAPL", "SMART", "USD")
order = MarketOrder("SELL", 10)

profitOrder = LimitOrder("BUY", 10, 10)
stopOrder = StopOrder("BUY", 10, 180)
portfolio.createOrder(ib, contract, order, profitOrder, stopOrder)

#order = ibOrder(action="SELL", orderType="MIDPRICE", totalQuantity=10)



#Test handle Fill
from ib_insync import Position, Contract, Ticker
from country_config.country_config import CountryConfig, CountryKey, getConfigFor
from strategy.strategy_data import StrategyData
from strategy.zigzag.strategy_zigzag import StrategyZigZag
from datetime import date, datetime
from database import FillDB
fill = FillDB('AAPL', date(2021,6,1))
tick = Ticker(Contract('AAPL', 'SMART', 'USD'))
position = Position('', Contract('AAPL', 'SMART', 'USD'), 100, 10)
data = StrategyData(tick, position, None, None, None, None, None, None, None, fill, date(2021,6,1), datetime(2021,6,1,18,59,59))
#data = StrategyData(tick, position, None, None, None, None, None, None, None, fill, date(2021,6,1), datetime(2021,6,1,18,30))
countryConfig = getConfigFor(CountryKey.USA)
object = StrategyZigZag()
object.strategyData = data
object.countryConfig = countryConfig
object.handleFill()