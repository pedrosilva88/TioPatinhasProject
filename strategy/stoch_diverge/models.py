from datetime import date, datetime
from pytz import timezone
from models.base_models import BracketOrder, Contract, Position
from models.stoch_diverge.models import EventStochDiverge
from typing import List
from database.model import FillDB
from strategy.models import StrategyData, StrategyResult, StrategyResultType

class StrategyStochDivergeData(StrategyData):
    timezone: timezone
    previousEvents: List[EventStochDiverge]
    fill: FillDB

    def __init__(self, contract: Contract, 
                        totalCash: float, 
                        event: EventStochDiverge, 
                        previousEvents: List[EventStochDiverge],  
                        position: Position = None, 
                        fill: FillDB = None,
                        today: date = None,
                        now: datetime = None,
                        timezone: timezone = timezone('UTC')):
        super().__init__(contract, totalCash, event, position=position, today=today, now=now)
        self.previousEvents = previousEvents
        self.fill = fill
        self.timezone = timezone
        
class StrategyStochDivergeResult(StrategyResult):
    priority: int

    def __init__(self, contract: Contract, event: EventStochDiverge, type: StrategyResultType, priority: int = None, 
                order: BracketOrder = None, position: Position = None):
        super().__init__(contract, event, type, order, position)
        self.priority = priority