from datetime import *
from ib_insync import IB, Ticker as ibTicker, Contract as ibContract, Order as ibOrder, LimitOrder, StopOrder, Position as ibPosition, BarData

class HistoricalData:

    async def getAverageVolume(self, ib: IB, stock: ibContract, days: int = 5):
        minute_bars = await self.downloadHistoricDataFromIB(ib=ib, stock=stock, days=days)
        return self.calculateAverageVolume(minute_bars)

    async def downloadHistoricDataFromIB(self, ib: IB, stock: ibContract, days: int = 5) -> [BarData]:
        nDays = days
        today = datetime.now().replace(microsecond=0, tzinfo=None).date()
        startDate = today-timedelta(days=nDays+1)
        
        minute_bars: [BarData] = []
        while startDate <= today:
            endtime = startDate+timedelta(days=1)
            bars: [BarData] = await ib.reqHistoricalDataAsync(stock, endDateTime=endtime, 
                                                    durationStr='5 D', 
                                                    barSizeSetting='1 min', 
                                                    whatToShow='TRADES',
                                                    useRTH=True,
                                                    formatDate=1)
            startDate = startDate+timedelta(days=6)
            minute_bars += bars
        
        return minute_bars

    def calculateAverageVolume(self, datas: [BarData]):
        nBars = len(datas)
        if nBars > 0:
            sum = 0
            for data in datas: 
                sum += data.volume
            
            return sum/nBars
        else:
            return None