
from backtest.reports.report_module import ReportModule
import csv
from datetime import date, datetime
from strategy.models import StrategyData, StrategyResult

from strategy.configs.models import StrategyConfig
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
        pass

    def getStockFileDataRow(self) -> List[Any]:
        pass

    def parseCSVFile(self, reader: csv.reader) -> List[Event]:
        pass

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
        strategyStocksData = self.addIndicatorsToStocksData(stocksData, config)
        self.saveDataInCSVFiles(config, strategyStocksData)

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
            

    def runShowGraphAction(self):
        pass

    #### STRATEGIES ####

    def contractsToRunStrategy(self) -> List[Event]:
        print("🧙‍♀️ Lets Start 🧙‍♀️")
        config = BacktestConfigs()
        allContractsEvents = BacktestScannerManager.loadStockFiles(config.provider, config.country, config.strategyType, config.action, self.parseCSVFile)
        print("🧙‍♀️ Sort all Events by date 🧙‍♀️")
        allContractsEvents.sort(key=lambda x: x.datetime, reverse=False)
        return allContractsEvents

    def getBalance(self):
        balance = 0
        if self.strategyModel.isForStockPerformance:
            balance = self.strategyModel.cashAvailable
        else:
            totalInPostions = self.calculateTotalInPositions()
            balance = min(150000, (self.strategyModel.cashAvailable - totalInPostions))
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


# # Reports
# class BackTestReport():
#     results: [str, [BackTestResult]] = dict()
#     trades: [str, [str]] = dict()
#     stockPerformance = dict()

#     def saveReportResultInFile(self, path: str, data:[[]]):
#         name = ("%s/ResultsPnL.csv" % path)
#         with open(name, 'w', newline='') as file:
#             writer = csv.writer(file)
#             writer.writerow(["Date", "PnL", "Trades"])
#             for model in data:
#                 writer.writerow(model)

#     def saveReportTradesInFile(self, path: str, data:[[]], zigzag: bool = False, fileName: str = "ResultsTrades.csv"):
#         name = ("%s/%s" % (path, fileName))
#         with open(name, 'w', newline='') as file:
#             writer = csv.writer(file)
#             if zigzag:
#                 writer.writerow(["Date", "Symbol", "Result", "PnL", "Price CreateTrade", "Price CloseTrade", "Size", "Order Date", "Total Invested", "Open Price", "YSTD Close Price", "Action", "Cash"])
#             else:
#                 writer.writerow(["Date", "Symbol", "Result", "PnL", "Price CreateTrade", "Price CloseTrade", "Size", "Avg Volume",  "Volume 1st minute", "Total Invested", "Open Price", "YSTD Close Price", "Action", "Cash"])
#             for model in data:
#                 writer.writerow(model)

#     def showReport(self, path: str, zigzag: bool = False):
#         items = [[]]
#         for key, array in self.results.items():
#             total = 0
#             for item in array:
#                 total += item.pnl
#             items.append([key, total, len(array)])
#             print("%s: %.2f€ %d" % (key, total, len(array)))

#         self.saveReportResultInFile(path, items)

#         items = [[]]
#         for key, array in self.trades.items():
#             for item in array:
#                 items.append(item)

#         self.saveReportTradesInFile(path, items, zigzag)

#     def showPerformanceReport(self, path: str, stocksPath: str, countryConfig: CountryConfig):
#         self.saveReportPerformance(path, stocksPath, self.stockPerformance, countryConfig)

#         items = [[]]
#         for key, array in self.trades.items():
#             for item in array:
#                 items.append(item)

#         self.saveReportTradesInFile(path, items, True, "ResultsTradesForPerformance.csv")

#     def updateResults(self, key: str, value: BackTestResult):
#         if key in self.results:
#             self.results[key].append(value)
#         else:
#             self.results[key] = [value]

#     def updateTrades(self, key: str, ticker: Ticker, result: BackTestResult, zigzag: bool = False):
#         resultArray = []
#         resultArray.append(key) # date
#         resultArray.append(ticker.contract.symbol) # symbol
#         resultArray.append(result.type.emoji()) # ✅ or ✅ ✅ or ❌  or ❌ ❌
#         resultArray.append(result.pnl) # PnL
#         resultArray.append(result.priceCreateTrade) # Price CreateTrade
#         resultArray.append(result.priceCloseTrade) # Price CloseTrade
#         resultArray.append(result.size) # Size
        
#         if zigzag:
#             resultArray.append(result.orderDate) # Order Date
#         else:
#             resultArray.append(result.volumeFirstMinute) # VolumeFirstMinute
#             resultArray.append(result.averageVolume) # AverageVolume
            
#         resultArray.append(result.totalInvested) # Total Invested
#         resultArray.append(result.openPrice) # Open Price
#         resultArray.append(result.ystdClosePrice) # YSTD Close Price
#         resultArray.append(result.action) # Action Long or Short
#         resultArray.append(result.cash) # Cash
        
#         if key in self.trades:
#             self.trades[key].append(resultArray)
#         else:
#             self.trades[key] = [resultArray]

