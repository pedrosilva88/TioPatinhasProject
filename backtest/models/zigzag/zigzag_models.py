from datetime import date, datetime
from models.base_models import Contract, OrderAction
from backtest.models.base_models import BacktestResult, BacktestResultType

class BacktestZigZagResult(BacktestResult):
    zigzagDate: date
    
    def __init__(self, contract: Contract, action: OrderAction, type: BacktestResultType, createTradeDate: datetime, closeTradeDate: datetime, 
                        pnl: float, priceCreateTrade: float, priceCloseTrade: float, size: int, cash: float,
                        zigzagDate: date):
        super().__init__(contract, action, type, createTradeDate, closeTradeDate, pnl, priceCreateTrade, priceCloseTrade, size, cash)
        self.zigzagDate = zigzagDate