import os, sys
import csv
from models.base_models import Contract

class Scanner:
    def stocksFrom(path= str):
        modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
        datapath = os.path.join(modpath, path)
        stocks = []
        
        with open(datapath) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count > 0:
                    stocks.append(Contract(row[0], row[1], row[2]))
                line_count += 1
        
        return stocks            

    def removeTicker(self, symbol: str):
        ticker = [d for d in self.stocks if d.symbol == symbol].pop()
        self.stocks.remove(ticker)