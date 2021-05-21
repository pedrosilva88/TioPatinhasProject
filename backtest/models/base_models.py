from datetime import datetime
from enum import Enum
from models.base_models import Contract, OrderAction

class BacktestItem:
    pass

class BacktestResultType(Enum):
    takeProfit = 1
    profit = 2
    stopLoss = 3
    loss = 4

    @property
    def emoji(self):
        if self == BacktestResultType.takeProfit:
            return "✅ ✅"
        elif self == BacktestResultType.profit:
            return "✅"
        elif self == BacktestResultType.stopLoss:
            return "❌ ❌"
        elif self == BacktestResultType.loss:
            return "❌"

class BacktestResult:
    createTradeDate: datetime
    closeTradeDate: datetime
    contract: Contract
    pnl: float

    action: OrderAction
    type: BacktestResultType

    createTradePrice: float
    closeTradePrice: float

    size: int
    totalInvested: float

    cash: float

    def __init__(self, contract: Contract, 
                action: OrderAction, type: BacktestResultType,
                createTradeDate: datetime, closeTradeDate: datetime, 
                pnl: float, priceCreateTrade: float, priceCloseTrade: float, size: int,
                cash: float):
        self.contract = contract
        self.createTradeDate = createTradeDate
        self.closeTradeDate = closeTradeDate

        self.pnl = pnl
        self.action = action
        self.type = type

        self.priceCreateTrade = priceCreateTrade
        self.priceCloseTrade = priceCloseTrade

        self.size = size
        self.cash = cash

class BacktestDownloadModel:
    path: str
    numberOfDays: int
    barSize: str

    def __init__(self, path: str, numberOfDays: int, barSize: str):
        self.path = path
        self.numberOfDays = numberOfDays
        self.barSize = barSize

class BacktestAction(Enum):
    downloadData = 1
    showGraph = 2
    runStockPerformance = 3
    runStrategy = 4

class BacktestStrategy(Enum):
    zigzag = 'zigzag'
    opg = 'opg'
    macd = 'macd'

def getBacktestStrategyFromCode(code: str) -> BacktestStrategy:
    if code == 'zigzag':
        return BacktestStrategy.zigzag
    elif code == 'opg':
        return BacktestStrategy.opg
    elif code == 'macd':
        return BacktestStrategy.macd