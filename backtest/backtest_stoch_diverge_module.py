from datetime import date, timedelta
from strategy.models import StrategyData
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
from models.base_models import Contract, Event
from backtest.models.base_models import BacktestAction, ContractSymbol
from typing import Any, List, Tuple, Union
from strategy.strategy import Strategy
from strategy.configs.models import StrategyConfig
from backtest.backtest_module import BacktestModule
from strategy.stoch_diverge.models import StrategyStochDivergeData

class BacktestStochDivergeModule(BacktestModule):
    class RunStrategyStochDivergeModel(BacktestModule.RunStrategyModel):
        databaseModule: DatabaseModule
        positionStochDates: Union[str, date]
        eventsMapper: Union[str, EventStochDiverge]
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