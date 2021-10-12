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

    @property
    def emoji(self):
        if self == StrategyBounceResultType.criteria1:
            return "⭐️"
        elif self == StrategyBounceResultType.criteria2:
            return "⭐️⭐️"
        elif self == StrategyBounceResultType.criteria3:
            return "⭐️⭐️⭐️"
        else:
            return "-"


class StrategyImpulsePullbackResult(StrategyResult):
    resultType: StrategyBounceResultType

    def __init__(self, contract: Contract, event: EventBounce, type: StrategyResultType,
                resultType: StrategyBounceResultType = StrategyBounceResultType.none,
                order: BracketOrder = None, position: Position = None):
        super().__init__(contract, event, type, order, position)
        self.resultType = resultType