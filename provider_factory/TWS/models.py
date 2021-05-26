from datetime import datetime, timedelta
from typing import List

from ib_insync.objects import BarData
from ib_insync import IB, IBC, Stock

from models.base_models import Contract, Event
from configs.models import Provider, ProviderConfigs
from provider_factory.models import ProviderClient, ProviderController

class TWSClient(ProviderClient):
    @property
    def client(self):
        model: IB = self.session
        return model

    def __init__(self, providerConfigs: ProviderConfigs) -> None:
        super().__init__()
        self.provider = Provider.TWS
        self.providerConfigs = providerConfigs
        ib = IB()
        self.session = ib

    def run(self):
        self.client.run()

    def connect(self):
        self.client.connect(self.providerConfigs.endpoint, self.providerConfigs.port, self.providerConfigs.clientID)
    
    async def connectAsync(self):
        await self.client.connectAsync(self.providerConfigs.endpoint, self.providerConfigs.port, self.providerConfigs.clientID)

    def downloadHistoricalData(self, contract: Contract, days: int, barSize: str) -> List[Event]:
        return self.requestHistoricalData(False, contract, days, barSize)

    async def downloadHistoricalDataAsync(self, contract: Contract, days: int, barSize: str) -> List[Event]:
        return self.requestHistoricalData(True, contract, days, barSize)

    def requestHistoricalData(self, isAsync: bool, contract: Contract, days: int, barSize: str) -> List[Event]:
        if contract is None:
            return []
        nDays = days
        nYears = int(nDays/365)
        durationDays = ("%d D" % (nDays+10)) if nDays < 365 else ("%d Y" % nYears)
        today = datetime.now().replace(microsecond=0, tzinfo=None).date()
        startDate = today-timedelta(days=nDays+1)
        stock = Stock(contract.symbol, contract.exchange, contract.currency)
        
        bars: List[BarData] = []
        minute_bars: List[BarData] = []
        if barSize.endswith('min'):
            while startDate <= today:
                endtime = startDate+timedelta(days=1)
                if isAsync:
                    bars: List[BarData] = self.client.reqHistoricalDataAsync(stock, endDateTime=endtime, 
                                                            durationStr='5 D', 
                                                            barSizeSetting=barSize, 
                                                            whatToShow='TRADES',
                                                            useRTH=True,
                                                            formatDate=1)
                else:
                    bars: List[BarData] = self.client.reqHistoricalData(stock, endDateTime=endtime, 
                                                        durationStr='5 D', 
                                                        barSizeSetting=barSize, 
                                                        whatToShow='TRADES',
                                                        useRTH=True,
                                                        formatDate=1)
            
                startDate = startDate+timedelta(days=6)
                minute_bars += bars
        else:
            if isAsync:
                bars: List[BarData] = self.client.reqHistoricalDataAsync(stock, endDateTime='', 
                                                        durationStr=durationDays, 
                                                        barSizeSetting=barSize, 
                                                        whatToShow='TRADES',
                                                        useRTH=True,
                                                        formatDate=1)
            else:
                bars: List[BarData] = self.client.reqHistoricalData(stock, endDateTime='', 
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