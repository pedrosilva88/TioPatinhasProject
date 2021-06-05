from datetime import datetime
from typing import List
from yahoo_earnings_calendar import YahooEarningsCalendar
from helpers import *
from models.base_models import Contract

class EarningsCalendar():
    yec: YahooEarningsCalendar

    def __init__(self):
        self.yec = YahooEarningsCalendar(0.8)

    def requestEarnings(self, contracts: List[Contract], callback):
        total = len(contracts)
        current = 0
        for contract in contracts:
            try:
                current +=1
                logCounter("Earnings", total, current)

                timeinterval = self.yec.get_next_earnings_date(contract.symbol)
                nextEarningDate = datetime.utcfromtimestamp(timeinterval)
                callback(contract, nextEarningDate)
            except Exception as e:
                print(e)
            
