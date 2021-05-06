import datetime
from datetime import date
    
def stringToDate(dateStr: str):
    return datetime.datetime.strptime(dateStr, '%y/%m/%d').date()

class FillDB:
    symbol: str
    date: date

    def __init__(self, symbol: str, date: date):
        self.symbol = symbol
        self.date = date

    def init_from_db(row: (int, str, str)):
        return FillDB(symbol=row[1], date=stringToDate(row[2]))

    @property
    def sqlFormat(self):
        return (self.symbol, self.dateToString)

    @property
    def dateToString(self):
        return self.date.strftime('%y/%m/%d')