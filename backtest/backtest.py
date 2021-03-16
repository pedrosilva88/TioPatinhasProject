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

    def emoji(self):
        if self == BackTestResultType.takeProfit:
            return "✅ ✅"
        elif self == BackTestResultType.profit:
            return "✅"
        elif self == BackTestResultType.stopLoss:
            return "❌ ❌"
        elif self == BackTestResultType.loss:
            return "❌"

class BackTestResult():
    date: date
    symbol: str
    pnl: float
    action: str
    type: BackTestResultType
    priceCreateTrade: float
    priceCloseTrade: float
    size: int
    averageVolume: float
    volumeFirstMinute: float
    totalInvested: float
    openPrice: float
    ystdClosePrice: float

    def __init__(self, symbol: str, date: date, pnl, action: str, 
                type: BackTestResultType, priceCreateTrade: float, priceCloseTrade: float,
                size: int, averageVolume: float, volumeFirstMinute: float, totalInvested: float,
                openPrice: float, ystdClosePrice: float):
        self.symbol = symbol
        self.date = date
        self.pnl = pnl
        self.action = action
        self.type = type
        self.priceCreateTrade = priceCreateTrade
        self.priceCloseTrade = priceCloseTrade
        self.size = size
        self.averageVolume =  averageVolume
        self.volumeFirstMinute =  volumeFirstMinute
        self.totalInvested = totalInvested
        self.openPrice = openPrice
        self.ystdClosePrice = ystdClosePrice

class BackTest():
    results: [str, [BackTestResult]]
    trades: [str, [str]] = dict()

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
        # stocks = [Stock("VUZI","SMART","USD"),
        #             Stock("HBP","SMART","USD"),
        #             Stock("ASO","SMART","USD"),
        #             Stock("BBQ","SMART","USD"),
        #             Stock("BGI","SMART","USD"),
        #             Stock("KXIN","SMART","USD"),
        #             Stock("JILL","SMART","USD"),
        #             Stock("WTRH","SMART","USD")]
        for stock in stocks:
            name = ("backtest/Data/CSV/%s.csv" % stock.symbol)
        
            if not os.path.isfile(name):
                print("File not found ", name)
                continue
            models = self.getModelsFromCSV(name)
            self.runStrategy(models)
        self.showReport()
    
    def saveReportResultInFile(self, data:[[]]):
        name = "backtest/Data/CSV/Report/ResultsPnL.csv"
        with open(name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "PnL", "Trades"])
            for model in data:
                writer.writerow(model)

    def saveReportTradesInFile(self, data:[[]]):
        name = "backtest/Data/CSV/Report/ResultsTrades.csv"
        with open(name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Symbol", "Result", "PnL", "Price CreateTrade", "Price CloseTrade", "Size", "Avg Volume",  "Volume 1st minute", "Total Invested", "Open Price", "YSTD Close Price", "Action"])
            for model in data:
                writer.writerow(model)

    def showReport(self):
        for key, array in self.results.items():
            self.results[key] = array[:2]

        for key, array in self.trades.items():
            self.trades[key] = array[:2]

        items = [[]]
        for key, array in self.results.items():
            total = 0
            for item in array:
                total += item.pnl
            items.append([key, total, len(array)])
            print("%s: %.2f€ %d" % (key, total, len(array)))

        self.saveReportResultInFile(items)

        items = [[]]
        for key, array in self.trades.items():
            for item in array:
                items.append(item)

        self.saveReportTradesInFile(items)
            
    def deduplicate(self, items):
        seen = set()
        for item in items:
            if not item.symbol in seen:
                seen.add(item.symbol)
                yield item

    def updateResults(self, key: str, value: BackTestResult):
        if key in self.results:
            self.results[key].append(value)
        else:
            self.results[key] = [value]

    def updateTrades(self, key: str, ticker: Ticker, result: BackTestResult):
        resultArray = []
        resultArray.append(key) # date
        resultArray.append(ticker.contract.symbol) # symbol
        resultArray.append(result.type.emoji()) # ✅ or ✅ ✅ or ❌  or ❌ ❌
        resultArray.append(result.pnl) # PnL
        resultArray.append(result.priceCreateTrade) # Price CreateTrade
        resultArray.append(result.priceCloseTrade) # Price CloseTrade
        resultArray.append(result.size) # Size
        resultArray.append(result.averageVolume) # AverageVolume
        resultArray.append(result.volumeFirstMinute) # VolumeFirstMinute
        resultArray.append(result.totalInvested) # Total Invested
        resultArray.append(result.openPrice) # Open Price
        resultArray.append(result.ystdClosePrice) # YSTD Close Price
        resultArray.append(result.action) # Action Long or Short
        
        if key in self.trades:
            self.trades[key].append(resultArray)
        else:
            self.trades[key] = [resultArray]

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
                    print(today)
                    print("Success ✅ - %.2f FirstMinute(%d) Average(%d) Size(%.2f)\n" % (ganho, model.volumeInFirstMinuteBar, model.averageVolume, tempOrder.totalQuantity))
                    result = BackTestResult(symbol=ticker.contract.symbol, 
                                            date=ticker.time, 
                                            pnl=(ganho), 
                                            action=tempOrder.action.value, 
                                            type=BackTestResultType.takeProfit,
                                            priceCreateTrade= tempOrder.lmtPrice, 
                                            priceCloseTrade= tempOrder.takeProfitOrder.lmtPrice,
                                            size= tempOrder.totalQuantity, 
                                            averageVolume= model.averageVolume, 
                                            volumeFirstMinute= model.volumeInFirstMinuteBar, 
                                            totalInvested= tempOrder.lmtPrice*tempOrder.totalQuantity,
                                            openPrice= ticker.open, 
                                            ystdClosePrice= ticker.close)
                    self.updateResults(key=("%s" % ticker.time.date()), value=result)
                    self.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result)
                    limitProfits += 1
                    dayTradingEnded = True
                    continue
                elif ((tempOrder.action == OrderAction.Buy and tempOrder.stopLossOrder.auxPrice >= ticker.last) or
                    (tempOrder.action == OrderAction.Sell and tempOrder.stopLossOrder.auxPrice <= ticker.last)):
                    perda = abs(tempOrder.stopLossOrder.auxPrice*tempOrder.stopLossOrder.totalQuantity-tempOrder.lmtPrice*tempOrder.totalQuantity)
                    totalLoss += perda
                    print(today)
                    print("StopLoss ❌ - %.2f FirstMinute(%d) Average(%d) Size(%.2f)\n" % (perda, model.volumeInFirstMinuteBar, model.averageVolume, tempOrder.totalQuantity))
                    result = BackTestResult(symbol=ticker.contract.symbol, 
                                            date=ticker.time, 
                                            pnl=(-perda), 
                                            action=tempOrder.action.value, 
                                            type=BackTestResultType.stopLoss,
                                            priceCreateTrade= tempOrder.lmtPrice, 
                                            priceCloseTrade= tempOrder.stopLossOrder.auxPrice,
                                            size= tempOrder.totalQuantity, 
                                            averageVolume= model.averageVolume, 
                                            volumeFirstMinute= model.volumeInFirstMinuteBar, 
                                            totalInvested= tempOrder.lmtPrice*tempOrder.totalQuantity,
                                            openPrice= ticker.open, 
                                            ystdClosePrice= ticker.close)
                    self.updateResults(key=("%s" % ticker.time.date()), value=result)
                    self.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result)
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
                    result = BackTestResult(symbol=ticker.contract.symbol, 
                                            date=ticker.time, 
                                            pnl=(ganho), 
                                            action=tempOrder.action.value, 
                                            type=BackTestResultType.profit,
                                            priceCreateTrade= tempOrder.lmtPrice, 
                                            priceCloseTrade= ticker.last,
                                            size= tempOrder.totalQuantity, 
                                            averageVolume= model.averageVolume, 
                                            volumeFirstMinute= model.volumeInFirstMinuteBar, 
                                            totalInvested= tempOrder.lmtPrice*tempOrder.totalQuantity,
                                            openPrice= ticker.open, 
                                            ystdClosePrice= ticker.close)
                    self.updateResults(key=("%s" % ticker.time.date()), value=result)
                    self.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result)
                    print(today)
                    print("Success (not profit) ✅ - %.2f FirstMinute(%d) Average(%d) Size(%.2f)\n" % (ganho, model.volumeInFirstMinuteBar, model.averageVolume, tempOrder.totalQuantity))
                else:
                    perda = abs(ticker.last*tempOrder.takeProfitOrder.totalQuantity-tempOrder.lmtPrice*tempOrder.totalQuantity)
                    losses += 1
                    totalLoss += perda
                    result = BackTestResult(symbol=ticker.contract.symbol, 
                                            date=ticker.time, 
                                            pnl=(-perda), 
                                            action=tempOrder.action.value, 
                                            type=BackTestResultType.loss,
                                            priceCreateTrade= tempOrder.lmtPrice, 
                                            priceCloseTrade= ticker.last,
                                            size= tempOrder.totalQuantity, 
                                            averageVolume= model.averageVolume, 
                                            volumeFirstMinute= model.volumeInFirstMinuteBar, 
                                            totalInvested= tempOrder.lmtPrice*tempOrder.totalQuantity,
                                            openPrice= ticker.open, 
                                            ystdClosePrice= ticker.close)
                    self.updateResults(key=("%s" % ticker.time.date()), value=result)
                    self.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result)
                    print(today)
                    print("Loss ❌ - %.2f FirstMinute(%d) Average(%d) Size(%.2f)\n" % (perda, model.volumeInFirstMinuteBar, model.averageVolume, tempOrder.totalQuantity))

            elif result.type == StrategyResultType.KeepOrder:
                order = result.order

            elif (result.type == StrategyResultType.CancelOrder or result.type == StrategyResultType.StrategyDateWindowExpiredCancelOrder):
                print("Order Cancelled")
                order = None
                dayTradingEnded = True
            else:
                None

        #print("\n\nResult: LimitProfits(%d) Profits(%d) StopLosses(%d) Losses(%d) PnL(%.2f)" % (limitProfits, profits, stopLosses, losses, (totalWon-totalLoss)))
            
    def getDayBar(self, date: datetime, bars: [BarData]):
        for i in range(len(bars)):

            if date.replace(microsecond=0, tzinfo=None).date() == bars[i].date:
                if i == 0:
                    return None, None
                else:
                    return bars[i-1], bars[i]

    def downloadHistoricDataFromIB(self, stock: Contract, days: int = 5) -> ([BarData], [BarData]):
        nDays = days
        durationDays = ("%d D" % (nDays+1)) if nDays < 365 else "1 Y"
        today = datetime.now().replace(microsecond=0, tzinfo=None).date()
        startDate = today-timedelta(days=nDays+1)
        
        minute_bars: [BarData] = []
        while startDate <= today:
            print("Historical Data: %s - %s" % (stock.symbol, startDate))
            endtime = startDate+timedelta(days=1)
            bars: [BarData] = self.ib.reqHistoricalData(stock, endDateTime=endtime, 
                                                    durationStr='5 D', 
                                                    barSizeSetting='1 min', 
                                                    whatToShow='TRADES',
                                                    useRTH=True,
                                                    formatDate=1)
            startDate = startDate+timedelta(days=6)
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
        # stocks = [Stock("AAPL", "SMART", "USD")]
        total = len(stocks)
        current = 0
        for stock in stocks:
            current += 1
            sys.stdout.write("\t Contracts: %i/%i \r" % (current, total) )
            if current <= total-1:
                sys.stdout.flush()
            else:
                print("")

            mBars, dBars = self.downloadHistoricDataFromIB(stock, 365)
            # current = None
            # for bar in mBars:
            #     newDate = bar.date.replace(microsecond=0, tzinfo=None).date()
            #     if not current or current != newDate:
            #         current = newDate
            #         print(bar.date)
            models = self.createListOfBackTestModels(stock, mBars, dBars)
            self.saveDataInCSVFile(stock.symbol, models)

if __name__ == '__main__':
    try:
        backtest = BackTest()
        #backtest.downloadStocksToCSVFile()
        backtest.run()
    except (KeyboardInterrupt, SystemExit):
        None