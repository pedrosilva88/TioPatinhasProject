import csv, statistics, math
from scanner.scanner import Scanner
from backtest.scanner.scanner_manager import BacktestScannerManager, reportContractsPerformanceFilename, reportTradesPerformanceFilename, reportTradesFilename
from datetime import date
from models.base_models import BracketOrder, Event
from typing import Any, List, Union
from backtest.models.base_models import BacktestAction, BacktestResult, BacktestResultType, ContractSymbol
from backtest.configs.models import BacktestConfigs

class StrategyResultModel:
    numberOfTrades: int
    pnl: float
    totalReturn: float
    battingAverage: float
    winLossRatio: float
    averageReturnPerTrade: float
    standardDeviation: float
    sharpRatio: float

    def __init__(self, numberOfTrades: int, pnl: float, totalReturn: float, battingAverage: float, winLossRatio: float, averageReturnPerTrade: float,
                standardDeviation: float, sharpRatio: float) -> None:
        self.numberOfTrades = numberOfTrades
        self.pnl = pnl
        self.totalReturn = totalReturn
        self.battingAverage = battingAverage
        self.winLossRatio = winLossRatio
        self.averageReturnPerTrade = averageReturnPerTrade
        self.standardDeviation = standardDeviation
        self.sharpRatio = sharpRatio
        

class ReportModule:
    results: List[BacktestResult]
    strategyResults: List[StrategyResultModel]

    def __init__(self) -> None:
        self.results = []
        self.strategyResults = []

    def getHeaderRowForTradesReport(self) -> List[str]:
        pass

    def getRowForTradesReport(self, item: BacktestResult) -> List[Any]:
        pass

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
        self.saveReportPerformance(contractsPerformance)
    
    def createReportTrades(self, isForPerformance: bool):
        self.saveReportTrades(isForPerformance)

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
        return contractsPerformance

    def saveReportTrades(self, isForPerformance: bool):
        config = BacktestConfigs()
        filename = reportTradesPerformanceFilename if isForPerformance else reportTradesFilename
        tradesFilename = BacktestScannerManager.getPathFileToSaveReports(config.provider, config.country, config.strategyType, filename)
        with open(tradesFilename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.getHeaderRowForTradesReport())
            for result in self.results:
                writer.writerow(self.getRowForTradesReport(result))

    def saveReportPerformance(self, contractsPerformance: Union[ContractSymbol, List[int]]):
        config = BacktestConfigs()
        contracts = Scanner.contratcsFrom(config.downloadModel.path)
        performanceFilename = BacktestScannerManager.getPathFileToSaveReports(config.provider, config.country, config.strategyType, reportContractsPerformanceFilename)
        with open(performanceFilename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Symbol", "Exchange", "Currency", "Trades Found", "Take Profit", "Profit", "StopLoss", "Loss", "Wins", "%"])
            for key, item in contractsPerformance.items():
                total = item[0]+item[1]+item[2]+item[3]
                wins = item[0]+item[1]
                writer.writerow([key,
                                "SMART",
                                config.country.currency,
                                total,
                                item[0], item[1], item[2], item[3],
                                wins,
                                round((wins/total)*100, 2)])
                item = list(filter(lambda x : x.symbol == key, contracts)).pop()
                contracts.remove(item)
            for item in contracts:
                writer.writerow([item.symbol,
                                "SMART",
                                config.country.currency,
                                0,
                                0,0,0,0,
                                0,
                                0])

    def createStrategyResult(self, dynamicParameters: List[List[float]]) -> StrategyResultModel:
        pnl = 0
        totalReturn = 0
        battingAverageCount = 0
        totalPositivePercentage = 0
        totalNegativePercentage = 0
        positiveResultsCount = 0
        negativeResultsCount = 0
        standardDeviationData = []
        for result in self.results:
            pnl += result.pnl
            percentage = abs(result.priceCreateTrade-result.priceCloseTrade)/result.priceCreateTrade

            if result.type == BacktestResultType.profit or result.type == BacktestResultType.takeProfit:
                totalReturn += percentage
                battingAverageCount +=1
                positiveResultsCount +=1
                totalPositivePercentage += percentage
                standardDeviationData.append(percentage)
            else:
                totalReturn -= percentage
                negativeResultsCount +=1
                totalNegativePercentage += percentage
                standardDeviationData.append(-percentage)
        battingaAverage = battingAverageCount/len(self.results)
        winLossRatio = (totalPositivePercentage/positiveResultsCount) / (totalNegativePercentage/negativeResultsCount)
        averageReturnPerTrade = totalReturn/len(self.results)
        standardDeviation = statistics.stdev(standardDeviationData)
        sharpRatio = (averageReturnPerTrade/standardDeviation)*math.sqrt(365)
        return StrategyResultModel(len(self.results), pnl, totalReturn, battingaAverage, winLossRatio, averageReturnPerTrade, standardDeviation, sharpRatio)

    def saveStrategyResultsReport(self, isForPerformance: bool):
        config = BacktestConfigs()
        filename = reportTradesPerformanceFilename if isForPerformance else reportTradesFilename
        tradesFilename = BacktestScannerManager.getPathFileToSaveReports(config.provider, config.country, config.strategyType, filename)
        with open(tradesFilename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.getHeaderRowForTradesReport())
            for result in self.results:
                writer.writerow(self.getRowForTradesReport(result))