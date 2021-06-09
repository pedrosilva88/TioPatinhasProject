from datetime import date, datetime
import sys
from typing import List, Tuple, Union
from backtest.models.base_models import ContractSymbol
from models.base_models import Contract, Event
from provider_factory.models import ProviderClient

class BacktestDownloadModule:
    def downloadStocks(client: ProviderClient, stocks: List[Contract], days: int, barSize: str) -> Union[ContractSymbol, Tuple[Contract, List[Event]]]:
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
        return dic

    def downloadStock(client: ProviderClient, stock: Contract, days: int, barSize: str, endDate: date = datetime.today()) -> List[Event]:
        return client.downloadHistoricalData(stock, days, barSize, endDate)
        