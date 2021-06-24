from country_config.country_manager import getCountryFromCurrency
from datetime import date, datetime, timedelta
from typing import Callable, List

from ib_insync.objects import BarData
from ib_insync import IB, IBC, Stock, Order as IBOrder, LimitOrder, StopOrder
from ib_insync import Contract as IBContract, BracketOrder as IBBracketOrder, MarketOrder

from models.base_models import BracketOrder, Contract, Event, Order, OrderAction, OrderType, Position, Trade
from configs.models import Provider, ProviderConfigs
from provider_factory.models import ProviderClient, ProviderController, ProviderEvents

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

    # Connections

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

    # Portfolio

    async def syncData(self):
        await self.client.accountSummaryAsync()
        await self.client.reqPositionsAsync()
        await self.client.reqAllOpenOrdersAsync()

    def positions(self) -> List[Position]:
        items = self.client.positions()
        positions = []
        for item in items:
            contract = Contract(item.contract.symbol, getCountryFromCurrency(item.contract.currency), item.contract.exchange)
            positions.append(Position(contract, item.position))
        return positions

    def trades(self) -> List[Trade]:
        items = self.client.openTrades()
        trades = []
        for item in items:
            price = item.order.auxPrice if item.order.orderType == OrderType.StopOrder.value else item.order.lmtPrice
            order = Order(OrderAction(item.order.action), OrderType(item.order.orderType), item.order.totalQuantity, price, item.order.parentId, item.order.orderId)
            country = getCountryFromCurrency(item.contract.currency)
            contract = Contract(item.contract.symbol, country, item.contract.exchange)
            trades.append(Trade(contract, order))
        return trades

    def cashBalance(self) -> float:
        for account in self.client.accountValues():
            if account.tag == "AvailableFunds":
                return float(account.value)

    def currencyRateFor(self, currency: str) -> float:
        for account in self.client.accountValues():
            if (account.tag == "ExchangeRate" and account.currency == currency):
                return float(account.value)

    def createOrder(self, contract: Contract, bracketOrder: BracketOrder):
        parentOrder = bracketOrder.parentOrder
        profitOrder = bracketOrder.takeProfitOrder
        stopLossOrder = bracketOrder.stopLossOrder
        newContract: Stock = Stock(symbol=contract.symbol, exchange=contract.exchange, currency=contract.currency)

        if parentOrder.type == OrderType.MarketOrder:
            assert parentOrder.action in (OrderAction.Buy, OrderAction.Sell)
            reverseAction = parentOrder.action.reverse.value

            parent = IBOrder(action=parentOrder.action.value, totalQuantity=parentOrder.size,
                            orderId=self.client.client.getReqId(),
                            orderType="MKT",
                            transmit=False)
            takeProfit = LimitOrder(reverseAction, profitOrder.size, profitOrder.price,
                                    orderId=self.client.client.getReqId(),
                                    tif="GTC",
                                    transmit=False,
                                    parentId=parent.orderId)
            stopLoss = StopOrder(reverseAction, stopLossOrder.size, stopLossOrder.price,
                                orderId=self.client.client.getReqId(),
                                tif="GTC",
                                transmit=True,
                                parentId=parent.orderId)

            bracket = IBBracketOrder(parent, takeProfit, stopLoss)
            for o in bracket:
                self.client.placeOrder(newContract, o)
        else:
            bracket = self.client.bracketOrder(parentOrder.action.value, parentOrder.size, parentOrder.price, profitOrder.price, stopLossOrder.price)
            for o in bracket:
                self.client.placeOrder(newContract, o)

    def cancelOrder(self, order: Order):
        ibOrder: IBOrder = IBOrder(orderId=order.id, parentId=order.parentId, 
                                    orderType=order.type.value, action=order.action.value,
                                    totalQuantity=order.size)
        if order.type == OrderType.StopOrder:
            ibOrder.auxPrice = order.price
        else:
            ibOrder.lmtPrice = order.price
        self.client.cancelOrder(ibOrder)

    def cancelPosition(self, action: OrderAction, position: Position):
        order = MarketOrder(action.value, abs(position.size))
        contract: Stock = Stock(symbol=position.contract.symbol, 
                                currency=position.contract.currency,
                                exchange=position.contract.exchange)
        self.client.placeOrder(contract, order)

    # Historical Data

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
            endtime = '' 
            if barSize.endswith('min'):
                endtime = configs.startDate+timedelta(days=1)
            else:
                endtime = configs.endDate
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
            events.append(Event(contract, bar.date, bar.open, bar.close, bar.high, bar.low))
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

    # Events

    def subscribeEvent(self, event: ProviderEvents, callable: Callable):
        if event == ProviderEvents.didTimeOut:
            self.client.timeoutEvent += callable
        elif event == ProviderEvents.didGetError:
            self.client.errorEvent += callable
        elif event == ProviderEvents.didDisconnect:
            self.client.disconnectedEvent += callable

    def unsubscribeEvent(self, event: ProviderEvents, callable: Callable):
        if event == ProviderEvents.didTimeOut:
            self.client.timeoutEvent -= callable
        elif event == ProviderEvents.didGetError:
            self.client.errorEvent -= callable
        elif event == ProviderEvents.didDisconnect:
            self.client.disconnectedEvent -= callable


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
        self.provider = TWSClient(providerConfigs)
        self.sessionController = IBC(twsVersion= providerConfigs.version, 
                                    tradingMode= providerConfigs.tradingMode, 
                                    userid= providerConfigs.user, 
                                    password= providerConfigs.password)

    def isConnected(self) -> bool:
        return self.client.isConnected()

    async def startAsync(self):
        await self.controller.startAsync()

    async def terminateAsync(self):
        await self.controller.terminateAsync()