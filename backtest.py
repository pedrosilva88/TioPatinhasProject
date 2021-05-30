from backtest.backtest_module import BacktestModule
from strategy.configs.models import StrategyType
from backtest.configs.models import BacktestConfigs
from backtest.backtest_zigzag_module import BacktestZigZagModule

def createBacktestModule():
    config = BacktestConfigs()
    if config.strategyType == StrategyType.zigzag:
        return BacktestZigZagModule()
    return None

if __name__ == '__main__':
    try:
        module: BacktestModule = createBacktestModule()
        module.runBacktest()
    except (KeyboardInterrupt, SystemExit):
        None