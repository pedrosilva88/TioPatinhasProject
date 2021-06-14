from country_config.country_manager import getCountryFromCode, getCountryFromCurrency
from datetime import date, datetime, timedelta
from os import name
from typing import List
from asyncio.unix_events import SelectorEventLoop

from ib_insync.objects import BarData
from ib_insync import IB, IBC, Stock, client

from models.base_models import Contract, Event, Order, OrderAction, OrderType, Position, Trade
from configs.models import Provider, ProviderConfigs
from provider_factory.models import ProviderClient, ProviderController

class TWSClient(ProviderClient):
    @property
    def client(self) -> IB:
        return self.session

    def __init__(self, providerConfigs: ProviderConfigs) -> None:
        super().__init__()
        self.type = Provider.TWS
        self.providerConfigs = providerConfigs
        ib = IB()
        self.session = ib

    def run(self):
        self.client.run()

    def setTimeout(self):
        self.client.setTimeout(self.providerConfigs.appTimeout)

    def connect(self):
        self.client.connect(self.providerConfigs.endpoint, self.providerConfigs.port, self.providerConfigs.clientID)
    
    def disconnect(self):
        self.client.disconnect()

    async def connectAsync(self):
        await self.client.connectAsync(self.providerConfigs.endpoint, self.providerConfigs.port, self.providerConfigs.clientID, self.providerConfigs.connectTimeout)

    async def syncData(self):
        await self.client.accountSummaryAsync()
        await self.client.reqPositionsAsync()
        await self.client.reqAllOpenOrdersAsync()

    def positions(self) -> List[Position]:
        items = self.client.positions()
        positions = []
        for item in items:
            positions.append(Position(item.contract, item.position))
        return positions

    def trades(self) -> List[Trade]:
        items = self.client.openTrades()
        trades = []
        for item in items:
            price = item.order.auxPrice if item.order.orderType == OrderType.StopOrder else item.order.lmtPrice
            order = Order(OrderAction(item.order.action), OrderType(item.order.orderType), item.order.totalQuantity, price, item.order.parentId)
            country = getCountryFromCurrency(item.contract.currency)
            contract = Contract(item.contract.symbol, country, item.contract.exchange)
            trades.append(Trade(contract, order))
        return trades

    def cashBalance(self) -> float:
        for account in self.client.accountValues():
            if account.tag == "AvailableFunds":
                self.cashBalance = float(account.value)

    def currencyRateFor(self, currency: str) -> float:
        for account in self.client.accountValues():
            if (account.tag == "ExchangeRate" and account.currency == currency):
                return float(account.value)

    def downloadHistoricalData(self, contract: Contract, days: int, barSize: str, endDate: date = datetime.today()) -> List[Event]:
        if contract is None:
            return []

        configs = TWSClient.HistoricalRequestConfigs(contract, days, barSize, endDate)
        allBars: List[BarData] = []
        startDate = configs.startDate

        while startDate <= configs.endDate:
            endtime = '' 
            if barSize.endswith('min'):
                endtime = configs.startDate+timedelta(days=1)
            else:
                endtime = configs.endDate
            bars: List[BarData] = self.client.reqHistoricalData(configs.stock, endDateTime=endtime, 
                                                durationStr=configs.durationStr, 
                                                barSizeSetting=barSize, 
                                                whatToShow='TRADES',
                                                useRTH=True,
                                                formatDate=1)
            startDate = startDate+timedelta(days=6)
            allBars += bars

        events = []
        for bar in allBars:
            events.append(Event(contract, bar.date, bar.open, bar.close, bar.high, bar.low))
        return events

    async def downloadHistoricalDataAsync(self, contract: Contract, days: int, barSize: str, endDate: date = datetime.today()) -> List[Event]:
        if contract is None:
            return []

        configs = TWSClient.HistoricalRequestConfigs(contract, days, barSize, endDate)
        allBars: List[BarData] = []
        startDate = configs.startDate

        while startDate <= configs.endDate:
            endtime = startDate+timedelta(days=1) if barSize.endswith('min') else ''
            bars: List[BarData] = await self.client.reqHistoricalDataAsync(configs.stock, endDateTime=endtime, 
                                                    durationStr=configs.durationStr, 
                                                    barSizeSetting=barSize, 
                                                    whatToShow='TRADES',
                                                    useRTH=True,
                                                    formatDate=1)
            startDate = startDate+timedelta(days=6)
            allBars += bars

        events = []
        for bar in allBars:
            events.append(Event(contract, bar.date, bar.open, bar.close, bar.high, bar.low, bar.volume))
        return events

    class HistoricalRequestConfigs:
        nDays: int
        nYears: int
        durationsDays: str
        endDate: date
        startDate: date
        stock: Stock
        durationStr: str

        def __init__(self, contract: Contract, days: int, barSize: str, endDate: date = datetime.today()) -> None:
            super().__init__()
            self.nDays = days
            self.nYears = int(self.nDays/365)
            self.durationDays = ("%d D" % (self.nDays+10)) if self.nDays < 365 else ("%d Y" % self.nYears)
            self.endDate = endDate
            self.startDate = self.endDate-timedelta(days=self.nDays+1) if barSize.endswith('min') else self.endDate
            self.stock = Stock(contract.symbol, contract.exchange, contract.currency)
            self.durationStr = '5 D' if barSize.endswith('min') else self.durationDays

class TWSController(ProviderController):
    @property
    def client(self) -> IB:
        return self.provider.session

    @property
    def controller(self) -> IBC:
        return self.sessionController

    def __init__(self, providerConfigs: ProviderConfigs) -> None:
        super().__init__()
        self.type = Provider.TWS
        self.session = IB()
        self.sessionController = IBC(version= providerConfigs.version, 
                                    tradingMode= providerConfigs.tradingMode, 
                                    userid= providerConfigs.user, 
                                    password= providerConfigs.password)

    def isConnected(self) -> bool:
        return self.client.isConnected()

    async def startAsync(self):
        await self.controller.startAsync()

    async def terminateAsync(self):
        await self.controller.terminateAsync()