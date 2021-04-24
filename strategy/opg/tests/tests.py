from datetime import *
from strategy import *
from ib_insync import Ticker as ibTicker, Contract as ibContract, Stock as ibStock, Position as ibPosition
from models import Order, OrderAction
from strategy import StrategyData, StrategyResult, StrategyResultType, getStrategyConfigFor, StrategyConfig
from country_config import getConfigFor, CountryKey
from helpers import utcToLocal

def dummyTicker(datetime: datetime = datetime.combine(date.today(),time(9,31)), close=21, open=22.27, last=22.30, ask=22.34, bid=22.29, avVolume=1):
    contract = ibStock("DummyStock", "SMART", "USD")
    countryConfig = getConfigFor(key=CountryKey.USA)
    datetime = datetime.replace(microsecond=0, tzinfo=countryConfig.timezone)
    return ibTicker(contract=contract, time=datetime, close=close, open=open, last=last, ask=ask, bid=bid, avVolume=avVolume)

def dummyPosition(position: int=10, avgCost: float=5):
    contract = ibStock("DummyStock", "SMART", "USD")
    return ibPosition(account="", contract= contract, position=position, avgCost=avgCost)

def TestStrategyDataToShortWithAOpenPriceHigherThanLastPrice():
    print("Running Test to Short - OpenPrice < LastPrice")
    ticker = dummyTicker()
    countryConfig = getConfigFor(key=CountryKey.USA)
    strategyConfig = getStrategyConfigFor(key=CountryKey.USA, timezone=countryConfig.timezone)
    data = StrategyData(ticker, None, None, 2000, 1, 1)
    strategy = StrategyOPG()
    result = strategy.run(data, strategyConfig, countryConfig)

    if (result.type == StrategyResultType.Sell and
        result.order.action == OrderAction.Sell and
        result.order.totalQuantity == 44 and
        result.order.lmtPrice == 22.34 and
        result.order.takeProfitOrder.lmtPrice == 21.33 and
        result.order.stopLossOrder.auxPrice == 24.13):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataToShortWithAOpenPriceLowerThanLastPrice():
    print("Running Test to Short - OpenPrice > LastPrice")
    ticker = dummyTicker(open=22.27, ask=22.20, bid=22.16)
    countryConfig = getConfigFor(key=CountryKey.USA)
    strategyConfig = getStrategyConfigFor(key=CountryKey.USA, timezone=countryConfig.timezone)
    data = StrategyData(ticker, None, None, 2000, 1, 1)

    strategy = StrategyOPG()
    result = strategy.run(data, strategyConfig, countryConfig)

    if (result.type == StrategyResultType.Sell and
        result.order.action == OrderAction.Sell and
        result.order.totalQuantity == 45 and
        result.order.lmtPrice == 22.2 and
        result.order.takeProfitOrder.lmtPrice == 21.26 and
        result.order.stopLossOrder.auxPrice == 23.98):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataToLongWithAOpenPriceHigherThanLastPrice():
    print("Running Test to Long - OpenPrice > LastPrice")
    ticker = dummyTicker(close=30.74, open=28.45, last=29.20, ask=29.24, bid=29.20)
    countryConfig = getConfigFor(key=CountryKey.USA)
    strategyConfig = getStrategyConfigFor(key=CountryKey.USA, timezone=countryConfig.timezone)
    data = StrategyData(ticker, None, None, 2000, 1, 1)

    strategy = StrategyOPG()
    result = strategy.run(data, strategyConfig, countryConfig)

    if (result.type == StrategyResultType.Buy and
        result.order.action == OrderAction.Buy and
        result.order.totalQuantity == 34 and
        result.order.lmtPrice == 29.2 and
        result.order.takeProfitOrder.lmtPrice == 30.04 and
        result.order.stopLossOrder.auxPrice == 26.86):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataToLongWithAOpenPriceLowerThanLastPrice():
    print("Running Test to Long - OpenPrice < LastPrice")
    ticker = dummyTicker(close=30.74, open=28.45, last=28.30, ask=28.60, bid=28.30)
    countryConfig = getConfigFor(key=CountryKey.USA)
    strategyConfig = getStrategyConfigFor(key=CountryKey.USA, timezone=countryConfig.timezone)
    data = StrategyData(ticker, None, None, 2000, 1, 1)

    strategy = StrategyOPG()
    result = strategy.run(data, strategyConfig, countryConfig)

    if (result.type == StrategyResultType.Buy and
        result.order.action == OrderAction.Buy and
        result.order.totalQuantity == 35 and
        result.order.lmtPrice == 28.3 and
        result.order.takeProfitOrder.lmtPrice == 29.88 and
        result.order.stopLossOrder.auxPrice == 26.04):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataTooLateToRunThisStrategy():
    print("Running Test - Too late to run - (9:45)")
    dt = datetime.combine(date.today(),time(9,46))
    countryConfig = getConfigFor(key=CountryKey.USA)
    strategyConfig = getStrategyConfigFor(key=CountryKey.USA, timezone=countryConfig.timezone)
    ticker = dummyTicker(datetime=dt)
    data = StrategyData(ticker, None, None, 2000, 1, 1)

    strategy = StrategyOPG()
    result = strategy.run(data, strategyConfig, countryConfig)

    if (result.type == StrategyResultType.StrategyDateWindowExpired and
        result.order == None):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataForLongPositionForTimeout():
    print("Running Test - Long position - Time expired - (14:35)")

    dt = datetime.combine(date.today(),time(14,35))
    countryConfig = getConfigFor(key=CountryKey.USA)
    strategyConfig = getStrategyConfigFor(key=CountryKey.USA, timezone=countryConfig.timezone)
    ticker = dummyTicker(datetime=dt)
    position = dummyPosition()
    data = StrategyData(ticker, position, None, 2000, 1, 1)

    strategy = StrategyOPG()
    result = strategy.run(data, strategyConfig, countryConfig)

    if (result.type == StrategyResultType.PositionExpired_Sell and
        result.order == None):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataForShortPositionForTimeout():
    print("Running Test - Short position - Time expired - (14:30)")

    dt = datetime.combine(date.today(),time(14,35))
    countryConfig = getConfigFor(key=CountryKey.USA)
    strategyConfig = getStrategyConfigFor(key=CountryKey.USA, timezone=countryConfig.timezone)
    ticker = dummyTicker(datetime=dt)
    position = dummyPosition(position=-10)
    data = StrategyData(ticker, position, None, 2000, 1, 1)

    strategy = StrategyOPG()
    result = strategy.run(data, strategyConfig, countryConfig)

    if (result.type == StrategyResultType.PositionExpired_Buy and
        result.order == None):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataForShortPositionDoNothing():
    print("Running Test - Short position - Nothing to do")
    dt = datetime.combine(date.today(),time(11,35))
    countryConfig = getConfigFor(key=CountryKey.USA)
    strategyConfig = getStrategyConfigFor(key=CountryKey.USA, timezone=countryConfig.timezone)
    ticker = dummyTicker(datetime=dt)
    position = dummyPosition(position=-10)
    data = StrategyData(ticker, position, None, 2000, 1, 1)

    strategy = StrategyOPG()
    result = strategy.run(data, strategyConfig, countryConfig)

    if (result.type == StrategyResultType.KeepPosition and
        result.order == None):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataDateWindowExpiredWithoutPosition():
    print("Running Test - Date Window Expired - Nothing to do")
    dt = datetime.combine(date.today(),time(9,55))
    countryConfig = getConfigFor(key=CountryKey.USA)
    strategyConfig = getStrategyConfigFor(key=CountryKey.USA, timezone=countryConfig.timezone)
    ticker = dummyTicker(datetime=dt)
    data = StrategyData(ticker, None, None, 2000, 1, 1)

    strategy = StrategyOPG()
    result = strategy.run(data, strategyConfig, countryConfig)

    if (result.type == StrategyResultType.StrategyDateWindowExpired and
        result.order == None):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataWithDateWindowExpiredWithOrder():
    print("Running Test - Short order - Strategy time expired")
    dt = datetime.combine(date.today(),time(14,1))
    countryConfig = getConfigFor(key=CountryKey.USA)
    strategyConfig = getStrategyConfigFor(key=CountryKey.USA, timezone=countryConfig.timezone)
    takeProfitOrder = Order(OrderAction.Buy, OrderType.LimitOrder, -17, 2.1)
    stopLossOrder = Order(OrderAction.Buy, OrderType.StopOrder, -17, 2.1)
    order = Order(OrderAction.Buy, OrderType.LimitOrder, -17, 2, 1, takeProfitOrder, stopLossOrder)
    ticker = dummyTicker(datetime=dt)
    data = StrategyData(ticker, None, order, 2000, 1, 1)

    strategy = StrategyOPG()
    result = strategy.run(data, strategyConfig, countryConfig)

    if (result.type == StrategyResultType.StrategyDateWindowExpiredCancelOrder and
        not result.order == None):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataWithOrderNeedsToBeUpdated():
    print("Running Test - Receive Ticker to create Long Order - then - Ticker with a higher bid")
    dt = datetime.combine(date.today(),time(9,31,5))
    countryConfig = getConfigFor(key=CountryKey.USA)
    strategyConfig = getStrategyConfigFor(key=CountryKey.USA, timezone=countryConfig.timezone)
    ticker = dummyTicker(datetime=dt, close=5.3, open=5, last=5.1, ask=5.2, bid=5.1)
    data = StrategyData(ticker, None, None, 2000, 1, 1)

    strategy = StrategyOPG()
    result = strategy.run(data, strategyConfig, countryConfig)
    isStepValid_1 = False

    if (result.type == StrategyResultType.Buy and 
        result.order and
        result.order.action == OrderAction.Buy and
        result.order.totalQuantity == 196 and
        result.order.lmtPrice == 5.1 and
        result.order.takeProfitOrder.lmtPrice == 5.21 and
        result.order.stopLossOrder.auxPrice == 4.69):
        isStepValid_1 = True

    dt = datetime.combine(date.today(),time(9,30,8))
    order = result.order
    ticker = dummyTicker(datetime=dt, close=5.3, open=5, last=5.1, ask=5.2, bid=5.14)
    data = StrategyData(ticker, None, order, 2000, 1, 1)
    result = strategy.run(data, strategyConfig, countryConfig)

    if (result.type == StrategyResultType.KeepOrder and 
        result.order and
        result.order.action == OrderAction.Buy and
        result.order.totalQuantity == 194 and
        result.order.lmtPrice == 5.14 and
        result.order.takeProfitOrder.lmtPrice == 5.21 and
        result.order.stopLossOrder.auxPrice == 4.73 and
        isStepValid_1):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataForSizeLowerThan2Shares():
    #print("Running Test to Short - OpenPrice > LastPrice")
    ticker = dummyTicker(close=2221, open=2110.27, last=2110.27, ask=2110.27, bid=2110.27, avVolume=1)
    countryConfig = getConfigFor(key=CountryKey.USA)
    strategyConfig = getStrategyConfigFor(key=CountryKey.USA, timezone=countryConfig.timezone)
    data = StrategyData(ticker, None, None, 2000, 1, 1)

    strategy = StrategyOPG()
    result = strategy.run(data, strategyConfig, countryConfig)

    if (result.type == StrategyResultType.Buy and
        result.order.action == OrderAction.Buy and
        result.order.totalQuantity == 0 and
        result.order.lmtPrice == 2110.27 and
        result.order.takeProfitOrder.lmtPrice == 2189.18 and
        result.order.stopLossOrder.auxPrice == 1941.45):
        printTestSuccess()
    else:
        printTestFailure()

# def TestStrategyDataForSome():
#     #print("Running Test to Short - OpenPrice > LastPrice")
#     ticker = dummyTicker(close=2221, open=None, last=2110.27, ask=2110.27, bid=2110.27, avVolume=1)
#     countryConfig = getConfigFor(key=CountryKey.USA)
#     strategyConfig = getStrategyConfigFor(key=CountryKey.USA, timezone=countryConfig.timezone)
#     data = StrategyData(ticker, None, None, 2000, 1, 1)

#     strategy = StrategyOPG()
#     result = strategy.run(data, strategyConfig, countryConfig)

#     print(result)
#     if (result.type == StrategyResultType.Buy and
#         result.order.action == OrderAction.Buy and
#         result.order.totalQuantity == 0 and
#         result.order.lmtPrice == 2110.27 and
#         result.order.takeProfitOrder.lmtPrice == 2189.18 and
#         result.order.stopLossOrder.auxPrice == 1941.45):
#         printTestSuccess()
#     else:
#         printTestFailure()

# def TestStrategyDataForSome2():
#     #print("Running Test to Short - OpenPrice > LastPrice")
#     ticker = dummyTicker(close=None, open=2110.27, last=2110.27, ask=2110.27, bid=2110.27, avVolume=1)
#     countryConfig = getConfigFor(key=CountryKey.USA)
#     strategyConfig = getStrategyConfigFor(key=CountryKey.USA, timezone=countryConfig.timezone)
#     data = StrategyData(ticker, None, None, 2000, 1, 1)

#     strategy = StrategyOPG()
#     result = strategy.run(data, strategyConfig, countryConfig)

#     print(result)
#     if (result.type == StrategyResultType.Buy and
#         result.order.action == OrderAction.Buy and
#         result.order.totalQuantity == 0 and
#         result.order.lmtPrice == 2110.27 and
#         result.order.takeProfitOrder.lmtPrice == 2189.18 and
#         result.order.stopLossOrder.auxPrice == 1941.45):
#         printTestSuccess()
#     else:
#         printTestFailure()

# def TestStrategyDataForSome3():
#     #print("Running Test to Short - OpenPrice > LastPrice")
#     ticker = dummyTicker(close=2221, open=2110.27, last=None, ask=2110.27, bid=2110.27, avVolume=1)
#     countryConfig = getConfigFor(key=CountryKey.USA)
#     strategyConfig = getStrategyConfigFor(key=CountryKey.USA, timezone=countryConfig.timezone)
#     data = StrategyData(ticker, None, None, 2000, 1, 1)

#     strategy = StrategyOPG()
#     result = strategy.run(data, strategyConfig, countryConfig)

#     print(result)
#     if (result.type == StrategyResultType.Buy and
#         result.order.action == OrderAction.Buy and
#         result.order.totalQuantity == 0 and
#         result.order.lmtPrice == 2110.27 and
#         result.order.takeProfitOrder.lmtPrice == 2189.18 and
#         result.order.stopLossOrder.auxPrice == 1941.45):
#         printTestSuccess()
#     else:
#         printTestFailure()


# def TestStrategyDataForSome4():
#     #print("Running Test to Short - OpenPrice > LastPrice")
#     ticker = dummyTicker(close=2221, open=2110.27, last=2110.27, ask=None, bid=2110.27, avVolume=1)
#     countryConfig = getConfigFor(key=CountryKey.USA)
#     strategyConfig = getStrategyConfigFor(key=CountryKey.USA, timezone=countryConfig.timezone)
#     data = StrategyData(ticker, None, None, 2000, 1, 1)

#     strategy = StrategyOPG()
#     result = strategy.run(data, strategyConfig, countryConfig)

#     print(result)
#     if (result.type == StrategyResultType.Buy and
#         result.order.action == OrderAction.Buy and
#         result.order.totalQuantity == 0 and
#         result.order.lmtPrice == 2110.27 and
#         result.order.takeProfitOrder.lmtPrice == 2189.18 and
#         result.order.stopLossOrder.auxPrice == 1941.45):
#         printTestSuccess()
#     else:
#         printTestFailure()

def printTestSuccess():
    print ("Test Succeeded ✅")

def printTestFailure():
    print ("Test Failed ❌")
