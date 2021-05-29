import sys, os, csv
from typing import List
from scanner.scanner import Scanner
from backtest.configs.models import BacktestConfigs
from configs.models import Provider
from country_config.models import Country
from models.base_models import Contract, Event
from backtest.models.base_models import BacktestAction
from strategy.configs.models import StrategyType

runStartegyFilename = "scan_to_run_strategy.csv"
downloadFilename = "scan_to_download.csv"

scannerPath = "backtest/scanner/Data/CSV/%s/%s/%s/%s"
dataCSVStocksPath = "backtest/data/CSV/%s/%s/%s/Stocks"
dataCSVStockFilePath = "backtest/data/CSV/%s/%s/%s/Stocks/%s.csv"
dataCSVReportsPath = "backtest/data/CSV/%s/%s/%s/Report"

class BacktestScannerManager:
    def getPathFileToScanStocks(provider: Provider, country: Country, strategy: StrategyType, action: BacktestAction) -> str:
        filename = runStartegyFilename if action == BacktestAction.runStrategy else downloadFilename
        # backtest/scanner/Data/CSV/TWS/ZigZag/US/scan_to_download.csv
        return scannerPath % (provider.value, strategy.value, country.code, filename)

    def getPathFolderToSaveStocksData(provider: Provider, country: Country, strategy: StrategyType) -> str:
        # backtest/Data/CSV/TWS/ZigZag/US/Stocks
        return dataCSVStocksPath % (provider.value, strategy.value, country.code)

    def getPathFileToReadStocksData(contract: Contract, provider: Provider, country: Country, strategy: StrategyType) -> str:
        # backtest/Data/CSV/TWS/ZigZag/US/Stocks/APPL.csv
        return dataCSVStockFilePath % (provider.value, strategy.value, country.code, contract.symbol)

    def getPathFolderToSaveReports(provider: Provider, country: Country, strategy: StrategyType) -> str:
        # backtest/Data/CSV/TWS/ZigZag/US/Report
        return dataCSVStocksPath % (provider.value, strategy.value, country.code)

    def loadStockFiles(config: BacktestConfigs, parserBlock) -> List[Event]:
        filePathForStocks = BacktestScannerManager.getPathFileToScanStocks(config.provider, config.country, config.strategyType, config.action)
        contracts = Scanner.contratcsFrom(filePathForStocks)

        total = len(contracts)
        current = 0
        allContractsEvents = []
        for contract in contracts:
            current += 1
            sys.stdout.write("\t Fetching CSV Files: %i/%i \r" % (current, total) )
            if current <= total-1:
                sys.stdout.flush()
            else:
                print("")

            filePathForStock =  BacktestScannerManager.getPathFileToReadStocksData(contract, config.provider, config.country, config.strategyType, config.action)
            if not os.path.isfile(filePathForStock):
                print("File not found ", filePathForStock)
                continue
            contractEvents = []
            with open(filePathForStock) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                contractEvents = parserBlock(csv_reader)
            allContractsEvents += contractEvents
        return allContractsEvents



