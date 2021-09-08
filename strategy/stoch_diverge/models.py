from datetime import date, datetime
from pytz import timezone
from models.base_models import BracketOrder, Contract, Position
from models.stoch_diverge.models import EventStochDiverge
from typing import List
from database.model import FillDB
from strategy.models import StrategyData, StrategyResult, StrategyResultType

class StrategyStochDivergeData(StrategyData):
    previousEvents: List[EventStochDiverge]

    def __init__(self, contract: Contract, 
                        totalCash: float, 
                        event: EventStochDiverge, 
                        previousEvents: List[EventStochDiverge],  
                        today: date = None,
                        now: datetime = None):
        super().__init__(contract, totalCash, event, position=None, today=today, now=now)
        self.previousEvents = previousEvents
        
class StrategyStochDivergeResult(StrategyResult):
    targetPrice: float
    targetPercentage: float
    candlesToHold: int

    def __init__(self, contract: Contract, event: EventStochDiverge, type: StrategyResultType,
                targetPrice: float = None, targetPercentage: float = None,
                candlesToHold: int = None,
                order: BracketOrder = None, position: Position = None):
        super().__init__(contract, event, type, order, position)
        self.targetPrice = targetPrice
        self.targetPercentage = targetPercentage
        self.candlesToHold = candlesToHold