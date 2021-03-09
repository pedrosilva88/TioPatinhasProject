import sys
from datetime import datetime
from ib_insync import Contract as ibContract
from yahoo_earnings_calendar import YahooEarningsCalendar

class EarningsCalendar():
    yec: YahooEarningsCalendar

    def __init__(self):
        self.yec = YahooEarningsCalendar(0.8)

    def requestEarnings(self, contracts: [ibContract], callback):
        total = len(contracts)
        current = 0
        for contract in contracts:
            try:
                current +=1
                sys.stdout.write("\t Contracts: %i/%i \r" % (current, total) )
                if current <= total-1:
                    sys.stdout.flush()
                else:
                    print("")

                timeinterval = self.yec.get_next_earnings_date(contract.symbol)
                nextEarningDate = datetime.utcfromtimestamp(timeinterval)
                callback(contract, nextEarningDate)
            except Exception as e:
                None
            
