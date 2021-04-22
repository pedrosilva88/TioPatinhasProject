import os, sys
import os.path
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import csv
import distutils.util
from enum import Enum
from ib_insync import *
from datetime import datetime, date, timedelta, time
from helpers import log, utcToLocal
from country_config import CountryConfig, CountryKey, getConfigFor
from scanner import Scanner

class BackTestModel():
    ticker: Ticker
    averageVolume: float
    volumeInFirstMinuteBar: float
    openPrice: float
    close: float
    bid: float
    ask: float
    last: float
    volume: float
    symbol: str
    zigzag: bool
    rsi: float
    dateString: str

    def __init__(self, openPrice: float,
                        close: float,
                        bid: float,
                        ask: float,
                        last: float,
                        volume: float,
                        symbol: str,
                        zigzag: bool,
                        rsi: float,
                        dateString: str, avgVolume: float, volumeFirstMinuteBar: float):
        self.openPrice = openPrice
        self.close = close
        self.bid = bid
        self.ask = ask
        self.last = last
        self.volume = volume
        self.symbol = symbol
        self.zigzag = zigzag
        self.rsi = rsi
        self.dateString = dateString
        self.averageVolume = avgVolume if avgVolume else 0
        self.volumeInFirstMinuteBar = volumeFirstMinuteBar if volumeFirstMinuteBar else 0

    def __str__(self):
        return ("%s - %s" % (self.dateString, self.symbol))

    def ticker(self, countryConfig):
        formatDate = "%Y-%m-%d %H:%M:%S"
        stock = Stock(self.symbol, "SMART", countryConfig.currency)
        customDate = self.dateString
        if ":00+" in self.dateString:
            customDate = self.dateString.split(":00+")[0]+":00"
        elif ":00-" in self.dateString:
            customDate = self.dateString.split(":00-")[0]+":00"

        newTime = utcToLocal(datetime.strptime(customDate, formatDate), countryConfig.timezone)
        return Ticker(contract=stock, 
                            time=newTime, 
                            close=self.close, 
                            open=self.openPrice,
                            bid=self.bid, 
                            ask=self.ask, 
                            last=self.last,
                            volume=self.volume)

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
    orderDate: date
    cash: float

    def __init__(self, symbol: str, date: date, pnl, action: str, 
                type: BackTestResultType, priceCreateTrade: float, priceCloseTrade: float,
                size: int, averageVolume: float, volumeFirstMinute: float, totalInvested: float,
                openPrice: float, ystdClosePrice: float,
                cash: float, orderDate: date):
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
        self.cash = cash
        self.orderDate = orderDate

class BackTestDownloadModel():
    path: str
    numberOfDays: int
    barSize: str

    def __init__(self, path: str, numberOfDays: int, barSize: str):
        self.path = path
        self.numberOfDays = numberOfDays
        self.barSize = barSize

# Reports
class BackTestReport():
    results: [str, [BackTestResult]] = dict()
    trades: [str, [str]] = dict()
    stockPerformance = dict()

    def saveReportResultInFile(self, path: str, data:[[]]):
        name = ("%s/ResultsPnL.csv" % path)
        with open(name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "PnL", "Trades"])
            for model in data:
                writer.writerow(model)

    def saveReportTradesInFile(self, path: str, data:[[]], zigzag: bool = False):
        name = ("%s/ResultsTrades.csv" % path)
        with open(name, 'w', newline='') as file:
            writer = csv.writer(file)
            if zigzag:
                writer.writerow(["Date", "Symbol", "Result", "PnL", "Price CreateTrade", "Price CloseTrade", "Size", "Order Date", "Total Invested", "Open Price", "YSTD Close Price", "Action", "Cash"])
            else:
                writer.writerow(["Date", "Symbol", "Result", "PnL", "Price CreateTrade", "Price CloseTrade", "Size", "Avg Volume",  "Volume 1st minute", "Total Invested", "Open Price", "YSTD Close Price", "Action", "Cash"])
            for model in data:
                writer.writerow(model)

    def saveReportPerformance(self, path: str, stocksPath: str, data, countryConfig: CountryConfig):
        scanner = Scanner()
        scanner.getOPGRetailers(path=stocksPath, nItems=0)
        stocks = scanner.stocks
        name = ("%s/ResultsStockPerformance.csv" % path)
        with open(name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Symbol", "Exchange", "Currency", "OPGs Found", "Take Profit", "Profit", "StopLoss", "Loss", "Wins", "%"])
            for key, item in data.items():
                total = item[0]+item[1]+item[2]+item[3]
                wins = item[0]+item[1]
                writer.writerow([key,
                                "SMART",
                                countryConfig.currency,
                                total,
                                item[0],
                                item[1],
                                item[2],
                                item[3],
                                wins,
                                (wins/total)*100])
                item = list(filter(lambda x : x.symbol == key, stocks)).pop()
                stocks.remove(item)
            for item in stocks:
                writer.writerow([item.symbol,
                                "SMART",
                                countryConfig.currency,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0])

    def showReport(self, path: str, zigzag: bool = False):
        items = [[]]
        for key, array in self.results.items():
            total = 0
            for item in array:
                total += item.pnl
            items.append([key, total, len(array)])
            print("%s: %.2f€ %d" % (key, total, len(array)))

        self.saveReportResultInFile(path, items)

        items = [[]]
        for key, array in self.trades.items():
            for item in array:
                items.append(item)

        self.saveReportTradesInFile(path, items, zigzag)

    def showPerformanceReport(self, path: str, stocksPath: str, countryConfig: CountryConfig):
        self.saveReportPerformance(path, stocksPath, self.stockPerformance, countryConfig)

    def updateResults(self, key: str, value: BackTestResult):
        if key in self.results:
            self.results[key].append(value)
        else:
            self.results[key] = [value]

    def updateTrades(self, key: str, ticker: Ticker, result: BackTestResult, zigzag: bool = False):
        resultArray = []
        resultArray.append(key) # date
        resultArray.append(ticker.contract.symbol) # symbol
        resultArray.append(result.type.emoji()) # ✅ or ✅ ✅ or ❌  or ❌ ❌
        resultArray.append(result.pnl) # PnL
        resultArray.append(result.priceCreateTrade) # Price CreateTrade
        resultArray.append(result.priceCloseTrade) # Price CloseTrade
        resultArray.append(result.size) # Size
        
        if zigzag:
            resultArray.append(result.orderDate) # Order Date
        else:
            resultArray.append(result.volumeFirstMinute) # VolumeFirstMinute
            resultArray.append(result.averageVolume) # AverageVolume
            
        resultArray.append(result.totalInvested) # Total Invested
        resultArray.append(result.openPrice) # Open Price
        resultArray.append(result.ystdClosePrice) # YSTD Close Price
        resultArray.append(result.action) # Action Long or Short
        resultArray.append(result.cash) # Cash
        
        if key in self.trades:
            self.trades[key].append(resultArray)
        else:
            self.trades[key] = [resultArray]

    def updateStockPerformance(self, ticker: Ticker, type: BackTestResultType):
        array = []
        if ticker.contract.symbol in self.stockPerformance:
            array = self.stockPerformance[ticker.contract.symbol]
        else:
            array = [0,0,0,0]

        if type == BackTestResultType.takeProfit:
            array[0] += 1
        elif type == BackTestResultType.profit:
            array[1] += 1
        elif type == BackTestResultType.stopLoss:
            array[2] += 1
        elif type == BackTestResultType.loss:
            array[3] += 1

        self.stockPerformance[ticker.contract.symbol] = array


# Download Stocks Data

def downloadStocksData(ib: IB, model: BackTestDownloadModel) -> [str, (Stock, [BarData])]:
    scanner = Scanner()
    scanner.getOPGRetailers(path=model.path, nItems=0)
    stocks = scanner.stocks
    total = len(stocks)
    current = 0
    dic = dict()
    for stock in stocks:
        current += 1
        sys.stdout.write("\t Contracts: %i/%i \r" % (current, total) )
        if current <= total-1:
            sys.stdout.flush()
        else:
            print("")

        bars = downloadHistoricDataFromIB(ib, stock, model)
        dic[stock.symbol] = (stock, bars)
        #dBars = self.downloadHistoricDataFromIB(stock, model)
        #models = self.createListOfBackTestModels(stock, mBars, dBars)
        #self.saveDataInCSVFile(stock.symbol, models)
    return dic

def downloadHistoricDataFromIB(ib: IB, stock: Contract, model: BackTestDownloadModel) -> [BarData]:
    nDays = model.numberOfDays
    xYears = int(nDays/365)
    durationDays = ("%d D" % (nDays+10)) if nDays < 365 else ("%d Y" % xYears)
    today = datetime.now().replace(microsecond=0, tzinfo=None).date()
    startDate = today-timedelta(days=nDays+1)
    
    bars: [BarData] = []
    if model.barSize.endswith('min'):
        while startDate <= today:
            print("Historical Data: %s - %s" % (stock.symbol, startDate))
            endtime = startDate+timedelta(days=1)
            bars: [BarData] = ib.reqHistoricalData(stock, endDateTime=endtime, 
                                                    durationStr='5 D', 
                                                    barSizeSetting=model.barSize, 
                                                    whatToShow='TRADES',
                                                    useRTH=True,
                                                    formatDate=1)
            startDate = startDate+timedelta(days=6)
            minute_bars += bars
    else:
        bars: [BarData] = ib.reqHistoricalData(stock, endDateTime='', 
                                                durationStr=durationDays, 
                                                barSizeSetting=model.barSize, 
                                                whatToShow='TRADES',
                                                useRTH=True,
                                                formatDate=1)
    
    return bars

# Save

def saveDataInCSVFile(filename: str, path: str, data: [BackTestModel], countryConfig: CountryConfig):
    name = ("backtest/Data/CSV/%s/%s/%s.csv" % (countryConfig.key.code,path, filename))
    with open(name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Symbol", "Date", "Close", "Open", "Bid", "Ask", "Last", "Volume", "AvgVolume", "VolumeFirstMinute", "ZigZag", "RSI"])
        for model in data:
            ticker = model.ticker(countryConfig)
            volumeMinute = None if not model.volumeInFirstMinuteBar else round(model.volumeInFirstMinuteBar, 2)
            averageVolume = None if not model.averageVolume else round(model.averageVolume, 2)
            openPrice = 0 if not ticker.open else round(ticker.open, 2)
            close = 0 if not ticker.close else round(ticker.close, 2)
            bid = 0 if not ticker.bid else round(ticker.bid, 2)
            ask = 0 if not ticker.ask else round(ticker.ask, 2)
            last = 0 if not ticker.last else round(ticker.last, 2)
            volume = None if not ticker.volume else round(ticker.volume, 2)
            zigzag = False if model.zigzag is None else model.zigzag
            rsi = None if model.rsi is None else round(model.rsi, 2)
            writer.writerow([ticker.contract.symbol, 
                            ticker.time, 
                            close, 
                            openPrice, 
                            bid, 
                            ask, 
                            last, 
                            volume, 
                            averageVolume, 
                            volumeMinute,
                            zigzag,
                            rsi])

# Load

def loadFiles(pathToScan: str, countryConfig: CountryConfig):
    scanner = Scanner()
    scanner.getOPGRetailers(path=pathToScan, nItems=0)
    stocks = scanner.stocks

    total = len(stocks)
    current = 0
    models = []
    for stock in stocks:
        current += 1
        sys.stdout.write("\t Fetching CSV Files: %i/%i \r" % (current, total) )
        if current <= total-1:
            sys.stdout.flush()
        else:
            print("")

        name = ("backtest/Data/CSV/%s/ZigZag/%s.csv" % (countryConfig.key.code, stock.symbol))
        if not os.path.isfile(name):
            print("File not found ", name)
            continue
        models += getModelsFromCSV(name)
    print("Sort all Ticks by date")
    models.sort(key=lambda x: x.dateString, reverse=False)
    return models

def getModelsFromCSV(filePath: str):
    formatDate = "%Y-%m-%d %H:%M:%S"
    models = []
    with open(filePath) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                volumeMinute = None if not row[9] else float(row[9])
                averageVolume = None if not row[8] else float(row[8])
                openPrice = 0 if not row[3] else float(row[3])
                close = 0 if not row[2] else float(row[2])
                bid = 0 if not row[4] else float(row[4])
                ask = 0 if not row[5] else float(row[5])
                last = 0 if not row[6] else float(row[6])
                volume = 0 if not row[7] else float(row[7])
                zigzag = False if not row[10] else bool(distutils.util.strtobool(row[10]))
                rsi = 0 if not row[11] else float(row[11])
                models.append(BackTestModel(openPrice, close, bid, ask, last, volume, row[0], zigzag, rsi, row[1], averageVolume, volumeMinute))
            line_count += 1
    return models

# if __name__ == '__main__':
#     try:
#         backtest = BackTest(countryKey=CountryKey.USA)
#         #backtest.downloadStocksToCSVFile()
#         backtest.run()
#         #backtest.runStockPerformance()
#     except (KeyboardInterrupt, SystemExit):
#         None