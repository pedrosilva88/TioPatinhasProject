from strategy.configs.models import StrategyType
from backtest.configs.models import BacktestConfigs
from backtest.backtest_zigzag_module import BacktestZigZagModule
from backtest.backtest_module import BacktestModule

def createBacktestModule() -> BacktestModule :
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