import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from ib_insync import *
from datetime import datetime
from IPython.display import display, clear_output
import pandas as pd
from strategy import * #StrategyOPG, StrategyData, StrategyResult, StrategyResultType

class BackTest():

    def __init__(self):
        util.startLoop()
        self.ib = IB()
        self.ib.connect('127.0.0.1', 7497, clientId=15)
        self.strategy = StrategyOPG()

    def run(self):
        stock = Stock("VUZI", "SMART", "USD")        
        minute_bars: [BarData] = self.ib.reqHistoricalData(stock, endDateTime='', 
                                                durationStr='5 D', 
                                                barSizeSetting='1 min', 
                                                whatToShow='TRADES',
                                                useRTH=True,
                                                formatDate=1)

        day_bars: [BarData] = self.ib.reqHistoricalData(stock, endDateTime='', 
                                                durationStr='6 D', 
                                                barSizeSetting='1 day', 
                                                whatToShow='TRADES',
                                                useRTH=True,
                                                formatDate=1)

        tickers = []
        for mBar in minute_bars:
            barYstd, barToday = self.getDayBar(mBar.date, day_bars)
            ticker = Ticker(contract=stock, 
                            time=mBar.date, 
                            close=barYstd.close, 
                            open=barToday.open,
                            bid=mBar.average, 
                            ask=mBar.average, 
                            last=mBar.average,
                            volume=mBar.volume)
            tickers.append(ticker)


        for ticker in tickers:
            data = StrategyData(ticker, 
                                None, 
                                None, 
                                2000)
            result = self.strategy.run(data)

            if (result.type == StrategyResultType.Buy or result.type == StrategyResultType.Sell):
                print(result)

            elif (result.type == StrategyResultType.StrategyDateWindowExpired or result.type == StrategyResultType.DoNothing):
                None
                #print(result)

            elif (result.type == StrategyResultType.PositionExpired_Buy or result.type == StrategyResultType.PositionExpired_Sell):
                orderAction = OrderAction.Buy.value if result.type == StrategyResultType.PositionExpired_Buy else OrderAction.Sell.value
                print(result)

            elif result.type == StrategyResultType.KeepOrder:
                print(result)

            elif (result.type == StrategyResultType.CancelOrder or result.type == StrategyResultType.StrategyDateWindowExpiredCancelOrder):
                None
                #print(result)
            

    def getDayBar(self, date: datetime, bars: [BarData]):
        for i in range(len(bars)):
            if date.replace(microsecond=0, tzinfo=None).date() == bars[i].date:
                return bars[i-1], bars[i]

if __name__ == '__main__':
    try:
        backtest = BackTest()
        backtest.run()
    except (KeyboardInterrupt, SystemExit):
        None