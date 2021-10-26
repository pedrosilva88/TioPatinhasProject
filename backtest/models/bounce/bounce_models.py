from datetime import datetime
from strategy.bounce.models import StrategyBounceResultType
from models.base_models import Contract, OrderAction
from backtest.models.base_models import BacktestResult, BacktestResultType

class BacktestBounceResult(BacktestResult):
    criteria: StrategyBounceResultType
    def __init__(self, contract: Contract, action: OrderAction, type: BacktestResultType, createTradeDate: datetime, closeTradeDate: datetime, 
                        pnl: float, priceCreateTrade: float, priceCloseTrade: float, size: int, totalInvested: float, cash: float, criteria: StrategyBounceResultType):
        super().__init__(contract, action, type, createTradeDate, closeTradeDate, pnl, priceCreateTrade, priceCloseTrade, size, totalInvested, cash)
        self.criteria = criteria