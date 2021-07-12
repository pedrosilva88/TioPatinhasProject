from provider_factory.models import ProviderConfigs
from provider_factory.TWS.models import TWSClient
from models.base_models import Order, OrderType, Contract
from ib_insync import IB
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


from ib_insync import IB
from portfolio import *
from provider_factory.models import ProviderConfigs
from provider_factory.TWS.models import TWSClient
from models.base_models import Order, OrderType, Contract
from country_config.market_manager import MarketManager

portfolio = Portfolio()
market = MarketManager.getMarketFor(Country.USA)
contract = Contract("CABK", Country.Spain)
order = Order(OrderAction.Buy, OrderType.LimitOrder, 5, 1.4)
profitOrder = Order(OrderAction.Sell, OrderType.LimitOrder, 5, 10)
stopOrder = Order(OrderAction.Sell, OrderType.StopOrder, 5, 1)
bracketOrder = BracketOrder(order, profitOrder, stopOrder)
providerConfigs = ProviderConfigs(version="981",
                                tradingMode="paper",
                                user="silvap088", 
                                password="pedro&IB+88",
                                endpoint="127.0.0.1",
                                port="7497",
                                clientID="8",
                                connectTimeout=45,
                                appStartupTime=35,
                                appTimeout=45,
                                readOnly=False,
                                useController=True)
client = TWSClient(providerConfigs)
client.connect()
portfolio.createOrder(client, contract, bracketOrder)


client.session.reqPositions()
portfolio.updatePortfolio(client, market)
portfolio.cancelOrder(client, contract)
portfolio.updatePortfolio(client, market)
client.session.reqPositions()
position= portfolio.getPosition(contract)
portfolio.cancelPosition(client, OrderAction.Sell, position)

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