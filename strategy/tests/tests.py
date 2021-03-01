from datetime import *
from strategy import *

def TestStrategyDataToShortWithAOpenPriceHigherThanLastPrice():
    print("Running Test to Short - OpenPrice > LastPrice")
    dt = datetime.combine(date.today(),time(9,30))
    data = StrategyData('DummyStock', dt, 21, 22.27, 22.30, None, None)
    strategy = StrategyOPG()
    result = strategy.run(data)

    if (result.type == StrategyResultType.Sell and
        result.order.type == OrderType.Short and
        result.order.size == 17 and
        result.order.price == 22.3 and
        result.order.takeProfitPrice == 21.36 and
        result.order.stopLossPrice == 23.41):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataToShortWithAOpenPriceLowerThanLastPrice():
    print("Running Test to Short - OpenPrice < LastPrice")
    dt = datetime.combine(date.today(),time(9,30))
    data = StrategyData('DummyStock', dt, 21, 22.27, 22.20, None, None)
    strategy = StrategyOPG()
    result = strategy.run(data)

    if (result.type == StrategyResultType.Sell and
        result.order.type == OrderType.Short and
        result.order.size == 18 and
        result.order.price == 22.2 and
        result.order.takeProfitPrice == 21.33 and
        result.order.stopLossPrice == 23.31):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataToLongWithAOpenPriceHigherThanLastPrice():
    print("Running Test to Long - OpenPrice > LastPrice")
    dt = datetime.combine(date.today(),time(9,30))
    data = StrategyData('DummyStock', dt, 30.74, 28.45, 29.20, None, None)
    strategy = StrategyOPG()
    result = strategy.run(data)

    if (result.type == StrategyResultType.Buy and
        result.order.type == OrderType.Long and
        result.order.size == 13 and
        result.order.price == 29.2 and
        result.order.takeProfitPrice == 29.93 and
        result.order.stopLossPrice == 27.74):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataToLongWithAOpenPriceLowerThanLastPrice():
    print("Running Test to Long - OpenPrice < LastPrice")
    dt = datetime.combine(date.today(),time(9,30))
    data = StrategyData('DummyStock', dt, 30.74, 28.45, 28.30, None, None)
    strategy = StrategyOPG()
    result = strategy.run(data)

    if (result.type == StrategyResultType.Buy and
        result.order.type == OrderType.Long and
        result.order.size == 14 and
        result.order.price == 28.3 and
        result.order.takeProfitPrice == 29.78 and
        result.order.stopLossPrice == 26.89):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataTooLateToRunThisStrategy():
    print("Running Test - Too late to run - (9:45)")
    dt = datetime.combine(date.today(),time(9,46))
    data = StrategyData('DummyStock', dt, 30.74, 28.45, 28.30, None, None)
    strategy = StrategyOPG()
    result = strategy.run(data)

    if (result.type == StrategyResultType.StrategyDateWindowExpired and
        result.order == None):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataForLongPositionForTimeout():
    print("Running Test - Long position - Time expired - (12:30)")
    dt = datetime.combine(date.today(),time(12,35))
    dtBought = datetime.combine(date.today(),time(9,32))
    position = StockPosition('DummyStock', 28.30, dtBought, 14, OrderType.Long)
    data = StrategyData('DummyStock', dt, 30.74, 28.45, 28.30, position, None)
    strategy = StrategyOPG()
    result = strategy.run(data)

    print(result.type)
    if (result.type == StrategyResultType.PositionExpired_Sell and
        result.order == None):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataForShortPositionForTimeout():
    print("Running Test - Short position - Time expired - (12:30)")
    dt = datetime.combine(date.today(),time(12,35))
    dtBought = datetime.combine(date.today(),time(9,32))
    position = StockPosition('DummyStock', 28.30, dtBought, 14, OrderType.Short)
    data = StrategyData('DummyStock', dt, 21, 22.27, 22.30, position, None)
    strategy = StrategyOPG()
    result = strategy.run(data)

    print(result.type)
    if (result.type == StrategyResultType.PositionExpired_Buy and
        result.order == None):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataForShortPositionDoNothing():
    print("Running Test - Short position - Nothing to do")
    dt = datetime.combine(date.today(),time(11,35))
    dtBought = datetime.combine(date.today(),time(9,32))
    position = StockPosition('DummyStock', 28.30, dtBought, 14, OrderType.Short)
    data = StrategyData('DummyStock', dt, 21, 22.27, 22.30, position, None)
    strategy = StrategyOPG()
    result = strategy.run(data)

    print(result.type)
    if (result.type == StrategyResultType.KeepPosition and
        result.order == None):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataDateWindowExpiredWithoutPosition():
    print("Running Test - Short position - Nothing to do")
    dt = datetime.combine(date.today(),time(12,35))
    data = StrategyData('DummyStock', dt, 21, 22.27, 22.30, None, None)
    strategy = StrategyOPG()
    result = strategy.run(data)

    if (result.type == StrategyResultType.StrategyDateWindowExpired and
        result.order == None):
        printTestSuccess()
    else:
        printTestFailure()

def TestStrategyDataWithDateWindowExpiredWithOrder():
    print("Running Test - Short order - Strategy time expired")
    dt = datetime.combine(date.today(),time(12,35))
    dtBought = datetime.combine(date.today(),time(9,32))
    order = Order(OrderType.Short, 'DummyStock', 14, 28.3, OrderExecutionType.MarketPrice)
    data = StrategyData('DummyStock', dt, 21, 22.27, 22.30, None, order)
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
