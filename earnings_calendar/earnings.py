from datetime import datetime
from ib_insync import Contract as ibContract
from yahoo_earnings_calendar import YahooEarningsCalendar

class EarningsCalendar():
    yec: YahooEarningsCalendar

    def __init__(self):
        self.yec = YahooEarningsCalendar(0.2)

    def requestEarnings(self, contracts: [ibContract], callback):
        for contract in contracts:
            try:
                timeinterval = self.yec.get_next_earnings_date(contract.symbol)
                nextEarningDate = datetime.utcfromtimestamp(timeinterval)
                callback(contract, nextEarningDate)
            except Exception as e:
                print(e)
            
