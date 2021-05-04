import os, sys
import os.path

import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mpl_dates
import pandas as pd

from pytz import timezone as tz
from zigzag import *
from ib_insync import *
from backtest import *
from country_config import CountryConfig, CountryKey, getConfigFor
from scanner import Scanner
from models import Order as myOrder, OrderAction, CustomBarData
from datetime import *
from strategy import StrategyZigZag, StrategyConfig, StrategyData, StrategyResultType, getStrategyConfigFor

class BackTestSwing():
    results: [str, [BackTestResult]]
    trades: [str, [str]]
    cashAvailable: float
    countryConfig: CountryConfig
    strategyConfig: StrategyConfig

    def __init__(self):
        self.results = dict()
        self.trades = dict()
        self.cashAvailable = 6000
        self.countryConfig = getConfigFor(CountryKey.USA)
        self.strategyConfig= getStrategyConfigFor(key=self.countryConfig.key, timezone=self.countryConfig.timezone)

def createListOfBackTestModels(stock: Contract, bars: [BarData], zigzags:[int], rsi: [float], dateFormat: str = "%Y-%m-%d %H:%M:%S") -> [BackTestModel]:
    models = []
    i = 0
    for bar in bars:
        zigzag = True if zigzags[i] != 0 else False
        rsi_value = None
        if i > 0:
            rsi_value = rsi[i-1]
        dateString = bar.date.strftime("%Y-%m-%d %H:%M:%S").replace(" 00", " 12")
        model = BackTestModel(bar.open, bar.close, bar.low, bar.high, bar.close, 
                                bar.volume, stock.symbol,
                                zigzag, rsi_value,
                                dateString, 
                                None, None)
        models.append(model)
        i += 1
    return models

def computeRSI(data, time_window):
    diff = data.diff(1).dropna()        # diff in one field(one day)

    #this preservers dimensions off diff values
    up_chg = 0 * diff
    down_chg = 0 * diff
    
    # up change is equal to the positive difference, otherwise equal to zero
    up_chg[diff > 0] = diff[ diff>0 ]
    
    # down change is equal to negative deifference, otherwise equal to zero
    down_chg[diff < 0] = diff[ diff < 0 ]
    
    # check pandas documentation for ewm
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.ewm.html
    # values are related to exponential decay
    # we set com=time_window-1 so we get decay alpha=1/time_window
    up_chg_avg   = up_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
    down_chg_avg = down_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
    
    rs = abs(up_chg_avg/down_chg_avg)
    rsi = 100 - 100/(1+rs)
    return rsi

def showPlot(mBars: [BarData], zigzags:[int]):
    i = 0
    dates = []
    items = []
    isForLow = False
    for bar in mBars:
        zigzag = zigzags[i]
        if zigzag != 0:
            dates.append(bar.date)
            if isForLow:
                items.append(bar.low)
                isForLow = False
            else:
                items.append(bar.high)
                isForLow = True

        i += 1
    plt.style.use('ggplot')

    # Extracting Data for plotting
    ohlc = util.df(mBars, ['date', 'open', 'high', 'low', 'close'])
    ohlc['date'] = pd.to_datetime(ohlc['date'])
    ohlc['date'] = ohlc['date'].apply(mpl_dates.date2num)
    ohlc = ohlc.astype(float)

    # Creating Subplots
    fig, ax = plt.subplots()

    candlestick_ohlc(ax, ohlc.values, width=0.6, colorup='green', colordown='red', alpha=0.8)

    # Setting labels & titles
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    fig.suptitle('Daily Candlestick Chart of NIFTY50')

    ax.plot(dates, items, color='blue', label='ZigZag')

    fig.suptitle('Daily Candlestick Chart of PG with ZigZag')

    plt.legend()

    # Formatting Date
    date_format = mpl_dates.DateFormatter('%d-%m-%Y')
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()

    fig.tight_layout()

    plt.show()

def downloadData():
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=16)
    path = ("Scanner/ZigZag/%s/scan_to_download.csv" % CountryKey.USA.code)
    savePath = "ZigZag/Stocks"
    countryConfig = getConfigFor(key=CountryKey.USA)
    modelDays = BackTestDownloadModel(path=path, numberOfDays=1825, barSize="1 day") # 5Years = 1825 days
    itemsDictionary = downloadStocksData(ib, modelDays)

    for key, (stock, bars) in itemsDictionary.items():
        closes = util.df(bars)['close']
        lows = util.df(bars)['low']
        highs = util.df(bars)['high']
        RSI = computeRSI(closes, 14)
        pivots = peak_valley_pivots_candlestick(closes.values, highs.values, lows.values, 0.05, -0.05)
        models = createListOfBackTestModels(stock, bars, pivots, RSI.values)

        saveDataInCSVFile(key, savePath, models, countryConfig)

        #showPlot(bars, pivots)

def loadStocks(fileName: str = "scan_to_run_strategy.csv"):
    path = ("Scanner/ZigZag/%s/%s" % (CountryKey.USA.code, fileName))
    countryConfig = getConfigFor(key=CountryKey.USA)
    return loadFiles(path, countryConfig)

# Run Strategy

def run():
    models = loadStocks()
    print("Run Strategy")
    model = BackTestSwing()
    report = BackTestReport()
    runStrategy(backtestModel=model, backtestReport=report, models=models)
    path = ("backtest/Data/CSV/%s/ZigZag/Report" % (model.countryConfig.key.code))
    report.showReport(path, True)

def runStockPerformance():
    models = loadStocks("scan_to_download.csv")
    print("Run Performance")
    model = BackTestSwing()
    report = BackTestReport()
    runStrategy(backtestModel=model, backtestReport=report, models=models, forPerformance=True)

    stocksPath = ("Scanner/ZigZag/%s/scan_to_download.csv" % CountryKey.USA.code)
    path = ("backtest/Data/CSV/%s/ZigZag/Report" % (CountryKey.USA.code))
    report.showPerformanceReport(path, stocksPath, model.countryConfig)

def runStrategy(backtestModel: BackTestSwing, backtestReport: BackTestReport, models: [BackTestModel], forPerformance: bool = False):
    strategy = StrategyZigZag()
    tempOrders: [str, (myOrder, Position, date)] = dict()
    isForStockPerformance = forPerformance
    i = 0
    for model in models:
        ticker = model.ticker(backtestModel.countryConfig)
        stock = ticker.contract
        filteredList = [] #[(a,b,c) for key, (a,b,c) in tempOrders if ticker.contract.symbol in key.lower()]

        for key, myTuple in tempOrders.items():
            if key.split("_")[0] == ticker.contract.symbol:
                filteredList.append(myTuple)

        #print(len(filteredList))
        if (len(filteredList) > 0):
            for tempOrder, position, positionDate in filteredList:
                if ((tempOrder.action == "BUY" and tempOrder.takeProfitOrder.lmtPrice <= ticker.ask) or
                     (tempOrder.action == "SELL" and tempOrder.takeProfitOrder.lmtPrice >= ticker.bid)):
                    ganho = abs(tempOrder.takeProfitOrder.lmtPrice*tempOrder.takeProfitOrder.totalQuantity-tempOrder.lmtPrice*tempOrder.totalQuantity)
                    print("Success ✅ - %.2f Size(%.2f) high(%.2f) low(%.2f)\n" % (ganho, tempOrder.totalQuantity, ticker.ask, ticker.bid))
                    result = BackTestResult(symbol=ticker.contract.symbol, 
                                            date=ticker.time, 
                                            pnl=(ganho), 
                                            action="Long" if tempOrder.action == "BUY" else "Short", 
                                            type=BackTestResultType.takeProfit,
                                            priceCreateTrade= tempOrder.lmtPrice, 
                                            priceCloseTrade= tempOrder.takeProfitOrder.lmtPrice,
                                            size= tempOrder.totalQuantity, 
                                            averageVolume= model.averageVolume, 
                                            volumeFirstMinute= model.volumeInFirstMinuteBar, 
                                            totalInvested= tempOrder.lmtPrice*tempOrder.totalQuantity,
                                            openPrice= ticker.open, 
                                            ystdClosePrice= ticker.close,
                                            cash= backtestModel.cashAvailable,
                                            orderDate = positionDate.date())
                    if isForStockPerformance:
                        backtestReport.updateStockPerformance(ticker=ticker, type=result.type)
                        backtestReport.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result, zigzag=True)
                    else:
                        backtestReport.updateResults(key=("%s" % ticker.time.date()), value=result)
                        backtestReport.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result, zigzag=True)
                        backtestModel.cashAvailable += ganho
                    tempOrders.pop(magicKey(position.contract.symbol, positionDate))
                elif ((tempOrder.action == "BUY" and tempOrder.stopLossOrder.auxPrice > ticker.bid) or
                        (tempOrder.action == "SELL" and tempOrder.stopLossOrder.auxPrice < ticker.ask)):
                    perda = abs(tempOrder.stopLossOrder.auxPrice*tempOrder.stopLossOrder.totalQuantity-tempOrder.lmtPrice*tempOrder.totalQuantity)
                    print("StopLoss ❌ - %.2f Size(%.2f)\n" % (perda, tempOrder.totalQuantity))
                    result = BackTestResult(symbol=ticker.contract.symbol, 
                                            date=ticker.time, 
                                            pnl=(-perda), 
                                            action="Long" if tempOrder.action == "BUY" else "Short", 
                                            type=BackTestResultType.stopLoss,
                                            priceCreateTrade= tempOrder.lmtPrice, 
                                            priceCloseTrade= tempOrder.stopLossOrder.auxPrice,
                                            size= tempOrder.totalQuantity, 
                                            averageVolume= model.averageVolume, 
                                            volumeFirstMinute= model.volumeInFirstMinuteBar, 
                                            totalInvested= tempOrder.lmtPrice*tempOrder.totalQuantity,
                                            openPrice= ticker.open, 
                                            ystdClosePrice= ticker.close,
                                            cash= backtestModel.cashAvailable,
                                            orderDate = positionDate.date())
                    if isForStockPerformance:
                        backtestReport.updateStockPerformance(ticker=ticker, type=result.type)
                        backtestReport.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result, zigzag=True)
                    else:
                        backtestReport.updateResults(key=("%s" % ticker.time.date()), value=result)
                        backtestReport.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result, zigzag=True)
                        backtestModel.cashAvailable -= perda
                    tempOrders.pop(magicKey(position.contract.symbol, positionDate))
                elif ticker.time.date() >= (positionDate+timedelta(days=5)).date():
                    if ((tempOrder.action == "BUY" and (tempOrder.lmtPrice <= ticker.last)) or
                        (tempOrder.action == "SELL" and (tempOrder.lmtPrice >= ticker.last))):
                        closePrice = ticker.last
                        ganho = abs(closePrice*tempOrder.takeProfitOrder.totalQuantity-tempOrder.lmtPrice*tempOrder.totalQuantity)
                        result = BackTestResult(symbol=ticker.contract.symbol, 
                                                date=ticker.time, 
                                                pnl=(ganho), 
                                                action="Long" if tempOrder.action == "BUY" else "Short", 
                                                type=BackTestResultType.profit,
                                                priceCreateTrade= tempOrder.lmtPrice, 
                                                priceCloseTrade= closePrice,
                                                size= tempOrder.totalQuantity, 
                                                averageVolume= model.averageVolume, 
                                                volumeFirstMinute= model.volumeInFirstMinuteBar, 
                                                totalInvested= tempOrder.lmtPrice*tempOrder.totalQuantity,
                                                openPrice= ticker.open, 
                                                ystdClosePrice= ticker.close,
                                                cash= backtestModel.cashAvailable,
                                                orderDate = positionDate.date())
                        if isForStockPerformance:
                            backtestReport.updateStockPerformance(ticker=ticker, type=result.type)
                            backtestReport.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result, zigzag=True)
                        else:
                            backtestReport.updateResults(key=("%s" % ticker.time.date()), value=result)
                            backtestReport.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result, zigzag=True)
                            backtestModel.cashAvailable += ganho
                        print("Success (not profit) ✅ - %.2f Size(%.2f)\n" % (ganho, tempOrder.totalQuantity))
                    else:
                        closePrice = ticker.last
                        perda = abs(closePrice*tempOrder.totalQuantity-tempOrder.lmtPrice*tempOrder.totalQuantity)
                        result = BackTestResult(symbol=ticker.contract.symbol, 
                                                date=ticker.time, 
                                                pnl=(-perda), 
                                                action="Long" if tempOrder.action == "BUY" else "Short", 
                                                type=BackTestResultType.loss,
                                                priceCreateTrade= tempOrder.lmtPrice, 
                                                priceCloseTrade= closePrice,
                                                size= tempOrder.totalQuantity, 
                                                averageVolume= model.averageVolume, 
                                                volumeFirstMinute= model.volumeInFirstMinuteBar, 
                                                totalInvested= tempOrder.lmtPrice*tempOrder.totalQuantity,
                                                openPrice= ticker.open, 
                                                ystdClosePrice= ticker.close,
                                                cash= backtestModel.cashAvailable,
                                                orderDate = positionDate.date())
                        if isForStockPerformance:
                            backtestReport.updateStockPerformance(ticker=ticker, type=result.type)
                            backtestReport.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result, zigzag=True)
                        else:
                            backtestReport.updateResults(key=("%s" % ticker.time.date()), value=result)
                            backtestReport.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result, zigzag=True)
                            backtestModel.cashAvailable -= perda
                        print("Loss ❌ - %.2f Size(%.2f)\n" % (perda, tempOrder.totalQuantity))
                    tempOrders.pop(magicKey(position.contract.symbol, positionDate))

        result = None
        previousModels = getPreviousBarsData(model, models, i)
        if (previousModels[0] is not None and
            previousModels[1] is not None and
            previousModels[2] is not None and
            previousModels[3] is not None and
            previousModels[4] is not None and
            previousModels[5] is not None):
            previousBars = [createCustomBarData(previousModels[5], backtestModel.countryConfig),
                            createCustomBarData(previousModels[4], backtestModel.countryConfig),
                            createCustomBarData(previousModels[3], backtestModel.countryConfig),
                            createCustomBarData(previousModels[2], backtestModel.countryConfig),
                            createCustomBarData(previousModels[1], backtestModel.countryConfig),
                            createCustomBarData(previousModels[0], backtestModel.countryConfig)]
            currentBar = createCustomBarData(model, backtestModel.countryConfig)
            data = StrategyData(ticker=ticker, 
                                position=None, 
                                order=None, 
                                totalCash=backtestModel.cashAvailable,
                                previousBars=previousBars,
                                currentBar=currentBar)
            
            for bar in previousBars:
                if getPercentageChange(currentBar.close, bar.close) < 5:
                    bar.zigzag = False
            
            result = strategy.run(data, backtestModel.strategyConfig, backtestModel.countryConfig)
            if (result.type == StrategyResultType.Buy or result.type == StrategyResultType.Sell):
                totalInPositions = calculatePriceInPositions(tempOrders)
                balance = backtestModel.cashAvailable - totalInPositions
                totalOrderCost = result.order.lmtPrice*result.order.totalQuantity
                if (balance > totalOrderCost and result.order.totalQuantity > 0) or isForStockPerformance:
                    tempOrders[magicKey(ticker.contract.symbol, ticker.time)] = (result.order,
                                                                                    Position(account="",contract=stock, position=result.order.totalQuantity, avgCost=result.order.lmtPrice),
                                                                                    ticker.time)
                    print(result)

            elif result.type == StrategyResultType.DoNothing:
                None
            else:
                None
        i += 1

    #print("\n\nResult: LimitProfits(%d) Profits(%d) StopLosses(%d) Losses(%d) PnL(%.2f)" % (limitProfits, profits, stopLosses, losses, (totalWon-totalLoss)))

def getPercentageChange(current, previous):
    if current == previous:
        return 100.0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return 0

def createCustomBarData(model: BackTestModel, countryConfig: CountryConfig):
    barData = BarData(date=model.ticker(countryConfig).time,
                        open=model.openPrice,
                        high=model.ask,
                        low=model.bid,
                        close=model.close,
                        volume=model.volume)
    return CustomBarData(barData, model.zigzag, model.rsi)

def getPreviousBarsData(model: BackTestModel, models: [BackTestModel], currentPosition: int):
    previousData_1 = None
    previousData_2 = None
    previousData_3 = None
    previousData_4 = None
    previousData_5 = None
    previousData_6 = None
    position = 0
    zigzagFound = False
    while (previousData_1 is None and
            currentPosition-position > 0):
        position += 1
        item = models[currentPosition-position]
        if item.symbol == model.symbol:
            previousData_1 = item
            if item.zigzag == True:
                zigzagFound = True
    
    while (previousData_2 is None and
            currentPosition-position > 0):
        position += 1
        item = models[currentPosition-position]
        if item.symbol == model.symbol:
            previousData_2 = item
            if zigzagFound == True:
                previousData_2.zigzag = False
            elif item.zigzag == True and zigzagFound == False:
                zigzagFound = True
    
    while (previousData_3 is None and
            currentPosition-position > 0):
        position += 1
        item = models[currentPosition-position]
        if item.symbol == model.symbol:
            previousData_3 = item
            if zigzagFound == True:
                previousData_3.zigzag = False
            elif item.zigzag == True and zigzagFound == False:
                zigzagFound = True

    
    while (previousData_4 is None and
            currentPosition-position > 0):
        position += 1
        item = models[currentPosition-position]
        if item.symbol == model.symbol:
            previousData_4 = item
            if zigzagFound == True:
                previousData_4.zigzag = False
            elif item.zigzag == True and zigzagFound == False:
                zigzagFound = True


    while (previousData_5 is None and
            currentPosition-position > 0):
        position += 1
        item = models[currentPosition-position]
        if item.symbol == model.symbol:
            previousData_5 = item
            if zigzagFound == True:
                previousData_5.zigzag = False
            elif item.zigzag == True and zigzagFound == False:
                zigzagFound = True


    while (previousData_6 is None and
            currentPosition-position > 0):
        position += 1
        item = models[currentPosition-position]
        if item.symbol == model.symbol:
            previousData_6 = item
            if zigzagFound == True:
                previousData_6.zigzag = False
            elif item.zigzag == True and zigzagFound == False:
                zigzagFound = True

    if previousData_6 is not None and previousData_6.zigzag == True:
        if ((getPercentageChange(previousData_6.close, previousData_1.close) >= 5) or
            (getPercentageChange(previousData_6.close, previousData_2.close) >= 5) or
            (getPercentageChange(previousData_6.close, previousData_3.close) >= 5) or
            (getPercentageChange(previousData_6.close, previousData_4.close) >= 5) or
            (getPercentageChange(previousData_6.close, previousData_5.close) >= 5)):
            previousData_6.zigzag = False

    if previousData_5 is not None and previousData_5.zigzag == True:
        if ((getPercentageChange(previousData_5.close, previousData_1.close) >= 5) or
            (getPercentageChange(previousData_5.close, previousData_2.close) >= 5) or
            (getPercentageChange(previousData_5.close, previousData_3.close) >= 5) or
            (getPercentageChange(previousData_5.close, previousData_4.close) >= 5)):
            previousData_5.zigzag = False

    if previousData_4 is not None and previousData_4.zigzag == True:
        if ((getPercentageChange(previousData_4.close, previousData_1.close) >= 5) or
            (getPercentageChange(previousData_4.close, previousData_2.close) >= 5) or
            (getPercentageChange(previousData_4.close, previousData_3.close) >= 5)):
            previousData_4.zigzag = False

    if previousData_3 is not None and previousData_3.zigzag == True:
        if ((getPercentageChange(previousData_3.close, previousData_1.close) >= 5) or
            (getPercentageChange(previousData_3.close, previousData_2.close) >= 5)):
            previousData_3.zigzag = False

    if previousData_2 is not None and previousData_2.zigzag == True:
        if ((getPercentageChange(previousData_2.close, previousData_1.close) >= 5)):
            previousData_2.zigzag = False

    return [previousData_1, previousData_2, previousData_3, previousData_4, previousData_5, previousData_6]

def calculatePriceInPositions(tempOrders):
    total = 0
    for key, (tempOrder, item, positionDate) in tempOrders.items():
        total += item.position * item.avgCost
    return total

def magicKey(symbol: str, date: datetime):
    return ("%s_%s" % (symbol, date.strftime("%y%m%d")))

if __name__ == '__main__':
    try:
        #downloadData()
        #runStockPerformance()
        run()
        
    except (KeyboardInterrupt, SystemExit) as e:
        print(e)