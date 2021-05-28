from backtest.backtest_zigzag_module import BacktestZigZagModule
from backtest.backtest_module import BacktestModule

if __name__ == '__main__':
    try:
        module = BacktestZigZagModule()
        module.runBacktest()

        # Testing this Stock
        # Change the file scan_to_download
        # GLBE,SMART,USD,8,2,6,0,0,8,100
    except (KeyboardInterrupt, SystemExit):
        None