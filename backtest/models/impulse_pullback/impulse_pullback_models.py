from datetime import datetime
from models.base_models import Contract, OrderAction
from backtest.models.base_models import BacktestResult, BacktestResultType

class BacktestImpulsePullbackResult(BacktestResult):
    def __init__(self, contract: Contract, action: OrderAction, type: BacktestResultType, createTradeDate: datetime, closeTradeDate: datetime, 
                        pnl: float, priceCreateTrade: float, priceCloseTrade: float, size: int, totalInvested: float, cash: float):
        super().__init__(contract, action, type, createTradeDate, closeTradeDate, pnl, priceCreateTrade, priceCloseTrade, size, totalInvested, cash)