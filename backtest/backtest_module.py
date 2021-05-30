
import csv
from typing import Any, List, Tuple, Union
from backtest.scanner.scanner_manager import BacktestScannerManager
from models.base_models import Contract, Event
from backtest.models.base_models import BacktestAction, ContractSymbol
from backtest.configs.models import BacktestConfigs
from backtest.download_module.download_module import BacktestDownloadModule
from provider_factory.provider_module import ProviderModule
from scanner import Scanner

class BacktestModule:
    def runBacktest(self):
        config = BacktestConfigs()
        if config.action == BacktestAction.downloadData:
            self.runDownloadStocksAction()
        elif config.action == BacktestAction.runStrategy:
            self.runStrategyAction()
        elif config.action == BacktestAction.runStockPerformance:
            self.runShowGraphAction()
        elif config.action == BacktestAction.showGraph:
            self.runShowGraphAction()
        else: 
            print("🚨 Unkwon Action - nothing to do 🚨")

    #### ABSTRACT METHODS ####  

    def addIndicatorsToStocksData(self, stocksData: Union[ContractSymbol, Tuple[Contract, List[Event]]], config: BacktestConfigs) -> Union[ContractSymbol, Tuple[Contract, List[Event]]]:
        pass
    
    def getStockFileHeaderRow(self) -> List[str]:
        pass

    def getStockFileDataRow(self) -> List[Any]:
        pass

    def parseCSVFile(reader: csv.reader) -> List[Event]:
        pass

    #### ACTIONS ####

    def runDownloadStocksAction(self):
        config = BacktestConfigs()
        stocksData = self.downloadStocksData(config)
        strategyStocksData = self.addIndicatorsToStocksData(stocksData, config)
        self.saveDataInCSVFiles(config, strategyStocksData)

    def runStrategyAction(self):
        config = BacktestConfigs()
        allContractsEvents = BacktestScannerManager.loadStockFiles(config, self.parseCSVFile)
        print("🧙‍♀️ Sort all Events by date 🧙‍♀️")
        allContractsEvents.sort(key=lambda x: x.datetime, reverse=False)
        
    def runStrategyPerformanceAction(self):
        pass

    def runShowGraphAction(self):
        pass

    #### STRATEGIES ####

    def runStrategy(self):
        print("🧙‍♀️ Start running strategy 🧙‍♀️")
        model = BackTestSwing()
        report = BackTestReport()
        runStrategy(backtestModel=model, backtestReport=report, models=models)
        path = ("backtest/Data/CSV/%s/ZigZag/Report" % (model.countryConfig.key.code))
        report.showReport(path, True)

    #### SAVE IN CSV FILES ####

    def saveDataInCSVFiles(self, config: BacktestConfigs, stocksData: Union[ContractSymbol, Tuple[Contract, List[Event]]]):
        folder = getPathFolderToSaveStocksData(config.provider, config.country, config.strategyType)
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

#     def saveReportPerformance(self, path: str, stocksPath: str, data, countryConfig: CountryConfig):
#         scanner = Scanner()
#         scanner.fetchStocksFromCSVFile(path=stocksPath, nItems=0)
#         stocks = scanner.stocks
#         name = ("%s/ResultsStockPerformance.csv" % path)
#         with open(name, 'w', newline='') as file:
#             writer = csv.writer(file)
#             writer.writerow(["Symbol", "Exchange", "Currency", "OPGs Found", "Take Profit", "Profit", "StopLoss", "Loss", "Wins", "%"])
#             for key, item in data.items():
#                 total = item[0]+item[1]+item[2]+item[3]
#                 wins = item[0]+item[1]
#                 writer.writerow([key,
#                                 "SMART",
#                                 countryConfig.currency,
#                                 total,
#                                 item[0],
#                                 item[1],
#                                 item[2],
#                                 item[3],
#                                 wins,
#                                 (wins/total)*100])
#                 item = list(filter(lambda x : x.symbol == key, stocks)).pop()
#                 stocks.remove(item)
#             for item in stocks:
#                 writer.writerow([item.symbol,
#                                 "SMART",
#                                 countryConfig.currency,
#                                 0,
#                                 0,
#                                 0,
#                                 0,
#                                 0,
#                                 0,
#                                 0])

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

#     def updateStockPerformance(self, ticker: Ticker, type: BackTestResultType):
#         array = []
#         if ticker.contract.symbol in self.stockPerformance:
#             array = self.stockPerformance[ticker.contract.symbol]
#         else:
#             array = [0,0,0,0]

#         if type == BackTestResultType.takeProfit:
#             array[0] += 1
#         elif type == BackTestResultType.profit:
#             array[1] += 1
#         elif type == BackTestResultType.stopLoss:
#             array[2] += 1
#         elif type == BackTestResultType.loss:
#             array[3] += 1

#         self.stockPerformance[ticker.contract.symbol] = array