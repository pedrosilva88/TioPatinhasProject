import os, sys
import os.path
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
import csv
from enum import Enum
from ib_insync import *
from datetime import datetime, date, timedelta, time
from IPython.display import display, clear_output
import pandas as pd
from scanner import Scanner
from strategy import StrategyOPG, StrategyData, StrategyResult, StrategyResultType
from models import Order as myOrder, OrderAction

class BackTestModel():
    ticker: Ticker
    averageVolume: float
    volumeInFirstMinuteBar: float

    def __init__(self, ticker: Ticker, avgVolume: float, volumeFirstMinuteBar: float):
        self.ticker = ticker
        self.averageVolume = avgVolume if avgVolume else 0
        self.volumeInFirstMinuteBar = volumeFirstMinuteBar if volumeFirstMinuteBar else 0

class BackTestResultType(Enum):
    takeProfit = 1
    profit = 2
    stopLoss = 3
    loss = 4

class BackTestResult():
    date: date
    symbol: str
    pnl: float
    action: str
    type: BackTestResultType

    def __init__(self, symbol: str, date: date, pnl, action: str, type: BackTestResultType):
        self.symbol = symbol
        self.date = date
        self.pnl = pnl
        self.action = action
        self.type = type

class BackTest():
    results: [str, [BackTestResult]]

    def __init__(self):
        util.startLoop()
        # self.ib = IB()
        # self.ib.connect('127.0.0.1', 7497, clientId=16)
        self.strategy = StrategyOPG()
        self.results = dict()

    def run(self):
        scanner = Scanner()
        scanner.getOPGRetailers(path='../scanner/Data/CSV/US/OPG_Retails_SortFromBackTest.csv')
        stocks = scanner.stocks
        
        for stock in stocks:
            name = ("backtest/Data/CSV/%s.csv" % stock.symbol)
        
            if not os.path.isfile(name):
                print("File not found ", name)
                continue
            models = self.getModelsFromCSV(name)
            self.runStrategy(models)
        print(len(self.results.keys()))

    def updateResults(self, key: str, value: BackTestResult):
        if key in self.results:
            self.results[key].append(value)
        self.results[key] = [value]

    def runStrategy(self, models: [BackTestModel]):
        limitProfits = 0
        stopLosses = 0
        profits = 0
        losses = 0
        totalWon = 0
        totalLoss = 0
        order: myOrder = None
        tempOrder: myOrder = None
        position: Position = None
        currentDay: date = None
        dayTradingEnded = False
        firstOfTheDay = True

        for model in models:
            ticker = model.ticker
            stock = model.ticker.contract
            today = ticker.time.replace(microsecond=0, tzinfo=None).date()
            if not currentDay or (currentDay != today):
                print(today)
                currentDay = today
                order = None
                tempOrder = None
                position = None
                dayTradingEnded = False
                firstOfTheDay = True

            if dayTradingEnded:
                continue

            if (position and tempOrder):
                if ((tempOrder.action == OrderAction.Buy and tempOrder.takeProfitOrder.lmtPrice <= ticker.last) or
                    (tempOrder.action == OrderAction.Sell and tempOrder.takeProfitOrder.lmtPrice >= ticker.last)):
                    ganho = abs(tempOrder.takeProfitOrder.lmtPrice*tempOrder.takeProfitOrder.totalQuantity-tempOrder.lmtPrice*tempOrder.totalQuantity)
                    totalWon += ganho
                    print("Success ✅ - %.2f FirstMinute(%d) Average(%d)\n" % (ganho, model.volumeInFirstMinuteBar, model.averageVolume))
                    result = BackTestResult(ticker.contract.symbol, ticker.time, ganho, tempOrder.action.value, BackTestResultType.takeProfit)
                    self.updateResults(key=("%s" % ticker.time.date()), value=result)
                    limitProfits += 1
                    dayTradingEnded = True
                    continue
                elif ((tempOrder.action == OrderAction.Buy and tempOrder.stopLossOrder.auxPrice >= ticker.last) or
                    (tempOrder.action == OrderAction.Sell and tempOrder.stopLossOrder.auxPrice <= ticker.last)):
                    perda = abs(tempOrder.stopLossOrder.auxPrice*tempOrder.stopLossOrder.totalQuantity-tempOrder.lmtPrice*tempOrder.totalQuantity)
                    totalLoss += perda
                    print("StopLoss ❌ - %.2f FirstMinute(%d) Average(%d)\n" % (perda, model.volumeInFirstMinuteBar, model.averageVolume))
                    result = BackTestResult(ticker.contract.symbol, ticker.time, perda, tempOrder.action.value, BackTestResultType.stopLoss)
                    self.updateResults(key=("%s" % ticker.time.date()), value=result)
                    stopLosses += 1
                    dayTradingEnded = True
                    continue
            elif (order and ((order.action == OrderAction.Buy and order.lmtPrice >= ticker.last) or
                (order.action == OrderAction.Sell and order.lmtPrice <= ticker.last))):
                tempOrder = order
                order = None
                position = Position(account="",contract=stock, position=tempOrder.totalQuantity, avgCost=tempOrder.lmtPrice)

            if ticker.time.day == 9: # and
                # result.ticker.time.day == 8 and
                # result.ticker.time.day == 8)
                #print("Hour(%s) Volume(%d)" % (ticker.time.time(), ticker.volume))
                None
                
            data = StrategyData(ticker, 
                                position, 
                                order, 
                                2000,
                                model.averageVolume,
                                model.volumeInFirstMinuteBar)
            result = self.strategy.run(data)

            # if (firstOfTheDay):
            #     firstOfTheDay = False
            #     print(result)

            if (result.type == StrategyResultType.Buy or result.type == StrategyResultType.Sell):
                order = result.order
                print(result)

            elif result.type == StrategyResultType.StrategyDateWindowExpired:
                dayTradingEnded = True
            elif result.type == StrategyResultType.DoNothing:
                None
            elif (result.type == StrategyResultType.PositionExpired_Buy or result.type == StrategyResultType.PositionExpired_Sell):
                dayTradingEnded = True
                if ((tempOrder.action == OrderAction.Buy and tempOrder.lmtPrice < ticker.last) or
                    (tempOrder.action == OrderAction.Sell and tempOrder.lmtPrice > ticker.last)):
                    ganho = abs(ticker.last*tempOrder.takeProfitOrder.totalQuantity-tempOrder.lmtPrice*tempOrder.totalQuantity)
                    profits += 1
                    totalWon += ganho
                    result = BackTestResult(ticker.contract.symbol, ticker.time, ganho, tempOrder.action.value, BackTestResultType.profit)
                    self.updateResults(key=("%s" % ticker.time.date()), value=result)
                    print("Success (not profit) ✅ - %.2f FirstMinute(%d) Average(%d)\n" % (ganho, model.volumeInFirstMinuteBar, model.averageVolume))
                else:
                    perda = abs(ticker.last*tempOrder.takeProfitOrder.totalQuantity-tempOrder.lmtPrice*tempOrder.totalQuantity)
                    losses += 1
                    totalLoss += perda
                    result = BackTestResult(ticker.contract.symbol, ticker.time, perda, tempOrder.action.value, BackTestResultType.loss)
                    self.updateResults(key=("%s" % ticker.time.date()), value=result)
                    print("Loss ❌ - %.2f FirstMinute(%d) Average(%d)\n" % (perda, model.volumeInFirstMinuteBar, model.averageVolume))

            elif result.type == StrategyResultType.KeepOrder:
                order = result.order

            elif (result.type == StrategyResultType.CancelOrder or result.type == StrategyResultType.StrategyDateWindowExpiredCancelOrder):
                print("Order Cancelled")
                order = None
                dayTradingEnded = True
            else:
                None

        print("\n\nResult: LimitProfits(%d) Profits(%d) StopLosses(%d) Losses(%d) PnL(%.2f)" % (limitProfits, profits, stopLosses, losses, (totalWon-totalLoss)))
            
    def getDayBar(self, date: datetime, bars: [BarData]):
        for i in range(len(bars)):

            if date.replace(microsecond=0, tzinfo=None).date() == bars[i].date:
                if i == 0:
                    return None, None
                else:
                    return bars[i-1], bars[i]

    def downloadHistoricDataFromIB(self, stock: Contract, days: int = 5) -> ([BarData], [BarData]):
        nDays = days
        durationDays = ("%d D" % (nDays+1))
        today = datetime.now().replace(microsecond=0, tzinfo=None).date()
        startDate = today-timedelta(days=nDays)
        
        minute_bars: [BarData] = []
        while startDate <= today:
            print("Historical Data: %s - %s" % (stock.symbol, startDate))
            bars: [BarData] = self.ib.reqHistoricalData(stock, endDateTime=startDate, 
                                                    durationStr='5 D', 
                                                    barSizeSetting='1 min', 
                                                    whatToShow='TRADES',
                                                    useRTH=True,
                                                    formatDate=1)
            startDate = startDate+timedelta(days=5)
            minute_bars += bars

        day_bars: [BarData] = self.ib.reqHistoricalData(stock, endDateTime='', 
                                                durationStr=durationDays, 
                                                barSizeSetting='1 day', 
                                                whatToShow='TRADES',
                                                useRTH=True,
                                                formatDate=1)
        
        return minute_bars, day_bars

    def createListOfBackTestModels(self, stock: Contract, mBars: [BarData], dBars: [BarData]) -> [BackTestModel]:
        models = []
        lastDay = None
        lastAverageVolume = None
        lastVolumeFirstMinute = None
        barTodayOpen = None
        barYstdClose = None

        for mBar in mBars:
            if (not lastDay or (lastDay.replace(microsecond=0, tzinfo=None).date() != mBar.date.replace(microsecond=0, tzinfo=None).date())):
                result = self.getDayBar(mBar.date, dBars)
                averageVolume = self.getAverageVolume(mBars, mBar.date)
                lastVolumeFirstMinute = self.getVolumeInFirstMinute(mBars, mBar.date)
                if (result and result[0] and result[1]):
                    barTodayOpen = result[1].open
                    barYstdClose = result[0].close
                else:
                    barTodayOpen = None
                    barYstdClose = None
                lastDay = mBar.date.replace(microsecond=0, tzinfo=None)
            ticker = Ticker(contract=stock, 
                            time=mBar.date, 
                            close=barYstdClose, 
                            open=barTodayOpen,
                            bid=mBar.average, 
                            ask=mBar.average, 
                            last=mBar.average,
                            volume=mBar.volume)
            model = BackTestModel(ticker, averageVolume, lastVolumeFirstMinute)
            models.append(model)
        return models
    
    def getAverageVolume(self, data: [BarData], date: date):
        last = (date.year, date.month, date.day)
        firstDate = date-timedelta(days=21)
        first = (firstDate.year, firstDate.month, firstDate.day)
        filterData = list(filter(lambda x: (first < (x.date.year, x.date.month, x.date.day) < last), data))
        nBars = len(filterData)
        if nBars > 0:
            sum = 0
            for data in filterData: 
                sum += data.volume
            
            return sum/nBars
        else:
            return 0

    def getVolumeInFirstMinute(self, data: [BarData], date: date):
        target = datetime.combine(date.date(), time(14,30)).replace(microsecond=0,tzinfo=None)
        filterData = list(filter(lambda x: x.date.replace(microsecond=0, tzinfo=None) == target, data))

        if len(filterData) >= 1:
            bar = filterData.pop()        
            return bar.volume
        else: return None

    def saveDataInCSVFile(self, filename: str, data: [BackTestModel]):
        name = ("backtest/Data/CSV/%s.csv" % filename)
        with open(name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Symbol", "Date", "Close", "Open", "Bid", "Ask", "Last", "Volume", "AvgVolume", "VolumeFirstMinute"])
            for model in data:
                volumeMinute = None if not model.volumeInFirstMinuteBar else round(model.volumeInFirstMinuteBar, 2)
                averageVolume = None if not model.averageVolume else round(model.averageVolume, 2)
                openPrice = 0 if not model.ticker.open else round(model.ticker.open, 2)
                close = 0 if not model.ticker.close else round(model.ticker.close, 2)
                bid = 0 if not model.ticker.bid else round(model.ticker.bid, 2)
                ask = 0 if not model.ticker.ask else round(model.ticker.ask, 2)
                last = 0 if not model.ticker.last else round(model.ticker.last, 2)
                volume = None if not model.ticker.volume else round(model.ticker.volume, 2)
                writer.writerow([model.ticker.contract.symbol, 
                                model.ticker.time, 
                                close, 
                                openPrice, 
                                bid, 
                                ask, 
                                last, 
                                volume, 
                                averageVolume, 
                                volumeMinute])

    def getModelsFromCSV(self, filePath: str):
        formatDate = "%Y-%m-%d %H:%M:%S"
        models = []
        with open(filePath) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count > 0:
                    stock = Stock(row[0], "SMART", "USD")
                    volumeMinute = None if not row[9] else float(row[9])
                    averageVolume = None if not row[8] else float(row[8])
                    openPrice = 0 if not row[3] else float(row[3])
                    close = 0 if not row[2] else float(row[2])
                    bid = 0 if not row[4] else float(row[4])
                    ask = 0 if not row[5] else float(row[5])
                    last = 0 if not row[6] else float(row[6])
                    volume = 0 if not row[7] else float(row[7])
                    ticker = Ticker(contract=stock, 
                            time=datetime.strptime(row[1], formatDate), 
                            close=close, 
                            open=openPrice,
                            bid=bid, 
                            ask=ask, 
                            last=last,
                            volume=volume)
                    models.append(BackTestModel(ticker, averageVolume, volumeMinute))
                line_count += 1
        return models

    def downloadStocksToCSVFile(self):
        scanner = Scanner()
        scanner.getOPGRetailers(path='../scanner/Data/CSV/US/OPG_Retails_SortFromBackTest.csv')
        stocks = scanner.stocks
        total = len(stocks)
        current = 0
        for stock in stocks:
            current += 1
            sys.stdout.write("\t Contracts: %i/%i \r" % (current, total) )
            if current <= total-1:
                sys.stdout.flush()
            else:
                print("")

            mBars, dBars = self.downloadHistoricDataFromIB(stock, 200)
            models = self.createListOfBackTestModels(stock, mBars, dBars)
            self.saveDataInCSVFile(stock.symbol, models)

if __name__ == '__main__':
    try:
        backtest = BackTest()
        #backtest.downloadStocksToCSVFile()
        backtest.run()
    except (KeyboardInterrupt, SystemExit):
        None