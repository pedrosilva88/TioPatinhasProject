import sys
from typing import List
from models.base_models import Contract
from provider_factory.models import ProviderClient

class BacktestDownloadModule:
    def downloadStocks(client: ProviderClient, stocks: List[Contract], days: int, barSize: str):
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

            bars = client.downloadHistoricalData(stock, days, barSize)
            dic[stock.symbol] = (stock, bars)

        