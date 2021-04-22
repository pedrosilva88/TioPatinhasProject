import os, sys
import csv
from ib_insync import Contract as ibContract, Stock as ibStock

class Scanner:
    stocksDownloaded: [ibStock]
    stocks: [ibStock]

    def __init__(self):
        self.tickersDownloaded = []
        self.tickers = []

    def getOPGRetailers(self, path: str, nItems: int):
        modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
        datapath = os.path.join(modpath, path)
        stocks = []
        
        with open(datapath) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count > 0:
                    stocks.append(ibStock(row[0], row[1], row[2]))
                line_count += 1
        
        if nItems > 0:
            self.stocksDownloaded = stocks[:nItems]
            self.stocks = stocks[:nItems]
        else:
            self.stocksDownloaded = stocks
            self.stocks = stocks

    def removeTicker(self, symbol: str):
        ticker = [d for d in self.stocks if d.symbol == symbol].pop()
        self.stocks.remove(ticker)