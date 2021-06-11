from matplotlib.axes import Axes
from backtest.reports.zigzag.report_zigzag_module import ReportZigZagModule
from strategy.configs.zigzag.models import StrategyZigZagConfig
import csv, math
from distutils.util import strtobool
from database.model import FillDB
from datetime import date, datetime, timedelta
from strategy.zigzag.models import StrategyZigZagData, StrategyZigZagResult
from strategy.models import StrategyData, StrategyResult, StrategyResultType
from typing import Any, List, Tuple, Union
from country_config.market_manager import MarketManager

from helpers.date_timezone import Helpers
from backtest.models.base_models import BacktestAction, ContractSymbol
from backtest.backtest_module import BacktestModule
from backtest.configs.models import BacktestConfigs

from strategy.configs.models import StrategyConfig
from strategy.configs.factory.strategy_config_factory import StrategyConfigFactory
from strategy.strategy import Strategy
from strategy.historical_data import HistoricalData
from strategy.zigzag.strategy_zigzag import StrategyZigZag

from models.zigzag.models import EventZigZag, ZigZagType
from models.base_models import BracketOrder, Contract, Event, Order, OrderAction, Position

from database.database_module import DatabaseModule

class BacktestZigZagModule(BacktestModule):
    class RunStrategyZigZagModel(BacktestModule.RunStrategyModel):
        databaseModule: DatabaseModule
        positionZigZagDates: Union[str, date]
        eventsMapper: Union[str, EventZigZag]
        currentDay: date
        tradesAvailable: int

        def __init__(self, strategy: Strategy, strategyConfig: StrategyConfig, isForStockPerformance: bool) -> None:
            super().__init__(strategy, strategyConfig, isForStockPerformance)
            self.databaseModule = DatabaseModule()
            self.databaseModule.openDatabaseConnectionForBacktest()
            self.databaseModule.deleteFills(self.databaseModule.getFills())
            
            self.currentDay = None
            self.tradesAvailable = 0
            self.positionZigZagDates = dict()
            self.eventsMapper = dict()

    def __init__(self) -> None:
        super().__init__()
        self.reportModule = ReportZigZagModule()

    #### READ/WRITE IN CSV FILES ####

    def addIndicatorsToStocksData(self, stocksData: Union[ContractSymbol, Tuple[Contract, List[Event]]], config: BacktestConfigs) -> Union[ContractSymbol, Tuple[Contract, List[Event]]]:
        newData: Union[str, Tuple[Contract, List[Event]]] = dict()
        for stockSymbol, (stock, bars) in stocksData.items():
            events = HistoricalData.computeEventsForZigZagStrategy(bars, config.strategy)
            if events is not None:
                newData[stockSymbol] = (stock, HistoricalData.computeEventsForZigZagStrategy(bars, config.strategy))
        return newData

    def getStockFileHeaderRow(self) -> List[str]:
        return ["Symbol", "Date", "Open", "Close", "High", "Low", "ZigZag", "ZigZagType", "RSI"]

    def getStockFileDataRow(self, contract: Contract, data: EventZigZag) -> List[Any]:
        symbol = contract.symbol
        date = Helpers.dateToString(data.datetime)

        open = 0 if not data.open else round(data.open, 2)
        close = 0 if not data.close else round(data.close, 2)
        high = 0 if not data.high else round(data.high, 2)
        low = 0 if not data.low else round(data.low, 2)

        zigzag = False if data.zigzag is None else data.zigzag
        zigzagType = None if data.zigzagType is None else data.zigzagType.value
        rsi = None if data.rsi is None else round(data.rsi, 2)

        return [symbol, date, open, close, high, low, zigzag, zigzagType, rsi]

    def parseCSVFile(self, reader: csv.reader) -> List[Event]:
        configs = BacktestConfigs()
        line_count = 0
        contractEvents = []
        for row in reader:
            if line_count > 0:
                symbol = None if not row[0] else row[0]
                contract = Contract(symbol, configs.country)

                datetimeStr = None if not row[1] else row[1]
                datetime = Helpers.stringToDate(datetimeStr)

                open = 0 if not row[2] else float(row[2])
                close = 0 if not row[3] else float(row[3])
                high = 0 if not row[4] else float(row[4])
                low = 0 if not row[5] else float(row[5])

                zigzag = False if not row[6] else bool(strtobool(row[6]))
                zigzagType = None if not row[7] else ZigZagType(int(row[7]))
                rsi = 0 if not row[8] else float(row[8])

                event = EventZigZag(contract, datetime, open, close, high, low, zigzag, zigzagType, rsi, open)
                contractEvents.append(event)
            line_count += 1
        return contractEvents

    #### RUN STRATEGY ####

    def setupRunStrategy(self, events: List[Event], dynamicParameters: List[List[float]]):
        config = BacktestConfigs()
        isForStockPerformance = True if config.action == BacktestAction.runStrategyPerformance or config.action == BacktestAction.runStrategyPerformanceWithDynamicParameters else False
        strategyConfig: StrategyZigZagConfig = StrategyConfigFactory.createZigZagStrategyFor(MarketManager.getMarketFor(config.country))
        if dynamicParameters is not None:
            strategyConfig.profitPercentage = float(dynamicParameters[0])
            strategyConfig.stopToLosePercentage = float(dynamicParameters[1])
            strategyConfig.zigzagSpread = float(dynamicParameters[2])
            strategyConfig.daysToHold = float(dynamicParameters[3])
            strategyConfig.daysAfterZigZag = int(dynamicParameters[4])
        self.strategyModel = self.RunStrategyZigZagModel(StrategyZigZag(), strategyConfig, isForStockPerformance)
        for event in events:
            identifier = self.uniqueIdentifier(event.contract.symbol, event.datetime.date())
            self.strategyModel.eventsMapper[identifier] = event

    def clearOldFills(self, event: Event):
        model: BacktestZigZagModule.RunStrategyZigZagModel = self.strategyModel
        fills = model.databaseModule.getFills()
        limitDate = event.datetime.date()-timedelta(days=40)
        filteredFills = list(filter(lambda x: x.date < limitDate, fills))
        model.databaseModule.deleteFills(filteredFills)

    def getFill(self, contract: Contract):
        model: BacktestZigZagModule.RunStrategyZigZagModel = self.strategyModel
        fills = model.databaseModule.getFills()
        filteredFills = list(filter(lambda x: contract.symbol == x.symbol, fills))
        filteredFills.sort(key=lambda x: x.date, reverse=True)
        if len(filteredFills) > 0:
            return filteredFills[0]
        return None

    def validateCurrentDay(self, event: Event):
        model: BacktestZigZagModule.RunStrategyZigZagModel = self.strategyModel
        if model.currentDay != event.datetime.date():
            balance = self.getBalance()
            model.tradesAvailable = 0
            if model.isForStockPerformance:
                model.tradesAvailable = 9999
            else:
                result = math.floor(balance/150000)
                if balance - (150000*result) >= 2000:
                    model.tradesAvailable = result+1
                else: 
                    model.tradesAvailable = result

            self.clearOldFills(event) 
            model.currentDay = None
    
    def getStrategyData(self, event: Event, events: List[Event], index: int) -> StrategyData:
        strategyConfig: StrategyZigZagConfig = self.strategyModel.strategyConfig
        event: EventZigZag = event
        events: List[EventZigZag] = events
        previousEvents = self.getPreviousEvents(event, strategyConfig.daysBeforeToDownload)
        if previousEvents is None or len(previousEvents) < strategyConfig.daysBefore:
            return None
        
        previousEventsFiltered = previousEvents[-strategyConfig.daysBefore:]
        fill = self.getFill(event.contract)
        balance = min(150000, self.getBalance())

        return StrategyZigZagData(contract= event.contract,
                                    totalCash= balance,
                                    event= event,
                                    previousEvents= previousEventsFiltered,
                                    position= None,
                                    fill= fill,
                                    today = event.datetime.date(),
                                    now = event.datetime)
        
    def getPreviousEvents(self, event: EventZigZag, daysBefore: int = 5):
        model: BacktestZigZagModule.RunStrategyZigZagModel = self.strategyModel
        previousDays: List[EventZigZag] = []

        cloneEvent = EventZigZag(event.contract, event.datetime, event.open, event.close, 
                                 event.high, event.low, event.zigzag, event.zigzagType, 
                                 event.rsi, event.lastPrice)
        cloneEvent.close = event.open
        cloneEvent.high = event.open
        cloneEvent.low = event.open
        previousDays.append(cloneEvent)
        for x in range(1,daysBefore):
            previousDate = event.datetime.date()+timedelta(days=-x)
            identifier = self.uniqueIdentifier(event.contract.symbol, previousDate)
            if identifier in model.eventsMapper:
                previousDays.append(model.eventsMapper[identifier])

        previousDays.reverse()
        previousEvents = HistoricalData.computeEventsForZigZagStrategy(previousDays, model.strategyConfig)
        previousEvents.pop()
        return previousEvents

    def handleStrategyResult(self, event: Event, events: List[Event], result: StrategyResult, currentPosition: int):
        result: StrategyZigZagResult = result
        model: BacktestZigZagModule.RunStrategyZigZagModel = self.strategyModel
        if ((result.type == StrategyResultType.Buy or result.type == StrategyResultType.Sell) and model.tradesAvailable > 0):
            balance = self.getBalance()
            totalOrderCost = result.order.parentOrder.price*result.order.parentOrder.size
            if (balance > totalOrderCost and result.order.parentOrder.size > 0) or model.isForStockPerformance:
                identifier = self.uniqueIdentifier(result.contract.symbol, result.event.datetime.date())
                model.positions[identifier] = (result.order,
                                                Position(contract=result.contract, size= result.order.parentOrder.size),
                                                result.event.datetime.date(),
                                                event)
                model.positionZigZagDates[identifier] = result.event.datetime.date()+timedelta(days=result.priority)
                print(result)
                model.tradesAvailable -= 1
                newFill = FillDB(result.contract.symbol, result.event.datetime.date())
                model.databaseModule.createFill(newFill)
        else:
            for key, position in model.positions.items():
                if key.split("_")[0] == event.contract.symbol:
                    lista = list(position)
                    lista[3] = event
                    model.positions[key] = tuple(lista)

    def handleEndOfDayIfNecessary(self, event: Event, events: List[Event], currentPosition: int):
        model: BacktestZigZagModule.RunStrategyZigZagModel = self.strategyModel
        model.currentDay = event.datetime.date()
        
        if len(events) > currentPosition+1 and events[currentPosition+1].datetime.date() != model.currentDay:
            self.handleProfitAndStop()
            self.handleExpiredFills()

    def handleProfitAndStop(self):
        model: BacktestZigZagModule.RunStrategyZigZagModel = self.strategyModel
        reportModule: ReportZigZagModule = self.reportModule
        positions = model.positions.copy()
        if (len(positions.values()) > 0):
            for key, (bracketOrder, position, positionDate, event) in positions.items():
                bracketOrder: BracketOrder = bracketOrder
                if self.isStopLoss(event, bracketOrder):
                    mainOrder: Order = bracketOrder.parentOrder
                    stopOrder: Order = bracketOrder.stopLossOrder
                    loss = abs(stopOrder.price*stopOrder.size-mainOrder.price*mainOrder.size)
                    zigzagDate = model.positionZigZagDates[key]

                    reportModule.createStopLossResult(event, bracketOrder, positionDate, loss, model.cashAvailable, zigzagDate)

                    model.positions.pop(key)
                    model.positionZigZagDates.pop(key)

                    if model.isForStockPerformance == False:
                        model.cashAvailable -= loss
                elif self.isTakeProfit(event, bracketOrder):
                    mainOrder: Order = bracketOrder.parentOrder
                    profitOrder: Order = bracketOrder.takeProfitOrder
                    profit = abs(profitOrder.price*profitOrder.size-mainOrder.price*mainOrder.size)
                    zigzagDate = model.positionZigZagDates[key]

                    reportModule.createTakeProfitResult(event, bracketOrder, positionDate, profit, model.cashAvailable, zigzagDate)

                    model.positions.pop(key)
                    model.positionZigZagDates.pop(key)

                    if model.isForStockPerformance == False:
                        model.cashAvailable += profit

    def handleExpiredFills(self):
        model: BacktestZigZagModule.RunStrategyZigZagModel = self.strategyModel
        reportModule: ReportZigZagModule = self.reportModule
        positions = model.positions.copy()
        if (len(positions.values()) > 0):
            for key, (bracketOrder, position, positionDate, event) in positions.items():
                bracketOrder: BracketOrder = bracketOrder
                if self.isPositionExpired(event, positionDate):
                    if self.isProfit(event, bracketOrder):
                        mainOrder: Order = bracketOrder.parentOrder
                        profit = abs(event.close*mainOrder.size-mainOrder.price*mainOrder.size)
                        zigzagDate = model.positionZigZagDates[key]

                        reportModule.createProfitResult(event, bracketOrder, positionDate, profit, model.cashAvailable, zigzagDate)

                        if model.isForStockPerformance == False:
                            model.cashAvailable += profit
                    else:
                        mainOrder: Order = bracketOrder.parentOrder
                        loss = abs(event.close*mainOrder.size-mainOrder.price*mainOrder.size)
                        zigzagDate = model.positionZigZagDates[key]

                        reportModule.createLossResult(event, bracketOrder, positionDate, loss, model.cashAvailable, zigzagDate)

                        if model.isForStockPerformance == False:
                            model.cashAvailable -= loss

                    identifier = self.uniqueIdentifier(event.contract.symbol, positionDate)
                    model.positions.pop(identifier)
                    model.positionZigZagDates.pop(identifier)

    def isPositionExpired(self, event: EventZigZag, positionDate: date) -> bool:
        config: StrategyZigZagConfig = self.strategyModel.strategyConfig
        return event.datetime.date() >= (positionDate+timedelta(days=config.daysToHold))

    def isStopLoss(self, event: EventZigZag, bracketOrder: BracketOrder) -> bool:
        mainOrder = bracketOrder.parentOrder
        stopOrder = bracketOrder.stopLossOrder
        return ((mainOrder.action == OrderAction.Buy and event.low <= stopOrder.price) or
                (mainOrder.action == OrderAction.Sell and event.high >= stopOrder.price))

    def isTakeProfit(self, event: EventZigZag, bracketOrder: BracketOrder) -> bool:
        mainOrder = bracketOrder.parentOrder
        takeProfitOrder = bracketOrder.takeProfitOrder
        return ((mainOrder.action == OrderAction.Buy and  event.high >= takeProfitOrder.price) or
                (mainOrder.action == OrderAction.Sell and event.low <= takeProfitOrder.price))

    def isProfit(self, event: EventZigZag, bracketOrder: BracketOrder) -> bool:
        mainOrder = bracketOrder.parentOrder
        return ((mainOrder.action == OrderAction.Buy and mainOrder.price <= event.close) or
                (mainOrder.action == OrderAction.Sell and mainOrder.price >= event.close))

    def addIndicatorsToGraph(self, events: List[Event]) -> Union[str, Any]:
        import numpy as np
        events: List[EventZigZag] = events
        items = []
        for event in events:
            if event.zigzag == True:
                if event.zigzagType == ZigZagType.high:
                    items.append([event.datetime, event.high])
                else:
                    items.append([event.datetime, event.low])
        return dict(alines=items, colors=['b'])