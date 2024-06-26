from models.bounce.models import EventBounce
from typing import List
from enum import Enum
from strategy.models import StrategyData, StrategyResult, StrategyResultType
from models.base_models import BracketOrder, Contract, Position
from datetime import date, datetime

class StrategyBounceData(StrategyData):
    previousEvents: List[EventBounce]

    def __init__(self, contract: Contract, 
                        totalCash: float, 
                        event: EventBounce, 
                        previousEvents: List[EventBounce],  
                        today: date = None,
                        now: datetime = None):
        super().__init__(contract, totalCash, event, position=None, today=today, now=now)
        self.previousEvents = previousEvents

class StrategyBounceResultType(Enum):
    none = 0
    criteria1 = 1
    criteria2 = 2

    @property
    def emoji(self):
        if self == StrategyBounceResultType.criteria1:
            return "⭐️⭐️"
        elif self == StrategyBounceResultType.criteria2:
            return "⭐️⭐️⭐️"
        else:
            return "-"

class ReversalCandletType(Enum):
    SingleCandleReversal = 0
    Original2CandleReversal = 1
    InsideBar2CandleReversal = 2
    TradeThroughCandleReversal = 3

    @property
    def code(self) -> str:
        if self == ReversalCandletType.SingleCandleReversal:
            return "Single_CR"
        elif self == ReversalCandletType.Original2CandleReversal:
            return "Original_2CR"
        elif self == ReversalCandletType.InsideBar2CandleReversal:
            return "InsideBar_2CR"
        elif self == ReversalCandletType.TradeThroughCandleReversal:
            return "TradeThrough_2CR"

class StrategyBounceResult(StrategyResult):
    resultType: StrategyBounceResultType
    reversalCandle: EventBounce
    confirmationCandle: EventBounce
    ema: int
    reversalCandleType: ReversalCandletType

    def __init__(self, contract: Contract, event: EventBounce, type: StrategyResultType,
                resultType: StrategyBounceResultType = StrategyBounceResultType.none,
                reversalCandle: EventBounce = None,
                confirmationCandle: EventBounce = None,
                reversalCandleType: ReversalCandletType = None,
                ema: int = None,
                order: BracketOrder = None, position: Position = None):
        super().__init__(contract, event, type, order, position)
        self.resultType = resultType
        self.reversalCandle = reversalCandle
        self.confirmationCandle = confirmationCandle
        self.reversalCandleType = reversalCandleType
        self.ema = ema