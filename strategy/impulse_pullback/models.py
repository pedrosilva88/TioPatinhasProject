from models.impulse_pullback.models import EventImpulsePullback
from typing import List
from enum import Enum
from strategy.models import StrategyData, StrategyResult, StrategyResultType
from models.base_models import BracketOrder, Contract, Position
from datetime import date, datetime

class StrategyImpulsePullbackData(StrategyData):
    previousEvents: List[EventImpulsePullback]

    def __init__(self, contract: Contract, 
                        totalCash: float, 
                        event: EventImpulsePullback, 
                        previousEvents: List[EventImpulsePullback],  
                        today: date = None,
                        now: datetime = None):
        super().__init__(contract, totalCash, event, position=None, today=today, now=now)
        self.previousEvents = previousEvents

class StrategyImpulsePullbackResultType(Enum):
    none = 0
    criteria1 = 1
    criteria2 = 2
    criteria3 = 3

    @property
    def emoji(self):
        if self == StrategyImpulsePullbackResultType.criteria1:
            return "⭐️"
        elif self == StrategyImpulsePullbackResultType.criteria2:
            return "⭐️⭐️"
        elif self == StrategyImpulsePullbackResultType.criteria3:
            return "⭐️⭐️⭐️"
        else:
            return "-"


class StrategyImpulsePullbackResult(StrategyResult):
    ipType: StrategyImpulsePullbackResultType
    swingCandleDate: datetime

    def __init__(self, contract: Contract, event: EventImpulsePullback, type: StrategyResultType,
                ipType: StrategyImpulsePullbackResultType = StrategyImpulsePullbackResultType.none,
                order: BracketOrder = None, position: Position = None):
        super().__init__(contract, event, type, order, position)
        self.ipType = ipType