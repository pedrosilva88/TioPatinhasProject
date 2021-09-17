from database.model import FillDB
from database.database_module import DatabaseModule
from backtest.reports.impulse_pullback.report_impulse_pullback_module import ReportImpulsePullbackModule
from datetime import date, timedelta
import csv
import math
from strategy.impulse_pullback.strategy_impulse_pullback import StrategyImpulsePullback
from models.base_models import BracketOrder, Contract, Event, Order, OrderAction, Position
from strategy.strategy import Strategy
from strategy.configs.models import StrategyConfig, StrategyType
from strategy.configs.impulse_pullback.models import StrategyImpulsePullbackConfig
from strategy.models import StrategyData, StrategyResult, StrategyResultType
from country_config.market_manager import MarketManager
from strategy.configs.factory.strategy_config_factory import StrategyConfigFactory
from strategy.impulse_pullback.models import StrategyImpulsePullbackData, StrategyImpulsePullbackResult, StrategyImpulsePullbackResultResultType
from models.impulse_pullback.models import EventImpulsePullback
from typing import Any, List, Tuple, Union
from backtest.backtest_module import BacktestModule
from backtest.models.base_models import BacktestAction, ContractSymbol
from backtest.configs.models import BacktestConfigs
from helpers.date_timezone import DateSystemFormat, Helpers
from strategy.historical_data import HistoricalData

class BacktestImpulsePullbackModule(BacktestModule):
    class RunStrategyImpulsePullbackModel(BacktestModule.RunStrategyModel):
        databaseModule: DatabaseModule
        positionIPDates: Union[str, date]
        positionIPHolds: Union[str, int]
        positionIPCriteria: Union[str, StrategyImpulsePullbackResultResultType]
        eventsMapper: Union[str, EventImpulsePullback]
        currentDay: date
        tradesAvailable: int
        nextDayTrades: Union[str, StrategyImpulsePullbackResult]

        def __init__(self, strategy: Strategy, strategyConfig: StrategyConfig, isForStockPerformance: bool) -> None:
            super().__init__(strategy, strategyConfig, isForStockPerformance)
            self.databaseModule = DatabaseModule()
            self.databaseModule.openDatabaseConnectionForBacktest()
            self.databaseModule.deleteFills(self.databaseModule.getFills())

            self.currentDay = None
            self.tradesAvailable = 0
            self.positionIPDates = dict()
            self.eventsMapper = dict()
            self.nextDayTrades = dict()
            self.positionIPHolds = dict()

    def __init__(self) -> None:
        super().__init__()
        self.reportModule = ReportImpulsePullbackModule()

    #### READ/WRITE IN CSV FILES ####

    def addIndicatorsToStocksData(self, stocksData: Union[ContractSymbol, Tuple[Contract, List[Event]]], config: BacktestConfigs) -> Union[ContractSymbol, Tuple[Contract, List[Event]]]:
        newData: Union[str, Tuple[Contract, List[Event]]] = dict()
        for stockSymbol, (stock, bars) in stocksData.items():
            events = HistoricalData.computeEventsForImpulsePullbackStrategy(bars, config.strategy)
            if events is not None:
                newData[stockSymbol] = (stock, events)
        return newData

    def getStockFileHeaderRow(self) -> List[str]:
        return ["Symbol", "Date", "Open", "Close", "High", "Low", "Stoch_K", "Stoch_D", 
                "EMA6", "EMA18", "EMA50", "EMA100", "EMA200",
                "BB_High", "BB_Low"
                "MACD", "MACD_Signal"]

    def getStockFileDataRow(self, contract: Contract, data: EventImpulsePullback) -> List[Any]:
        symbol = contract.symbol
        date = Helpers.dateToString(data.datetime, format=DateSystemFormat)

        open = 0 if not data.open else round(data.open, 2)
        close = 0 if not data.close else round(data.close, 2)
        high = 0 if not data.high else round(data.high, 2)
        low = 0 if not data.low else round(data.low, 2)

        k = None if data.stochK is None else round(data.stochK, 2)
        d = None if data.stochD is None else round(data.stochD, 2)

        ema6 = None if data.ema6 is None else round(data.ema6, 2)
        ema18 = None if data.ema18 is None else round(data.ema18, 2)
        ema50 = None if data.ema50 is None else round(data.ema50, 2)
        ema100 = None if data.ema100 is None else round(data.ema100, 2)
        ema200 = None if data.ema200 is None else round(data.ema200, 2)

        bb_high = None if data.bollingerBandHigh is None else round(data.bollingerBandHigh, 2)
        bb_low = None if data.bollingerBandLow is None else round(data.bollingerBandLow, 2)

        macd = None if data.macd is None else round(data.macd, 2)
        macd_signal = None if data.macdEMA is None else round(data.macdEMA, 2)

        return [symbol, date, open, close, high, low, k, d, 
                ema6, ema18, ema50, ema100, ema200,
                bb_high, bb_low,
                macd, macd_signal]

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

                ema6 = None if not row[8] else float(row[8])
                ema18 = None if not row[9] else float(row[9])
                ema50 = None if not row[10] else float(row[10])
                ema100 = None if not row[11] else float(row[11])
                ema200 = None if not row[12] else float(row[12])

                bb_high = None if not row[13] else float(row[13])
                bb_low = None if not row[14] else float(row[14])

                macd = None if not row[15] else float(row[15])
                macd_signal = None if not row[16] else float(row[16])
                
                event = EventImpulsePullback(contract, datetime, open, close, high, low, k, d, 
                                            ema50, ema100, ema200, ema6, ema18,
                                            bb_high, bb_low,
                                            macd, macd_signal)
                contractEvents.append(event)
            line_count += 1
        return contractEvents

    def setupRunStrategy(self, events: List[Event], dynamicParameters: List[List[float]]):
        config = BacktestConfigs()
        isForStockPerformance = True if config.action == BacktestAction.runStrategyPerformance or config.action == BacktestAction.runStrategyPerformanceWithDynamicParameters else False
        strategyConfig: StrategyImpulsePullbackConfig = StrategyConfigFactory.createImpulsePullbackStrategyFor(
            MarketManager.getMarketFor(config.country), config.timezone)
        if dynamicParameters is not None:
            strategyConfig.willingToLose = float(dynamicParameters[0])
            strategyConfig.winLossRatio = float(dynamicParameters[1])
        self.strategyModel = self.RunStrategyImpulsePullbackModel(
            StrategyImpulsePullback(), strategyConfig, isForStockPerformance)
        for event in events:
            identifier = self.uniqueIdentifier(
                event.contract.symbol, event.datetime.date())
            self.strategyModel.eventsMapper[identifier] = event

    def getStrategyData(self, event: Event, events: List[Event], index: int) -> StrategyData:
        strategyConfig: StrategyImpulsePullbackConfig = self.strategyModel.strategyConfig
        event: EventImpulsePullback = event
        events: List[EventImpulsePullback] = events
        previousEvents = self.getPreviousEvents(
            event, strategyConfig.daysBeforeToDownload)
        if previousEvents is None or len(previousEvents) < strategyConfig.daysBefore:
            return None
        previousEventsFiltered = previousEvents[-strategyConfig.daysBefore:]
        balance = min(30000, self.getBalance())
        return StrategyImpulsePullbackData(contract=event.contract,
                                            totalCash=balance,
                                            event=event,
                                            previousEvents=previousEventsFiltered,
                                            today=event.datetime.date(),
                                            now=event.datetime)

    def getPreviousEvents(self, event: EventImpulsePullback, daysBefore: int = 5):
        model: BacktestImpulsePullbackModule.RunStrategyImpulsePullbackModel = self.strategyModel
        previousDays: List[EventImpulsePullback] = []
        for x in range(1, daysBefore):
            previousDate = event.datetime.date()+timedelta(days=-x)
            identifier = self.uniqueIdentifier(
                event.contract.symbol, previousDate)
            if identifier in model.eventsMapper:
                previousDays.append(model.eventsMapper[identifier])

        previousDays.reverse()
        return previousDays

    def handleStrategyResult(self, event: Event, events: List[Event], result: StrategyResult, currentPosition: int):
        result: StrategyImpulsePullbackResult = result
        model: BacktestImpulsePullbackModule.RunStrategyImpulsePullbackModel = self.strategyModel
        strategyConfig: StrategyImpulsePullbackConfig = model.strategyConfig
        if ((result.type == StrategyResultType.Buy or result.type == StrategyResultType.Sell) and model.tradesAvailable > 0):
            model.nextDayTrades[result.event.contract.symbol] = result
        else:
            for key, position in model.positions.items():
                if key.split("_")[0] == event.contract.symbol:
                    lista = list(position)
                    lista[3] = event
                    model.positions[key] = tuple(lista)
    
    def validateCurrentDay(self, event: Event):
        model: BacktestImpulsePullbackModule.RunStrategyImpulsePullbackModel = self.strategyModel
        strategyConfig: StrategyImpulsePullbackConfig = model.strategyConfig
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

            model.currentDay = None
        
        if event.contract.symbol in model.nextDayTrades:
            result: StrategyImpulsePullbackResult = model.nextDayTrades[event.contract.symbol]
            order: BracketOrder = result.bracketOrder
            if order.parentOrder.size > 0:
                if order.parentOrder.price < event.high and order.parentOrder.price > event.low:
                    identifier = self.uniqueIdentifier(result.contract.symbol, event.datetime.date())
                    model.positions[identifier] = (order,
                                                    Position(contract=result.contract, size=order.parentOrder.size),
                                                    event.datetime.date(),
                                                    event)
                    print(result)
                    print("%s Position for %s" % (event.datetime.date(), event.contract.symbol))
                    model.positionIPDates[identifier] = event.datetime.date()
                    model.positionIPHolds[identifier] = strategyConfig.maxPeriodsToHoldPosition
                    model.tradesAvailable -= 1
                    newFill = FillDB(result.contract.symbol, result.event.datetime.date(
                    ), result.contract.country, strategyConfig.type)
                    model.databaseModule.createFill(newFill)
            model.nextDayTrades.pop(event.contract.symbol)

    def handleEndOfDayIfNecessary(self, event: Event, events: List[Event], currentPosition: int):
        model: BacktestImpulsePullbackModule.RunStrategyImpulsePullbackModel = self.strategyModel
        model.currentDay = event.datetime.date()

        if ((len(events) > currentPosition+1 and events[currentPosition+1].datetime.date() != model.currentDay) or
                (len(events) == currentPosition+1)):
            self.handleProfitAndStop()
            self.handleExpiredFills()

    def handleProfitAndStop(self):
        model: BacktestImpulsePullbackModule.RunStrategyImpulsePullbackModel = self.strategyModel
        reportModule: ReportImpulsePullbackModule = self.reportModule
        positions = model.positions.copy()
        if (len(positions.values()) > 0):
            for key, (bracketOrder, position, positionDate, event) in positions.items():
                bracketOrder: BracketOrder = bracketOrder
                if self.isStopLoss(event, bracketOrder):
                    mainOrder: Order = bracketOrder.parentOrder
                    stopOrder: Order = bracketOrder.stopLossOrder
                    loss = abs(stopOrder.price*stopOrder.size -
                                mainOrder.price*mainOrder.size)
                    candlesHold = model.positionIPHolds[key]

                    reportModule.createStopLossResult(
                        event, bracketOrder, positionDate, loss, model.cashAvailable, candlesHold)

                    model.positions.pop(key)
                    model.positionIPDates.pop(key)
                    model.positionIPHolds.pop(key)

                    if model.isForStockPerformance == False:
                        model.cashAvailable -= loss
                elif self.isTakeProfit(event, bracketOrder):
                    mainOrder: Order = bracketOrder.parentOrder
                    profitOrder: Order = bracketOrder.takeProfitOrder
                    profit = abs(profitOrder.price*profitOrder.size -
                                    mainOrder.price*mainOrder.size)
                    candlesHold = model.positionIPHolds[key]

                    reportModule.createTakeProfitResult(
                        event, bracketOrder, positionDate, profit, model.cashAvailable, candlesHold)

                    model.positions.pop(key)
                    model.positionIPDates.pop(key)
                    model.positionIPHolds.pop(key)

                    if model.isForStockPerformance == False:
                        model.cashAvailable += profit

    def handleExpiredFills(self):
        model: BacktestImpulsePullbackModule.RunStrategyImpulsePullbackModel = self.strategyModel
        reportModule: ReportImpulsePullbackModule = self.reportModule
        positions = model.positions.copy()
        if (len(positions.values()) > 0):
            for key, (bracketOrder, position, positionDate, event) in positions.items():
                bracketOrder: BracketOrder = bracketOrder
                ipPostionHold = model.positionIPHolds[key]
                if self.isPositionExpired(event, positionDate, ipPostionHold):
                    if self.isProfit(event, bracketOrder):
                        mainOrder: Order = bracketOrder.parentOrder
                        profit = abs(event.close*mainOrder.size -
                                        mainOrder.price*mainOrder.size)
                        candlesHold = model.positionIPHolds[key]

                        reportModule.createProfitResult(
                            event, bracketOrder, positionDate, profit, model.cashAvailable, candlesHold)

                        if model.isForStockPerformance == False:
                            model.cashAvailable += profit
                    else:
                        mainOrder: Order = bracketOrder.parentOrder
                        loss = abs(event.close*mainOrder.size -
                                    mainOrder.price*mainOrder.size)
                        candlesHold = model.positionIPHolds[key]

                        reportModule.createLossResult(
                            event, bracketOrder, positionDate, loss, model.cashAvailable, candlesHold)

                        if model.isForStockPerformance == False:
                            model.cashAvailable -= loss

                    identifier = self.uniqueIdentifier(event.contract.symbol, positionDate)
                    model.positions.pop(identifier)
                    model.positionIPDates.pop(identifier)
                    model.positionIPHolds.pop(key)

    def isPositionExpired(self, event: EventImpulsePullback, positionDate: date, candlesToHold: int) -> bool:
        config: StrategyImpulsePullbackConfig = self.strategyModel.strategyConfig
        return event.datetime.date() >= (positionDate+timedelta(days=candlesToHold))

    def isStopLoss(self, event: EventImpulsePullback, bracketOrder: BracketOrder) -> bool:
        mainOrder = bracketOrder.parentOrder
        stopOrder = bracketOrder.stopLossOrder
        return ((mainOrder.action == OrderAction.Buy and event.low <= stopOrder.price) or
                (mainOrder.action == OrderAction.Sell and event.high >= stopOrder.price))

    def isTakeProfit(self, event: EventImpulsePullback, bracketOrder: BracketOrder) -> bool:
        mainOrder = bracketOrder.parentOrder
        takeProfitOrder = bracketOrder.takeProfitOrder
        return ((mainOrder.action == OrderAction.Buy and event.high >= takeProfitOrder.price) or
                (mainOrder.action == OrderAction.Sell and event.low <= takeProfitOrder.price))

    def isProfit(self, event: EventImpulsePullback, bracketOrder: BracketOrder) -> bool:
        mainOrder = bracketOrder.parentOrder
        return ((mainOrder.action == OrderAction.Buy and mainOrder.price < event.close) or
                (mainOrder.action == OrderAction.Sell and mainOrder.price > event.close))

    def clearOldFills(self, event: Event):
        model: BacktestImpulsePullbackModule.RunStrategyImpulsePullbackModel = self.strategyModel
        fills = model.databaseModule.getFills()
        limitDate = event.datetime.date()-timedelta(days=40)
        filteredFills = list(filter(lambda x: (x.date < limitDate and x.strategy == StrategyType.impulse_pullback), fills))
        model.databaseModule.deleteFills(filteredFills)

    def getFill(self, contract: Contract):
        model: BacktestImpulsePullbackModule.RunStrategyImpulsePullbackModel = self.strategyModel
        fills = model.databaseModule.getFills()
        filteredFills = list(
            filter(lambda x: (contract.symbol == x.symbol and x.strategy == StrategyType.impulse_pullback), fills))
        filteredFills.sort(key=lambda x: x.date, reverse=True)
        if len(filteredFills) > 0:
            return filteredFills[0]
        return None