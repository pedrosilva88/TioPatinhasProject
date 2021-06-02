from models.base_models import BracketOrder, Contract, Event, Position
from models.zigzag.models import EventZigZag
from typing import List
from database.model import FillDB
from strategy.models import StrategyData, StrategyResult, StrategyResultType

class StrategyZigZagData(StrategyData):
    previousEvents: List[EventZigZag]
    fill: FillDB

    def __init__(self, contract: Contract, 
                        totalCash: float, 
                        event: EventZigZag, 
                        previousEvents: List[EventZigZag],  
                        position: Position = None, fill: FillDB = None):
        super().__init__(contract, totalCash, event, position=position)
        self.previousEvents = previousEvents
        self.fill = fill
        

class StrategyZigZagResult(StrategyResult):
    priority: int

    def __init__(self, contract: Contract, event: EventZigZag, type: StrategyResultType, priority: int = None, 
                order: BracketOrder = None, position: Position = None):
        super().__init__(contract, event, type, order, position)
        self.priority = priority