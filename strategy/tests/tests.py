from datetime import *
from strategy import *
from ib_insync import Ticker as ibTicker, Contract as ibContract, Stock as ibStock, Position as ibPosition
from models import Order, OrderAction
from strategy import StrategyData, StrategyResult, StrategyResultType

def dummyTicker(datetime: datetime = datetime.combine(date.today(),time(14,30)), close=21, open=22.27, last=22.30, ask=22.34, bid=22.29, avVolume=10):
    contract = ibStock("DummyStock", "SMART", "USD")
    datetime = datetime.replace(microsecond=0)
    return ibTicker(contract=contract, time=datetime, close=close, open=open, last=last, ask=ask, bid=bid, avVolume=avVolume)

def dummyPosition(position: int=10, avgCost: float=5):
    contract = ibStock("DummyStock", "SMART", "USD")
    return ibPosition(account="", contract= contract, position=position, avgCost=avgCost)

def TestStrategyDataToShortWithAOpenPriceHigherThanLastPrice():
    print("Running Test to Short - OpenPrice < LastPrice")
    ticker = dummyTicker()
    data = StrategyData(ticker, None, None, 2000)
    strategy = StrategyOPG()
    result = strategy.run(data)

    if (result.type == StrategyResultType.Sell and
        result.order.action == OrderAction.Sell and
        result.order.totalQuantity == 17 and
        result.order.lmtPrice == 22.34 and
        result.order.takeProfitOrder.lmtPrice == 21.39 and
        result.order.stopLossOrder.auxPrice == 23.46):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataToShortWithAOpenPriceLowerThanLastPrice():
    print("Running Test to Short - OpenPrice > LastPrice")
    ticker = dummyTicker(open=22.27, ask=22.20, bid=22.16)
    data = StrategyData(ticker, None, None, 2000)

    strategy = StrategyOPG()
    result = strategy.run(data)

    if (result.type == StrategyResultType.Sell and
        result.order.action == OrderAction.Sell and
        result.order.totalQuantity == 18 and
        result.order.lmtPrice == 22.2 and
        result.order.takeProfitOrder.lmtPrice == 21.33 and
        result.order.stopLossOrder.auxPrice == 23.31):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataToLongWithAOpenPriceHigherThanLastPrice():
    print("Running Test to Long - OpenPrice > LastPrice")
    ticker = dummyTicker(close=30.74, open=28.45, last=29.20, ask=29.24, bid=29.20)
    data = StrategyData(ticker, None, None, 2000)

    strategy = StrategyOPG()
    result = strategy.run(data)

    if (result.type == StrategyResultType.Buy and
        result.order.action == OrderAction.Buy and
        result.order.totalQuantity == 13 and
        result.order.lmtPrice == 29.2 and
        result.order.takeProfitOrder.lmtPrice == 29.93 and
        result.order.stopLossOrder.auxPrice == 27.74):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataToLongWithAOpenPriceLowerThanLastPrice():
    print("Running Test to Long - OpenPrice < LastPrice")
    ticker = dummyTicker(close=30.74, open=28.45, last=28.30, ask=28.60, bid=28.30)
    data = StrategyData(ticker, None, None, 2000)

    strategy = StrategyOPG()
    result = strategy.run(data)

    if (result.type == StrategyResultType.Buy and
        result.order.action == OrderAction.Buy and
        result.order.totalQuantity == 14 and
        result.order.lmtPrice == 28.3 and
        result.order.takeProfitOrder.lmtPrice == 29.78 and
        result.order.stopLossOrder.auxPrice == 26.89):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataTooLateToRunThisStrategy():
    print("Running Test - Too late to run - (9:45)")
    dt = datetime.combine(date.today(),time(14,46))
    ticker = dummyTicker(datetime=dt)
    data = StrategyData(ticker, None, None, 2000)

    strategy = StrategyOPG()
    result = strategy.run(data)

    if (result.type == StrategyResultType.StrategyDateWindowExpired and
        result.order == None):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataForLongPositionForTimeout():
    print("Running Test - Long position - Time expired - (12:30)")

    dt = datetime.combine(date.today(),time(17,35))
    ticker = dummyTicker(datetime=dt)
    position = dummyPosition()
    data = StrategyData(ticker, position, None, 2000)

    strategy = StrategyOPG()
    result = strategy.run(data)

    if (result.type == StrategyResultType.PositionExpired_Sell and
        result.order == None):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataForShortPositionForTimeout():
    print("Running Test - Short position - Time expired - (12:30)")

    dt = datetime.combine(date.today(),time(17,35))
    ticker = dummyTicker(datetime=dt)
    position = dummyPosition(position=-10)
    data = StrategyData(ticker, position, None, 2000)

    strategy = StrategyOPG()
    result = strategy.run(data)

    if (result.type == StrategyResultType.PositionExpired_Buy and
        result.order == None):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataForShortPositionDoNothing():
    print("Running Test - Short position - Nothing to do")
    dt = datetime.combine(date.today(),time(16,35))
    ticker = dummyTicker(datetime=dt)
    position = dummyPosition(position=-10)
    data = StrategyData(ticker, position, None, 2000)

    strategy = StrategyOPG()
    result = strategy.run(data)

    if (result.type == StrategyResultType.KeepPosition and
        result.order == None):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataDateWindowExpiredWithoutPosition():
    print("Running Test - Date Window Expired - Nothing to do")
    dt = datetime.combine(date.today(),time(14,55))
    ticker = dummyTicker(datetime=dt)
    data = StrategyData(ticker, None, None, 2000)

    strategy = StrategyOPG()
    result = strategy.run(data)

    if (result.type == StrategyResultType.StrategyDateWindowExpired and
        result.order == None):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataWithDateWindowExpiredWithOrder():
    print("Running Test - Short order - Strategy time expired")
    dt = datetime.combine(date.today(),time(17,35))
    order = Order(OrderAction.Buy, OrderType.MarketOrder, -17, 2)
    ticker = dummyTicker(datetime=dt)
    data = StrategyData(ticker, None, order, 2000)

    strategy = StrategyOPG()
    result = strategy.run(data)

    if (result.type == StrategyResultType.StrategyDateWindowExpiredCancelOrder and
        not result.order == None):
        printTestSuccess()
    else:
        printTestFailure()

def printTestSuccess():
    print ("Test Succeeded ✅")

def printTestFailure():
    print ("Test Failed ❌")


## TODO TESTS
#   
#   * Tenho um order em curso para esta Stock, logo não devo correr a estratégia
