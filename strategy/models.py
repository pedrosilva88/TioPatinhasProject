from enum import Enum
from datetime import date, datetime
from models.base_models import BracketOrder, Contract, Event, Position
from typing import List

class StrategyResultType(Enum):
    def __str__(self):
        if self.value == 0: return "Ignore Event"
        elif self.value == 1: return "Do nothing"
        elif self.value == 2: return "Buy Position"
        elif self.value == 3: return "Sell Position"
        elif self.value == 4: return "Time expired Sell Position"
        elif self.value == 5: return "Time expired Buy Position"
        elif self.value == 6: return "Keep Position"
        elif self.value == 7: return "Keep Order"
        elif self.value == 8: return "Invalid Time for this Strategy"
        elif self.value == 9: return "Invalid Time for this Strategy - Cancel Order"
        else: return "💀"

    IgnoreEvent = 0
    DoNothing = 1
    Buy = 2
    Sell = 3
    PositionExpired_Sell = 4
    PositionExpired_Buy = 5
    KeepPosition = 6
    KeepOrder = 7
    StrategyDateWindowExpired = 8
    StrategyDateWindowExpiredCancelOrder = 9
    CancelOrder = 10

class StrategyData:
    totalCash: float
    contract: Contract
    event: Event
    position: Position

    today: date
    now: datetime

    def __init__(self, contract: Contract,
                        totalCash: float,
                        event: Event,
                        position: Position = None,
                        today: date = date.today(),
                        now: datetime = datetime.now()):
        self.contract = contract
        self.position = position
        self.totalCash = totalCash
        self.event = event
        self.today = today
        self.now = now

class StrategyResult:
    contract: Contract
    event: Event
    type: StrategyResultType
    order: BracketOrder
    position: Position

    def __str__(self):
        return "Result for %s: %s %s size(%d) price(%.2f)\n" % (self.contract.symbol, 
                                                                self.event.datetime.date(), 
                                                                self.type.name, 
                                                                self.order.parentOrder.size,
                                                                self.order.parentOrder.price)

    def __init__(self, contract: Contract, event: Event, type: StrategyResultType, order: BracketOrder = None, position: Position = None):
        self.contract = contract
        self.event = event
        self.type = type
        self.order = order
        self.position = position
