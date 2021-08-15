from country_config.country_manager import getCountryFromCode
from strategy.configs.models import StrategyType
from country_config.models import Country
from datetime import date, datetime
from typing import Tuple
    
def stringToDate(dateStr: str):
    return datetime.strptime(dateStr, '%y/%m/%d').date()

class FillDB:
    symbol: str
    date: date
    country: Country
    strategy: StrategyType

    def __init__(self, symbol: str, date: date, country: Country, strategy: StrategyType):
        self.symbol = symbol
        self.date = date
        self.country = country
        self.strategy = strategy

    def init_from_db(row: Tuple[int, str, str, str, str]):
        return FillDB(symbol=row[1], 
                        date=stringToDate(row[2]), 
                        country=getCountryFromCode(code=row[3]),
                        strategy=StrategyType.strategyFromCode(code=row[4]))

    @property
    def sqlFormat(self):
        return (self.symbol, self.dateToString, self.country.code, self.strategy.value)

    @property
    def dateToString(self):
        return self.date.strftime('%y/%m/%d')