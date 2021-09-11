from helpers.math import round_down
from backtest.reports.stoch_diverge.report_stoch_diverge_module import ReportStochDivergeModule
from datetime import date, timedelta
import math
from sqlite3.dbapi2 import enable_callback_tracebacks
from strategy.models import StrategyData, StrategyResult, StrategyResultType
from strategy.stoch_diverge.strategy_stoch_diverge import StrategyStochDiverge
from database.database_module import DatabaseModule
from country_config.market_manager import MarketManager
import csv
from strategy.configs.stoch_diverge.models import StrategyStochDivergeConfig
from strategy.configs.factory.strategy_config_factory import StrategyConfigFactory

from helpers.date_timezone import DateFormat, DateSystemFormat, DateSystemFullFormat, Helpers
from models.stoch_diverge.models import EventStochDiverge
from strategy.historical_data import HistoricalData
from backtest.configs.models import BacktestConfigs
from models.base_models import BracketOrder, Contract, Event, Order, OrderAction, OrderType, Position
from backtest.models.base_models import BacktestAction, ContractSymbol
from typing import Any, List, Tuple, Union
from strategy.strategy import Strategy
from strategy.configs.models import StrategyConfig
from backtest.backtest_module import BacktestModule
from strategy.stoch_diverge.models import StrategyStochDivergeData, StrategyStochDivergeResult

class BacktestStochDivergeModule(BacktestModule):
    class RunStrategyStochDivergeModel(BacktestModule.RunStrategyModel):
        databaseModule: DatabaseModule
        positionStochDates: Union[str, date]
        positionStochHolds: Union[str, int]
        eventsMapper: Union[str, EventStochDiverge]
        currentDay: date
        tradesAvailable: int
        nextDayTrades: Union[str, StrategyStochDivergeResult]

        def __init__(self, strategy: Strategy, strategyConfig: StrategyConfig, isForStockPerformance: bool) -> None:
            super().__init__(strategy, strategyConfig, isForStockPerformance)
            self.databaseModule = DatabaseModule()
            self.databaseModule.openDatabaseConnectionForBacktest()
            self.databaseModule.deleteFills(self.databaseModule.getFills())

            self.currentDay = None
            self.tradesAvailable = 0
            self.positionStochDates = dict()
            self.eventsMapper = dict()
            self.nextDayTrades = dict()
            self.positionStochHolds = dict()

    def __init__(self) -> None:
        super().__init__()
        self.reportModule = ReportStochDivergeModule()

    #### READ/WRITE IN CSV FILES ####

    def addIndicatorsToStocksData(self, stocksData: Union[ContractSymbol, Tuple[Contract, List[Event]]], config: BacktestConfigs) -> Union[ContractSymbol, Tuple[Contract, List[Event]]]:
        newData: Union[str, Tuple[Contract, List[Event]]] = dict()
        for stockSymbol, (stock, bars) in stocksData.items():
            events = HistoricalData.computeEventsForStochDivergeStrategy(bars, config.strategy)
            if events is not None:
                newData[stockSymbol] = (stock, events)
        return newData

    def getStockFileHeaderRow(self) -> List[str]:
        return ["Symbol", "Date", "Open", "Close", "High", "Low", "%K", "%D", "HH_Close", "LL_Close", "HL_Stoch", "LH_Stoch"]

    def getStockFileDataRow(self, contract: Contract, data: EventStochDiverge) -> List[Any]:
        symbol = contract.symbol
        date = Helpers.dateToString(data.datetime, format=DateSystemFormat)

        open = 0 if not data.open else round(data.open, 2)
        close = 0 if not data.close else round(data.close, 2)
        high = 0 if not data.high else round(data.high, 2)
        low = 0 if not data.low else round(data.low, 2)

        k = None if data.k is None else data.k
        d = None if data.d is None else data.d
        priceDivergenceOverbought = None if data.priceDivergenceOverbought is None else Helpers.dateToString(data.priceDivergenceOverbought, format=DateSystemFormat)
        kDivergenceOverbought = None if data.kDivergenceOverbought is None else Helpers.dateToString(data.kDivergenceOverbought, format=DateSystemFormat)
        priceDivergenceOversold = None if data.priceDivergenceOversold is None else Helpers.dateToString(data.priceDivergenceOversold, format=DateSystemFormat)
        kDivergenceOversold = None if data.kDivergenceOversold is None else Helpers.dateToString(data.kDivergenceOversold, format=DateSystemFormat)

        return [symbol, date, open, close, high, low, k, d, priceDivergenceOverbought, priceDivergenceOversold, kDivergenceOversold, kDivergenceOverbought]

    def parseCSVFile(self, reader: csv.reader) -> List[Event]:
        configs = BacktestConfigs()
        line_count = 0
        contractEvents = []
        for row in reader:
            if line_count > 0:
                symbol = None if not row[0] else row[0]
                contract = Contract(symbol, configs.country)

                datetimeStr = None if not row[1] else row[1]
                datetime = Helpers.stringToDate(datetimeStr, DateSystemFormat)

                open = 0 if not row[2] else float(row[2])
                close = 0 if not row[3] else float(row[3])
                high = 0 if not row[4] else float(row[4])
                low = 0 if not row[5] else float(row[5])

                k = None if not row[6] else float(row[6])
                d = None if not row[7] else float(row[7])
                datetimeStr = None if not row[8] else row[8]
                priceDivergenceOverbought = None if not datetimeStr else Helpers.stringToDate(datetimeStr, DateSystemFormat)
                datetimeStr = None if not row[9] else row[9]
                priceDivergenceOversold = None if not datetimeStr else Helpers.stringToDate(datetimeStr, DateSystemFormat)
                datetimeStr = None if not row[10] else row[10]
                kDivergenceOversold = None if not datetimeStr else Helpers.stringToDate(datetimeStr, DateSystemFormat)
                datetimeStr = None if not row[11] else row[11]
                kDivergenceOverbought = None if not datetimeStr else Helpers.stringToDate(datetimeStr, DateSystemFormat)

                event = EventStochDiverge(contract, datetime, open, close, high, low, k, d, priceDivergenceOverbought, kDivergenceOverbought, priceDivergenceOversold, kDivergenceOversold)
                contractEvents.append(event)
            line_count += 1
        return contractEvents

    def setupRunStrategy(self, events: List[Event], dynamicParameters: List[List[float]]):
        config = BacktestConfigs()
        isForStockPerformance = True if config.action == BacktestAction.runStrategyPerformance or config.action == BacktestAction.runStrategyPerformanceWithDynamicParameters else False
        strategyConfig: StrategyStochDivergeConfig = StrategyConfigFactory.createStochasticDivergeStrategyFor(
            MarketManager.getMarketFor(config.country), config.timezone)
        if dynamicParameters is not None:
            strategyConfig.profitPercentage = float(dynamicParameters[0])
            strategyConfig.stopToLosePercentage = float(dynamicParameters[1])
            strategyConfig.kPeriod = float(dynamicParameters[2])
            strategyConfig.dPeriod = int(dynamicParameters[4])
            strategyConfig.daysToHold = float(dynamicParameters[3])
        self.strategyModel = self.RunStrategyStochDivergeModel(
            StrategyStochDiverge(), strategyConfig, isForStockPerformance)
        for event in events:
            identifier = self.uniqueIdentifier(
                event.contract.symbol, event.datetime.date())
            self.strategyModel.eventsMapper[identifier] = event

    def getStrategyData(self, event: Event, events: List[Event], index: int) -> StrategyData:
        strategyConfig: StrategyStochDivergeConfig = self.strategyModel.strategyConfig
        event: EventStochDiverge = event
        events: List[EventStochDiverge] = events
        previousEvents = self.getPreviousEvents(
            event, strategyConfig.daysBeforeToDownload)
        if previousEvents is None or len(previousEvents) < strategyConfig.daysBefore:
            return None
        previousEventsFiltered = previousEvents[-strategyConfig.daysBefore:]
        balance = min(30000, self.getBalance())
        return StrategyStochDivergeData(contract=event.contract,
                                  totalCash=balance,
                                  event=event,
                                  previousEvents=previousEventsFiltered,
                                  today=event.datetime.date(),
                                  now=event.datetime)

    def getPreviousEvents(self, event: EventStochDiverge, daysBefore: int = 5):
        model: BacktestStochDivergeModule.RunStrategyStochDivergeModel = self.strategyModel
        previousDays: List[EventStochDiverge] = []
        for x in range(1, daysBefore):
            previousDate = event.datetime.date()+timedelta(days=-x)
            identifier = self.uniqueIdentifier(
                event.contract.symbol, previousDate)
            if identifier in model.eventsMapper:
                previousDays.append(model.eventsMapper[identifier])

        previousDays.reverse()
        return previousDays

    def getFill(self, contract: Contract):
        model: BacktestStochDivergeModule.RunStrategyStochDivergeModel = self.strategyModel
        fills = model.databaseModule.getFills()
        filteredFills = list(
            filter(lambda x: contract.symbol == x.symbol, fills))
        filteredFills.sort(key=lambda x: x.date, reverse=True)
        if len(filteredFills) > 0:
            return filteredFills[0]
        return None

    def clearOldFills(self, event: Event):
        model: BacktestStochDivergeModule.RunStrategyStochDivergeModel = self.strategyModel
        fills = model.databaseModule.getFills()
        limitDate = event.datetime.date()-timedelta(days=40)
        filteredFills = list(filter(lambda x: x.date < limitDate, fills))
        model.databaseModule.deleteFills(filteredFills)

    def handleStrategyResult(self, event: Event, events: List[Event], result: StrategyResult, currentPosition: int):
        result: StrategyStochDivergeResult = result
        model: BacktestStochDivergeModule.RunStrategyStochDivergeModel = self.strategyModel
        strategyConfig: StrategyStochDivergeConfig = model.strategyConfig
        if ((result.type == StrategyResultType.Buy or result.type == StrategyResultType.Sell) and model.tradesAvailable > 0):
            model.nextDayTrades[result.event.contract.symbol] = result
        else:
            for key, position in model.positions.items():
                if key.split("_")[0] == event.contract.symbol:
                    lista = list(position)
                    lista[3] = event
                    model.positions[key] = tuple(lista)

    def validateCurrentDay(self, event: Event):
        model: BacktestStochDivergeModule.RunStrategyStochDivergeModel = self.strategyModel
        strategyConfig: StrategyStochDivergeConfig = model.strategyConfig
        if model.currentDay != event.datetime.date():
            balance = self.getBalance()
            model.tradesAvailable = 0
            if model.isForStockPerformance:
                model.tradesAvailable = 9999
            else:
                total = math.floor(balance/30000)
                if balance - (30000*total) >= 2000:
                    model.tradesAvailable = total+1
                else:
                    model.tradesAvailable = total

            self.clearOldFills(event)
            model.currentDay = None
        
        if event.contract.symbol in model.nextDayTrades:
            result: StrategyStochDivergeResult = model.nextDayTrades[event.contract.symbol]
            gapPrice = result.targetPrice/event.open if result.type == StrategyResultType.Sell else event.open/result.targetPrice
            profitPercentage = abs(gapPrice-1)
            stopLossPercentage = profitPercentage/strategyConfig.winLossRatio
            if profitPercentage >= strategyConfig.minTakeProfitToEnterPosition:
                balance = self.getBalance()
                size = self.positonSizing(balance, event.open, stopLossPercentage)
                totalOrderCost = event.open * size
                if size > 0:
                    identifier = self.uniqueIdentifier(result.contract.symbol, event.datetime.date())
                    action = OrderAction.Sell if result.type == StrategyResultType.Sell else OrderAction.Buy
                    parentOrder = Order(action, OrderType.MarketOrder, size, event.open)
                    profitOrder = Order(action.reverse, OrderType.LimitOrder, size, result.targetPrice)
                    gap = event.open*stopLossPercentage
                    stopPrice = event.open+gap if action == OrderAction.Sell else event.open-gap
                    stopLossOrder = Order(action.reverse, OrderType.StopOrder, size, stopPrice)
                    model.positions[identifier] = (BracketOrder(parentOrder, profitOrder, stopLossOrder),
                                                    Position(contract=result.contract, size=size),
                                                    event.datetime.date(),
                                                    event)
                    print(result)
                    print("%s Position for %s" % (event.datetime.date(), event.contract.symbol))
                    model.positionStochDates[identifier] = event.datetime.date()
                    model.positionStochHolds[identifier] = result.candlesToHold
                    model.tradesAvailable -= 1
                    # newFill = FillDB(result.contract.symbol, result.event.datetime.date(
                    # ), result.contract.country, strategyConfig.type)
                    # model.databaseModule.createFill(newFill)
            model.nextDayTrades.pop(event.contract.symbol)

    def positonSizing(self, balance: float, price: float, stopLossPercentage: float) -> int:
        strategyConfig: StrategyStochDivergeConfig = self.strategyModel.strategyConfig
        value = (balance*strategyConfig.willingToLose)/(price*stopLossPercentage)
        return int(round_down(value, 0))

    def handleEndOfDayIfNecessary(self, event: Event, events: List[Event], currentPosition: int):
        model: BacktestStochDivergeModule.RunStrategyStochDivergeModel = self.strategyModel
        model.currentDay = event.datetime.date()

        if ((len(events) > currentPosition+1 and events[currentPosition+1].datetime.date() != model.currentDay) or
                (len(events) == currentPosition+1)):
            self.handleProfitAndStop()
            self.handleExpiredFills()

    def handleProfitAndStop(self):
        model: BacktestStochDivergeModule.RunStrategyStochDivergeModel = self.strategyModel
        reportModule: ReportStochDivergeModule = self.reportModule
        positions = model.positions.copy()
        if (len(positions.values()) > 0):
            for key, (bracketOrder, position, positionDate, event) in positions.items():
                bracketOrder: BracketOrder = bracketOrder
                if self.isStopLoss(event, bracketOrder):
                    mainOrder: Order = bracketOrder.parentOrder
                    stopOrder: Order = bracketOrder.stopLossOrder
                    loss = abs(stopOrder.price*stopOrder.size -
                                mainOrder.price*mainOrder.size)
                    candlesHold = model.positionStochHolds[key]

                    reportModule.createStopLossResult(
                        event, bracketOrder, positionDate, loss, model.cashAvailable, candlesHold)

                    model.positions.pop(key)
                    model.positionStochDates.pop(key)
                    model.positionStochHolds.pop(key)

                    if model.isForStockPerformance == False:
                        model.cashAvailable -= loss
                elif self.isTakeProfit(event, bracketOrder):
                    mainOrder: Order = bracketOrder.parentOrder
                    profitOrder: Order = bracketOrder.takeProfitOrder
                    profit = abs(profitOrder.price*profitOrder.size -
                                    mainOrder.price*mainOrder.size)
                    candlesHold = model.positionStochHolds[key]

                    reportModule.createTakeProfitResult(
                        event, bracketOrder, positionDate, profit, model.cashAvailable, candlesHold)

                    model.positions.pop(key)
                    model.positionStochDates.pop(key)
                    model.positionStochHolds.pop(key)

                    if model.isForStockPerformance == False:
                        model.cashAvailable += profit

    def handleExpiredFills(self):
        model: BacktestStochDivergeModule.RunStrategyStochDivergeModel = self.strategyModel
        reportModule: ReportStochDivergeModule = self.reportModule
        positions = model.positions.copy()
        if (len(positions.values()) > 0):
            for key, (bracketOrder, position, positionDate, event) in positions.items():
                bracketOrder: BracketOrder = bracketOrder
                stochPostionHold = model.positionStochHolds[key]
                if self.isPositionExpired(event, positionDate, stochPostionHold):
                    if self.isProfit(event, bracketOrder):
                        mainOrder: Order = bracketOrder.parentOrder
                        profit = abs(event.close*mainOrder.size -
                                        mainOrder.price*mainOrder.size)
                        candlesHold = model.positionStochHolds[key]

                        reportModule.createProfitResult(
                            event, bracketOrder, positionDate, profit, model.cashAvailable, candlesHold)

                        if model.isForStockPerformance == False:
                            model.cashAvailable += profit
                    else:
                        mainOrder: Order = bracketOrder.parentOrder
                        loss = abs(event.close*mainOrder.size -
                                    mainOrder.price*mainOrder.size)
                        candlesHold = model.positionStochHolds[key]

                        reportModule.createLossResult(
                            event, bracketOrder, positionDate, loss, model.cashAvailable, candlesHold)

                        if model.isForStockPerformance == False:
                            model.cashAvailable -= loss

                    identifier = self.uniqueIdentifier(event.contract.symbol, positionDate)
                    model.positions.pop(identifier)
                    model.positionStochDates.pop(identifier)
                    model.positionStochHolds.pop(key)

    def isPositionExpired(self, event: EventStochDiverge, positionDate: date, candlesToHold: int) -> bool:
        config: StrategyStochDivergeConfig = self.strategyModel.strategyConfig
        return event.datetime.date() >= (positionDate+timedelta(days=candlesToHold))

    def isStopLoss(self, event: EventStochDiverge, bracketOrder: BracketOrder) -> bool:
        mainOrder = bracketOrder.parentOrder
        stopOrder = bracketOrder.stopLossOrder
        return ((mainOrder.action == OrderAction.Buy and event.low <= stopOrder.price) or
                (mainOrder.action == OrderAction.Sell and event.high >= stopOrder.price))

    def isTakeProfit(self, event: EventStochDiverge, bracketOrder: BracketOrder) -> bool:
        mainOrder = bracketOrder.parentOrder
        takeProfitOrder = bracketOrder.takeProfitOrder
        return ((mainOrder.action == OrderAction.Buy and event.high >= takeProfitOrder.price) or
                (mainOrder.action == OrderAction.Sell and event.low <= takeProfitOrder.price))

    def isProfit(self, event: EventStochDiverge, bracketOrder: BracketOrder) -> bool:
        mainOrder = bracketOrder.parentOrder
        return ((mainOrder.action == OrderAction.Buy and mainOrder.price < event.close) or
                (mainOrder.action == OrderAction.Sell and mainOrder.price > event.close))


