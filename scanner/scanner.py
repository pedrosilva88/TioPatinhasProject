import os, sys
import csv

class Scanner:
    tickersDownloaded: [str]
    tickers: [str]

    def __init__(self):
        self.tickersDownloaded = []
        self.tickers = []

    def getOPGRetailers(self):
        modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
        datapath = os.path.join(modpath, 'scanner/Data/CSV/OPG_Retails.csv')
        tickers = []
        
        with open(datapath) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                else:
                    tickers.append(row[0])
                    line_count += 1
        
        self.tickersDownloaded = tickers[:15]
        self.tickers = tickers[:15]
        
        # self.tickersDownloaded = ['WMT']
        # self.tickers = ['WMT']

        #return ['BIMI', 'COST', 'WMT', 'TJX', 'TGT']