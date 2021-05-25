from backtest.backtest import Backtest

if __name__ == '__main__':
    try:
        Backtest.downloadStocksData()
    except (KeyboardInterrupt, SystemExit):
        None