import os, sys
import os.path
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import csv
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
    dateString: str

    def __init__(self, openPrice: float,
                        close: float,
                        bid: float,
                        ask: float,
                        last: float,
                        volume: float,
                        symbol: str,
                        dateString: str, avgVolume: float, volumeFirstMinuteBar: float):
        self.openPrice = openPrice
        self.close = close
        self.bid = bid
        self.ask = ask
        self.last = last
        self.volume = volume
        self.symbol = symbol
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
    cash: float

    def __init__(self, symbol: str, date: date, pnl, action: str, 
                type: BackTestResultType, priceCreateTrade: float, priceCloseTrade: float,
                size: int, averageVolume: float, volumeFirstMinute: float, totalInvested: float,
                openPrice: float, ystdClosePrice: float,
                cash: float):
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

class BackTestDownloadModel():
    path: str
    numberOfDays: int
    barSize: str

    def __init__(self, path: str, numberOfDays: int, barSize: str):
        self.path = path
        self.numberOfDays = numberOfDays
        self.barSize = barSize

# Download Stocks Data

def downloadStocksData(ib: IB, model: BackTestDownloadModel) -> [str, (Stock, [BarData])]:
    scanner = Scanner()
    scanner.getOPGRetailers(path=model.path, nItems=1)
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
    durationDays = ("%d D" % (nDays+10)) if nDays < 365 else "1 Y"
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

def saveDataInCSVFile(filename: str, data: [BackTestModel], countryConfig: CountryConfig):
    name = ("backtest/Data/CSV/%s/%s.csv" % (countryConfig.key.code, filename))
    with open(name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Symbol", "Date", "Close", "Open", "Bid", "Ask", "Last", "Volume", "AvgVolume", "VolumeFirstMinute"])
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
            writer.writerow([ticker.contract.symbol, 
                            ticker.time, 
                            close, 
                            openPrice, 
                            bid, 
                            ask, 
                            last, 
                            volume, 
                            averageVolume, 
                            volumeMinute])

# if __name__ == '__main__':
#     try:
#         backtest = BackTest(countryKey=CountryKey.USA)
#         #backtest.downloadStocksToCSVFile()
#         backtest.run()
#         #backtest.runStockPerformance()
#     except (KeyboardInterrupt, SystemExit):
#         None