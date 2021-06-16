from datetime import date, datetime
from pytz import timezone
from models.base_models import BracketOrder, Contract, Event, Position
from models.zigzag.models import EventZigZag
from typing import List
from database.model import FillDB
from strategy.models import StrategyData, StrategyResult, StrategyResultType

class StrategyZigZagData(StrategyData):
    timezone: timezone
    previousEvents: List[EventZigZag]
    fill: FillDB

    def __init__(self, contract: Contract, 
                        totalCash: float, 
                        event: EventZigZag, 
                        previousEvents: List[EventZigZag],  
                        position: Position = None, 
                        fill: FillDB = None,
                        today: date = None,
                        now: datetime = None,
                        timezone: timezone = timezone('UTC')):
        super().__init__(contract, totalCash, event, position=position, today=today, now=now)
        self.previousEvents = previousEvents
        self.fill = fill
        self.timezone = timezone
        
class StrategyZigZagResult(StrategyResult):
    priority: int

    def __init__(self, contract: Contract, event: EventZigZag, type: StrategyResultType, priority: int = None, 
                order: BracketOrder = None, position: Position = None):
        super().__init__(contract, event, type, order, position)
        self.priority = priority