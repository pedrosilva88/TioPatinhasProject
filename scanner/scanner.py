from country_config.market_manager import Constants
from country_config.country_manager import getCountryFromCurrency
import os, sys
import csv
from models.base_models import Contract

class Scanner:
    def contratcsFrom(path= str):
        modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
        datapath = os.path.join(modpath, path)
        contracts = []
        
        with open(datapath) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count > 0:
                    contracts.append(Contract(row[0], getCountryFromCurrency(row[2]), row[1]))
                line_count += 1
        
        return contracts        

    # Isto nao devia ser preciso. Ter um method de instancia
    def removeTicker(self, symbol: str):
        ticker = [d for d in self.stocks if d.symbol == symbol].pop()
        self.stocks.remove(ticker)

    def getPathFor(provider: str, 
                    strategy: str, 
                    country: str, 
                    filename: str = "scan_to_run_startegy.csv") -> str:
        return ("%s/%s/%s/%s/%s" % (Constants.rootPath, provider, strategy, country, filename))

    class Constants:
        rootPath = "scanner/Data/CSV"