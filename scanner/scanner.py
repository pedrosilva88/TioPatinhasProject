import os, sys
import csv
from ib_insync import Contract as ibContract, Stock as ibStock

class Scanner:
    stocksDownloaded: [ibStock]
    stocks: [ibStock]

    def __init__(self):
        self.tickersDownloaded = []
        self.tickers = []

    def getOPGRetailers(self):
        modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
        datapath = os.path.join(modpath, 'scanner/Data/CSV/OPG_Retails_SortFromBackTest.csv')
        stocks = []
        
        with open(datapath) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count > 0:
                    stocks.append(ibStock(row[0], row[1], row[2]))
                line_count += 1
        
        self.stocksDownloaded = stocks[:80]
        self.stocks = stocks[:80]

        # self.stocksDownloaded = [ibStock("CABK", "SMART", "EUR")]
        # self.stocks = [ibStock("CABK", "SMART", "EUR")]

    def getTicker(self, symbol: str):
        ticker = [d for d in self.stocks if d.symbol == symbol].pop()
        return ticker