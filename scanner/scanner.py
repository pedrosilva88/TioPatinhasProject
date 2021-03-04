import os, sys
import csv
from order import Ticker

class Scanner:
    tickersDownloaded: [Ticker]
    tickers: [Ticker]

    def __init__(self):
        self.tickersDownloaded = []
        self.tickers = []

    def getOPGRetailers(self):
        modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
        datapath = os.path.join(modpath, 'scanner/Data/CSV/OPG_Retails_SortFromBackTest.csv')
        #datapath = os.path.join(modpath, 'scanner/Data/CSV/OPG_Retails.csv')
        tickers = []
        
        with open(datapath) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                if line_count > 0:
                    tickers.append(Ticker(row[0], None))
        
        self.tickersDownloaded = tickers[:15]
        self.tickers = tickers[:15]

    def getTicker(self, symbol: str):
        ticker = [d for d in self.tickers if d.symbol == symbol].pop()
        return ticker