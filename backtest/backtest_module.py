from strategy.historical_data import HistoricalData
from mplfinance import plot
import matplotlib.dates as mpl_dates
import pandas as pd

from pandas.core.frame import DataFrame

from backtest.reports.report_module import ReportModule
import csv
from datetime import date, datetime
from strategy.models import StrategyData, StrategyResult
from helpers.date_timezone import DateSystemFormat, Helpers
from strategy.configs.models import StrategyConfig, StrategyType
from strategy.strategy import Strategy
from typing import Any, List, Tuple, Union
from backtest.scanner.scanner_manager import BacktestScannerManager
from models.base_models import BracketOrder, Contract, Event, Position
from backtest.models.base_models import BacktestAction, ContractSymbol
from backtest.configs.models import BacktestConfigs
from backtest.download_module.download_module import BacktestDownloadModule
from provider_factory.provider_module import ProviderModule
from scanner import Scanner

class BacktestModule:
    class RunStrategyModel:
        strategy: Strategy
        positions: Union[str, Tuple[BracketOrder, Position, date, Event]]
        cashAvailable: float
        isForStockPerformance: bool
        strategyConfig: StrategyConfig

        def __init__(self, strategy: Strategy, strategyConfig: StrategyConfig, isForStockPerformance: bool) -> None:
            config = BacktestConfigs()
            self.strategy = strategy
            self.strategyConfig = strategyConfig
            self.positions = dict()
            self.isForStockPerformance = isForStockPerformance
            self.cashAvailable = float(config.wallet)

    strategyModel: RunStrategyModel
    reportModule = ReportModule

    def __init__(self) -> None:
        self.reportModule = ReportModule()

    def runBacktest(self):
        config = BacktestConfigs()
        if config.action == BacktestAction.downloadData:
            self.runDownloadStocksAction()
        elif config.action == BacktestAction.runStrategy or config.action == BacktestAction.runStrategyPerformance:
            self.runStrategyAction()
        elif config.action == BacktestAction.showGraph:
            self.runShowGraphAction()
        elif config.action == BacktestAction.runStrategyPerformanceWithDynamicParameters or config.action == BacktestAction.runStrategyWithDynamicParameters:
            self.runStrategyWithDynamicParametersAction()
        else: 
            print("🚨 Unkwon Action - nothing to do 🚨")

    #### ABSTRACT METHODS ####  

    def addIndicatorsToStocksData(self, stocksData: Union[ContractSymbol, Tuple[Contract, List[Event]]], config: BacktestConfigs) -> Union[ContractSymbol, Tuple[Contract, List[Event]]]:
        pass
    
    def getStockFileHeaderRow(self) -> List[str]:
        return ["Symbol", "Date", "Open", "Close", "High", "Low"]

    def getStockFileDataRow(self, contract: Contract, data: Event) -> List[Any]:
        symbol = contract.symbol
        date = Helpers.dateToString(data.datetime, format=DateSystemFormat)

        open = 0 if not data.open else round(data.open, 2)
        close = 0 if not data.close else round(data.close, 2)
        high = 0 if not data.high else round(data.high, 2)
        low = 0 if not data.low else round(data.low, 2)

        return [symbol, date, open, close, high, low]

    def parseRawCSVFile(self, reader: csv.reader) -> List[Event]:
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
                event = Event(contract, datetime, open, close, high, low)
                contractEvents.append(event)
            line_count += 1
        return contractEvents

    def setupRunStrategy(self, events: List[Event], dynamicParameters: List[List[float]]):
        pass

    def getStrategyData(self) -> StrategyData:
        pass

    def handleStrategyResult(self, event: Event, events: List[Event], result: StrategyResult, currentPosition: int):
        pass

    def validateCurrentDay(self, event: Event):
        pass

    def handleEndOfDayIfNecessary(self, event: Event, events: List[Event], currentPosition: int):
        pass

    #### ACTIONS ####

    def runDownloadStocksAction(self):
        config = BacktestConfigs()
        stocksData = self.downloadStocksData(config)
        events = stocksData
        if config.strategyType is not StrategyType.none and config.strategyType is not StrategyType.combined:
            events = self.addIndicatorsToStocksData(stocksData, config)
        self.saveDataInCSVFiles(config, events)

    def runStrategyAction(self):
        print("🧙‍♀️ Lets Start running Strategy 🧙‍♀️")
        events = self.contractsToRunStrategy()
        self.runStrategy(events)

        print("🧙‍♀️ Saving Reports 🧙‍♀️")
        if self.strategyModel.isForStockPerformance:
            self.reportModule.createReportPerformance()

        self.reportModule.createReportTrades(self.strategyModel.isForStockPerformance)
    
    def runStrategyWithDynamicParametersAction(self):
        print("🧙‍♀️ Lets Start running Strategy with dynamic parameters 🧙‍♀️")
        events = self.contractsToRunStrategy()
        config = BacktestConfigs()
        for parameters in config.dynamicParameters:
            self.runStrategy(events, parameters)
            self.reportModule.createStrategyResult(parameters)
            self.reportModule.results = []
            self.reportModule.createStrategyReport(self.strategyModel.isForStockPerformance)
            self.reportModule.strategyResults = []
            
    def runShowGraphAction(self):
        self.showGraph()

    #### STRATEGIES ####

    def contractsToRunStrategy(self) -> List[Event]:
        print("🧙‍♀️ Lets Start 🧙‍♀️")
        config = BacktestConfigs()
        stocksData = BacktestScannerManager.loadStockFiles(config.provider, config.country, config.strategyType, config.action, self.parseRawCSVFile)
        print("🧙‍♀️ Compute Strategy Indicators 🧙‍♀️")
        strategyStocksData = self.addIndicatorsToStocksData(stocksData, config)
        allContractsEvents = []
        for stockSymbol, (stock, bars) in strategyStocksData.items():
            allContractsEvents += bars
        print("🧙‍♀️ Sort all Events by date 🧙‍♀️")
        allContractsEvents.sort(key=lambda x: x.datetime, reverse=False)
        return allContractsEvents

    def getBalance(self):
        balance = 0
        if self.strategyModel.isForStockPerformance:
            balance = self.strategyModel.cashAvailable
        else:
            totalInPostions = self.calculateTotalInPositions()
            balance = self.strategyModel.cashAvailable - totalInPostions
        return balance

    def runStrategy(self, events: List[Event], dynamicParameters: List[List[float]] = None):
        print("🧙‍♀️ Setup strategy 🧙‍♀️")
        self.setupRunStrategy(events, dynamicParameters)
        print("🧙‍♀️ Start running strategy 🧙‍♀️")

        i = 0
        for event in events:    
            self.validateCurrentDay(event)
            data = self.getStrategyData(event, events, i)
            if data is not None:
                result = self.strategyModel.strategy.run(data, self.strategyModel.strategyConfig)
                self.handleStrategyResult(event, events, result, i)
            self.handleEndOfDayIfNecessary(event, events, i)
            i += 1

    def calculateTotalInPositions(self):
        total = 0
        for key, (order, position, date, event) in self.strategyModel.positions.items():
            total += position.size * order.parentOrder.price
        return total

    def uniqueIdentifier(self, symbol: ContractSymbol, date: date) -> str:
        return ("%s_%s" % (symbol, date.strftime("%y%m%d")))

    #### SAVE IN CSV FILES ####

    def saveDataInCSVFiles(self, config: BacktestConfigs, stocksData: Union[ContractSymbol, Tuple[Contract, List[Event]]]):
        folder = BacktestScannerManager.getPathFolderToSaveStocksData(config.provider, config.country, config.strategyType)
        for contractSymbol, (contract, bars) in stocksData.items():
            filePath = ('%s/%s.csv' % (folder, contractSymbol))
            self.saveDataInCSVFile(filePath, contract, bars)

    def saveDataInCSVFile(self, filePath: str, contract: Contract, bars: List[Event]):
        with open(filePath, 'w', newline='') as file:
            writer = csv.writer(file)
            headerRow = self.getStockFileHeaderRow()
            writer.writerow(headerRow)
            for event in bars:
                row = self.getStockFileDataRow(contract, event)
                writer.writerow(row)

    #### DOWNLOAD ####

    def downloadStocksData(self, config: BacktestConfigs) -> Union[ContractSymbol, Tuple[Contract, List[Event]]]:
        client = ProviderModule.createClient(config.provider, config.providerConfigs)
        client.connect()
        stocks = Scanner.contratcsFrom(config.downloadModel.path)
        stocksData = BacktestDownloadModule.downloadStocks(client, stocks, config.downloadModel.numberOfDays, config.downloadModel.barSize)

        return stocksData

    #### Graph ####

    def showGraph(self):
        config = BacktestConfigs()
        client = ProviderModule.createClient(config.provider, config.providerConfigs)
        client.connect()
        days = (config.graphEndDate - config.graphStartDate).days
        stockData = BacktestDownloadModule.downloadStock(client, config.graphContract, days, config.downloadModel.barSize, config.graphEndDate)
        events = HistoricalData.computeEventsForZigZagStrategy(stockData, config.strategy)
        self.showPlot(config.graphContract, events)
    
    def showPlot(self, contract: Contract, events: List[Event]):
        ohlc = DataFrame.from_records([event.to_dict() for event in events], columns=['datetime', 'open', 'high', 'low', 'close'])
        ohlc.index = pd.DatetimeIndex(ohlc['datetime'])
        ohlc['datetime'] = pd.to_datetime(ohlc['datetime'])
        ohlc['datetime'] = ohlc['datetime'].apply(mpl_dates.date2num)
        ohlc = ohlc.astype(float)

        data: dict = self.addIndicatorsToGraph(events)
        plot(ohlc, type='candlestick', style='charles',
            title='Chart',
            ylabel='Price',
            alines=data)

    def addIndicatorsToGraph(self, events: List[Event]) -> List[float]:
        pass