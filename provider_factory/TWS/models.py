from datetime import datetime, timedelta
from typing import List

from ib_insync.objects import BarData
from models.base_models import Contract, Event
from ib_insync import IB, IBC, Stock
from configs.models import Provider, ProviderConfigs
from provider_factory.models import ProviderClient, ProviderController

class TWSClient(ProviderClient):
    def __init__(self, providerConfigs: ProviderConfigs) -> None:
        super().__init__()
        self.provider = Provider.TWS

        ib = IB()
        ib.connect(providerConfigs.endpoint, providerConfigs.port, clientId=providerConfigs.clientID)
        ib.run()
        self.session = ib

    async def downloadHistoricalData(self, contract: Contract, days: int, barSize: str) -> List[Event]:
        ib: IB = self.session
        if contract is None:
            return []
        print("BLI")
        nDays = days
        nYears = int(nDays/365)
        durationDays = ("%d D" % (nDays+10)) if nDays < 365 else ("%d Y" % nYears)
        today = datetime.now().replace(microsecond=0, tzinfo=None).date()
        startDate = today-timedelta(days=nDays+1)
        stock = Stock(contract.symbol, contract.currency, contract.currency)
        
        bars: List[BarData] = []
        minute_bars: List[BarData] = []
        if barSize.endswith('min'):
            while startDate <= today:
                endtime = startDate+timedelta(days=1)
                bars: List[BarData] = await ib.reqHistoricalDataAsync(stock, endDateTime=endtime, 
                                                        durationStr='5 D', 
                                                        barSizeSetting=barSize, 
                                                        whatToShow='TRADES',
                                                        useRTH=True,
                                                        formatDate=1)
                startDate = startDate+timedelta(days=6)
                minute_bars += bars
        else:
            bars: List[BarData] = await ib.reqHistoricalDataAsync(stock, endDateTime='', 
                                                    durationStr=durationDays, 
                                                    barSizeSetting=barSize, 
                                                    whatToShow='TRADES',
                                                    useRTH=True,
                                                    formatDate=1)
        events = []
        
        for bar in bars:
            events.append(Event(contract, bar.date, bar.open, bar.close, bar.high, bar.low, bar.volume))
        return events


class TWSController(ProviderController):
    def __init__(self, providerConfigs: ProviderConfigs) -> None:
        super().__init__()
        self.provider = Provider.TWS

        self.runner = IBC(version= providerConfigs.version, 
                            tradingMode= providerConfigs.tradingMode, 
                            userid= providerConfigs.user, 
                            password= providerConfigs.password)