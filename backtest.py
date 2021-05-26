import asyncio
from backtest.backtest_module import BacktestModule

if __name__ == '__main__':
    try:
        BacktestModule.downloadStocksData()
    except (KeyboardInterrupt, SystemExit):
        None