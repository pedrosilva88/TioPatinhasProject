from datetime import date
from models.base_models import BracketOrder, Event
from typing import List
from backtest.models.base_models import BacktestResult

class ReportModule:
    results: List[BacktestResult]

    def __init__(self) -> None:
        self.results = []

    def createStopLossResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, loss: float, cashAvailable: float):
        print("[%s] ❌ ❌ (%s) -> %.2f Size(%.2f) [%.2f]\n" % (event.datetime.date(), event.contract.symbol, loss, bracketOrder.parentOrder.size, cashAvailable))

    def createTakeProfitResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, profit: float, cashAvailable: float):
        print("[%s] ✅ ✅ (%s) -> %.2f Size(%.2f) high(%.2f) low(%.2f) [%.2f]\n" % (event.datetime.date(), event.contract.symbol, profit, bracketOrder.parentOrder.size, event.high, event.low, cashAvailable))

    def createLossResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, loss: float, cashAvailable: float):
        print("[%s] ❌ (%s) -> %.2f Size(%.2f) [%.2f]\n" % (event.datetime.date(), event.contract.symbol, loss, bracketOrder.parentOrder.size, cashAvailable))

    def createProfitResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, profit: float, cashAvailable: float):
        print("[%s] ✅ (%s) -> %.2f Size(%.2f) [%.2f]\n" % (event.datetime.date(), event.contract.symbol, profit, bracketOrder.parentOrder.size, cashAvailable))
