from configs.models import Provider
from country_config.models import Country
from backtest.models.base_models import BacktestAction
from strategy.configs.models import StrategyType

runStartegyFilename = "scan_to_run_strategy.csv"
downloadFilename = "scan_to_download.csv"

scannerPath = "backtest/scanner/Data/CSV/%s/%s/%s/%s"
dataCSVStocksPath = "backtest/Data/CSV/%s/%s/%s/Stocks"
dataCSVReportsPath = "backtest/Data/CSV/%s/%s/%s/Report"

def getPathFileToScanStocks(provider: Provider, country: Country, strategy: StrategyType, action: BacktestAction):
    filename = runStartegyFilename if action == BacktestAction.runStrategy else downloadFilename
    # backtest/scanner/Data/CSV/TWS/ZigZag/US/scan_to_download.csv
    return scannerPath % (provider.value, strategy.value, country.code, filename)

def getPathFolderToSaveStocksData(provider: Provider, country: Country, strategy: StrategyType):
    # backtest/Data/CSV/TWS/ZigZag/US/Stocks
    return dataCSVStocksPath % (provider.value, strategy.value, country.code)

def getPathFolderToSaveReports(provider: Provider, country: Country, strategy: StrategyType):
    # backtest/Data/CSV/TWS/ZigZag/US/Report
    return dataCSVStocksPath % (provider.value, strategy.value, country.code)
