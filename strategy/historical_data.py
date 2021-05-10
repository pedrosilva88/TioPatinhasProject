from datetime import *
from ib_insync import IB, Ticker as ibTicker, Contract as ibContract, Order as ibOrder, LimitOrder, StopOrder, Position as ibPosition, BarData, BarDataList, ContractDetails, PriceIncrement, util
from zigzag import *
from models import CustomBarData

class HistoricalData:

    async def getAverageVolume(self, ib: IB, stock: ibContract, days: int = 5):
        minute_bars = await self.downloadHistoricDataFromIB(ib=ib, stock=stock, days=days)
        value = self.calculateAverageVolume(minute_bars)
        return value

    async def downloadHistoricDataFromIB(self, ib: IB, stock: ibContract, days: int = 5, barSize = "1 min") -> [BarData]:
        nDays = days
        xYears = int(nDays/365)
        durationDays = ("%d D" % (nDays+10)) if nDays < 365 else ("%d Y" % xYears)
        today = datetime.now().replace(microsecond=0, tzinfo=None).date()
        startDate = today-timedelta(days=nDays+1)
        
        bars: [BarData] = []
        if barSize.endswith('min'):
            while startDate <= today:
                endtime = startDate+timedelta(days=1)
                bars: [BarData] = await ib.reqHistoricalDataAsync(stock, endDateTime=endtime, 
                                                        durationStr='5 D', 
                                                        barSizeSetting=barSize, 
                                                        whatToShow='TRADES',
                                                        useRTH=True,
                                                        formatDate=1)
                startDate = startDate+timedelta(days=6)
                minute_bars += bars
        else:
            bars: [BarData] = await ib.reqHistoricalDataAsync(stock, endDateTime='', 
                                                    durationStr=durationDays, 
                                                    barSizeSetting=barSize, 
                                                    whatToShow='TRADES',
                                                    useRTH=True,
                                                    formatDate=1)
        return bars

    def createListOfCustomBarsData(self, bars: [BarData]):
        zigzagValues, rsiValues = self.calculateRSIAndZigZag(bars)

        if zigzagValues is None or rsiValues is None:
            return []

        customBarsData = []
        i = 0
        for bar in bars:
            zigzag = True if zigzagValues[i] != 0 else False
            rsi = None
            if i > 0:
                rsi = rsiValues[i-1]

            barData = BarData(date=bar.date,
                                open=bar.open,
                                high=bar.high,
                                low=bar.low,
                                close=bar.close,
                                volume=bar.volume)
            
            customBarsData.append(CustomBarData(barData, zigzag, rsi))
            i += 1

        return customBarsData

    def calculateRSIAndZigZag(self, bars: [BarData]):
        try:
            closes = util.df(bars)['close']
            lows = util.df(bars)['low']
            highs = util.df(bars)['high']
            RSI = self.computeRSI(util.df(bars)['close'], 14)
            pivots = peak_valley_pivots_candlestick(closes.values, highs.values, lows.values, 0.05, -0.05)
            return pivots, RSI.values
        except TypeError as e:
            print(e)
            return None, None

    async def getContractDetails(self, ib: IB, stock: ibContract) -> (ContractDetails, [PriceIncrement]):
        contractDetails = await ib.reqContractDetailsAsync(stock)
        ruleId = contractDetails[0].marketRuleIds.split(',')[0]
        priceIncrementRules = await ib.reqMarketRuleAsync(ruleId)
        return (contractDetails, priceIncrementRules)
    
    def calculateAverageVolume(self, datas: [BarData]):
        nBars = len(datas)
        if nBars > 0:
            sum = 0
            for data in datas: 
                sum += data.volume
            
            return sum/nBars
        else:
            return None

    def computeRSI(self, data, time_window):
        diff = data.diff(1).dropna()

        up_chg = 0 * diff
        down_chg = 0 * diff
        
        up_chg[diff > 0] = diff[ diff>0 ]
        
        down_chg[diff < 0] = diff[ diff < 0 ]
        
        up_chg_avg   = up_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
        down_chg_avg = down_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
        
        rs = abs(up_chg_avg/down_chg_avg)
        rsi = 100 - 100/(1+rs)
        return rsi