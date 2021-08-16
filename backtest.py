from strategy.configs.models import StrategyType
from backtest.configs.models import BacktestConfigs
from backtest.backtest_zigzag_module import BacktestZigZagModule
from backtest.backtest_module import BacktestModule


def createBacktestModule() -> BacktestModule:
    config = BacktestConfigs()
    if config.strategyType == StrategyType.zigzag:
        return BacktestZigZagModule()
    return None


if __name__ == '__main__':
    try:
        module = createBacktestModule()
        module.runBacktest()
    except (KeyboardInterrupt, SystemExit):
        None


# from backtest.scanner.scanner_manager import BacktestScannerManager
# from scanner import Scanner
        # pathDownload = "backtest/scanner/Data/CSV/TWS/ZigZag/US/scan_to_download.csv"
        # pathStrategy = "backtest/scanner/Data/CSV/TWS/ZigZag/US/scan_to_run_strategy.csv"
        # stocksDownload = Scanner.contratcsFrom(pathDownload)
        # stocksStrategy = Scanner.contratcsFrom(pathStrategy)
        #
        # inDownloadArray = []
        # outDownloadArray = []
        # for item in stocksStrategy:
        #     exist = False
        #     for copy in stocksDownload:
        #         if copy.symbol == item.symbol:
        #             exist = True
        #             break
        #     if exist:
        #         inDownloadArray.append(item)
        #     else:
        #         outDownloadArray.append(item)
        # print(len(inDownloadArray))
        # print(len(outDownloadArray))
        # for i in outDownloadArray:
        #     print("%s,%s,%s" % (i.symbol, i.exchange, i.currency))
