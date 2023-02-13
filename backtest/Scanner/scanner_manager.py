import sys, os, csv
from typing import List, Tuple, Union
from scanner.scanner import Scanner
from configs.models import Provider
from country_config.models import Country
from models.base_models import Contract, Event
from backtest.models.base_models import BacktestAction
from strategy.configs.models import StrategyType

runStartegyFilename = "scan_to_run_strategy.csv"
downloadFilename = "scan_to_download.csv"

scannerPath = "backtest/scanner/data/CSV/%s/%s/%s/%s"
dataCSVStocksPath = "backtest/data/CSV/%s/%s/%s/Stocks"
dataCSVStockFilePath = "backtest/data/CSV/%s/%s/%s/Stocks/%s.csv"
dataCSVReportsPath = "backtest/data/CSV/%s/%s/%s/Report/%s"

reportTradesFilename = "ResultTrades.csv"
reportContractsPerformanceFilename = "ResultContractsPerformance.csv"
reportTradesPerformanceFilename = "ResultTradesForPerformance.csv"

reportStrategyResultFilename = "ReportStrategyResult.csv"
reportStrategyResultForPerformanceFilename = "ReportStrategyResultForPerformance.csv"

class BacktestScannerManager:
    def getPathFileToScanStocks(provider: Provider, country: Country, strategy: StrategyType, action: BacktestAction) -> str:
        filename = runStartegyFilename if action == BacktestAction.runStrategy or action == BacktestAction.runStrategyWithDynamicParameters else downloadFilename
        # backtest/scanner/Data/CSV/TWS/ZigZag/US/scan_to_download.csv
        return scannerPath % (provider.value, strategy.folderName, country.code, filename)

    def getPathFolderToSaveStocksData(provider: Provider, country: Country, strategy: StrategyType) -> str:
        # backtest/Data/CSV/TWS/Zigzag/US/Stocks
        return dataCSVStocksPath % (provider.value, strategy.folderName, country.code)

    def getPathFileToReadStocksData(contract: Contract, provider: Provider, country: Country, strategy: StrategyType) -> str:
        # backtest/Data/CSV/TWS/_raw/US/Stocks/APPL.csv
        return dataCSVStockFilePath % (provider.value, StrategyType.none.folderName, country.code, contract.symbol)

    def getPathFileToSaveReports(provider: Provider, country: Country, strategy: StrategyType, filename: str) -> str:
        # backtest/Data/CSV/TWS/ZigZag/US/Report
        return dataCSVReportsPath % (provider.value, strategy.folderName, country.code, filename)

    def loadStockFiles(provider: Provider, country: Country, strategy: StrategyType, action: BacktestAction,  parserBlock) -> Union[str, Tuple[Contract, List[Event]]]:
        filePathForStocks = BacktestScannerManager.getPathFileToScanStocks(provider, country, strategy, action)
        contracts = Scanner.contratcsFrom(filePathForStocks)

        total = len(contracts)
        current = 0
        allContractsEvents = dict()
        for contract in contracts:
            current += 1
            sys.stdout.write("\t Fetching CSV Files: %i/%i \r" % (current, total) )
            if current <= total-1:
                sys.stdout.flush()
            else:
                print("")

            filePathForStock =  BacktestScannerManager.getPathFileToReadStocksData(contract, provider, country, strategy)
            if not os.path.isfile(filePathForStock):
                print("File not found ", filePathForStock)
                continue
            contractEvents = []
            with open(filePathForStock) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                contractEvents = parserBlock(csv_reader)
            allContractsEvents[contract.symbol] = (contract, contractEvents)
        return allContractsEvents



