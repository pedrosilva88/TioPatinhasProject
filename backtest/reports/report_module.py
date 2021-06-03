from datetime import date
from strategy.configs.models import StrategyType
from models.base_models import BracketOrder, Event
from typing import List, Union
from backtest.models.base_models import BacktestAction, BacktestResult, BacktestResultType, ContractSymbol
from backtest.configs.models import BacktestConfigs

class ReportModule:
    results: List[BacktestResult]

    def __init__(self) -> None:
        self.results = []

    def createStopLossResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, loss: float, cashAvailable: float, *args):
        print("[%s] ❌ ❌ (%s) -> %.2f Size(%.2f) [%.2f]\n" % (event.datetime.date(), event.contract.symbol, loss, bracketOrder.parentOrder.size, cashAvailable))

    def createTakeProfitResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, profit: float, cashAvailable: float, *args):
        print("[%s] ✅ ✅ (%s) -> %.2f Size(%.2f) high(%.2f) low(%.2f) [%.2f]\n" % (event.datetime.date(), event.contract.symbol, profit, bracketOrder.parentOrder.size, event.high, event.low, cashAvailable))

    def createLossResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, loss: float, cashAvailable: float, *args):
        print("[%s] ❌ (%s) -> %.2f Size(%.2f) [%.2f]\n" % (event.datetime.date(), event.contract.symbol, loss, bracketOrder.parentOrder.size, cashAvailable))

    def createProfitResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, profit: float, cashAvailable: float, *args):
        print("[%s] ✅ (%s) -> %.2f Size(%.2f) [%.2f]\n" % (event.datetime.date(), event.contract.symbol, profit, bracketOrder.parentOrder.size, cashAvailable))

    def createReport(self):
        config = BacktestConfigs()
        if config.action == BacktestAction.runStrategy:
            pass
        elif config.action == BacktestAction.runStrategyPerformance:
            self.createReportPerformance()
            pass

    def createReportPerformance(self):
        contractsPerformance = self.createContractsPerformance()
        pass

    def createContractsPerformance(self) -> Union[ContractSymbol, List[int]]:
        contractsPerformance = dict()
        array = []
        for result in self.results:
            if result.contract.symbol in contractsPerformance:
                array = contractsPerformance[result.contract.symbol]
            else:
                array = [0,0,0,0]

            if result.type == BacktestResultType.takeProfit:
                array[0] += 1
            elif result.type == BacktestResultType.profit:
                array[1] += 1
            elif result.type == BacktestResultType.stopLoss:
                array[2] += 1
            elif result.type == BacktestResultType.loss:
                array[3] += 1

            contractsPerformance[result.contract.symbol] = array