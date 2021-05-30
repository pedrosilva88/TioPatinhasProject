from datetime import date, datetime, timedelta
from os import name
from typing import List

from ib_insync.objects import BarData
from ib_insync import IB, IBC, Stock

from models.base_models import Contract, Event
from configs.models import Provider, ProviderConfigs
from provider_factory.models import ProviderClient, ProviderController

class TWSClient(ProviderClient):
    @property
    def client(self) -> IB :
        return self.session

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
        if contract is None:
            return []

        configs = TWSClient.HistoricalRequestConfigs(contract, days, barSize)
        allBars: List[BarData] = []

        while configs.startDate <= configs.today:
            endtime = configs.startDate+timedelta(days=1) if barSize.endswith('min') else ''
            bars: List[BarData] = self.client.reqHistoricalData(configs.stock, endDateTime=endtime, 
                                                durationStr=configs.durationStr, 
                                                barSizeSetting=barSize, 
                                                whatToShow='TRADES',
                                                useRTH=True,
                                                formatDate=1)
            configs.startDate = configs.startDate+timedelta(days=6)
            allBars += bars

        events = []
        for bar in allBars:
            events.append(Event(contract, bar.date, bar.open, bar.close, bar.high, bar.low, bar.volume))
        return events

    async def downloadHistoricalDataAsync(self, contract: Contract, days: int, barSize: str) -> List[Event]:
        if contract is None:
            return []

        configs = TWSClient.HistoricalRequestConfigs(contract, days, barSize)
        allBars: List[BarData] = []

        while configs.startDate <= configs.today:
            endtime = configs.startDate+timedelta(days=1) if barSize.endswith('min') else ''
            bars: List[BarData] = await self.client.reqHistoricalDataAsync(configs.stock, endDateTime=endtime, 
                                                    durationStr=configs.durationStr, 
                                                    barSizeSetting=barSize, 
                                                    whatToShow='TRADES',
                                                    useRTH=True,
                                                    formatDate=1)
            configs.startDate = configs.startDate+timedelta(days=6)
            allBars += bars

        events = []
        for bar in allBars:
            events.append(Event(contract, bar.date, bar.open, bar.close, bar.high, bar.low, bar.volume))
        return events

    class HistoricalRequestConfigs:
        nDays: int
        nYears: int
        durationsDays: str
        today: date
        startDate: date
        stock: Stock
        durationStr: str

        def __init__(self, contract: Contract, days: int, barSize: str) -> None:
            super().__init__()
            self.nDays = days
            self.nYears = int(self.nDays/365)
            self.durationDays = ("%d D" % (self.nDays+10)) if self.nDays < 365 else ("%d Y" % self.nYears)
            self.today = datetime.now().replace(microsecond=0, tzinfo=None).date()
            self.startDate = self.today-timedelta(days=self.nDays+1) if barSize.endswith('min') else self.today
            self.stock = Stock(contract.symbol, contract.exchange, contract.currency)
            self.durationStr = '5 D' if barSize.endswith('min') else self.durationDays

class TWSController(ProviderController):
    def __init__(self, providerConfigs: ProviderConfigs) -> None:
        super().__init__()
        self.provider = Provider.TWS

        self.runner = IBC(version= providerConfigs.version, 
                            tradingMode= providerConfigs.tradingMode, 
                            userid= providerConfigs.user, 
                            password= providerConfigs.password)