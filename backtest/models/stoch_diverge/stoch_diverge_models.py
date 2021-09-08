from datetime import date, datetime
from models.base_models import Contract, OrderAction
from backtest.models.base_models import BacktestResult, BacktestResultType

class BacktestStochDivergeResult(BacktestResult):
    candlesToHold: int
    profitTarget: float
    stopLossTarget: float
    
    def __init__(self, contract: Contract, action: OrderAction, type: BacktestResultType, createTradeDate: datetime, closeTradeDate: datetime, 
                        pnl: float, priceCreateTrade: float, priceCloseTrade: float, size: int, totalInvested: float, cash: float,
                        candlesToHold: int, profitTarget: float, stopLossTarget: float):
        super().__init__(contract, action, type, createTradeDate, closeTradeDate, pnl, priceCreateTrade, priceCloseTrade, size, totalInvested, cash)
        self.candlesToHold = candlesToHold
        self.profitTarget = profitTarget
        self.stopLossTarget = stopLossTarget