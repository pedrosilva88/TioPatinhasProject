from datetime import datetime
from models.bounce.models import EventBounce
from strategy.bounce.models import StrategyBounceResultType
from models.base_models import Contract, OrderAction
from backtest.models.base_models import BacktestResult, BacktestResultType

class BacktestBounceResult(BacktestResult):
    confirmationCandle: EventBounce
    reversalCandle: EventBounce
    reversalType: str
    ema: int
    def __init__(self, contract: Contract, action: OrderAction, type: BacktestResultType, createTradeDate: datetime, closeTradeDate: datetime, 
                        pnl: float, priceCreateTrade: float, priceCloseTrade: float, size: int, totalInvested: float, cash: float, 
                        confirmationCandle: EventBounce, reversalCandle: EventBounce, reversalType: str, ema: int):
        super().__init__(contract, action, type, createTradeDate, closeTradeDate, pnl, priceCreateTrade, priceCloseTrade, size, totalInvested, cash)
        self.confirmationCandle = confirmationCandle
        self.reversalCandle = reversalCandle
        self.reversalType = reversalType
        self.ema = ema