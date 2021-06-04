
from datetime import date
from typing import Any, List
from backtest.models.base_models import BacktestResult, BacktestResultType
from backtest.models.zigzag.zigzag_models import BacktestZigZagResult
from backtest.reports.report_module import ReportModule, StrategyResultModel
from models.base_models import Event, BracketOrder, Order
from models.zigzag.models import EventZigZag

class StrategyZigzagResultModel(StrategyResultModel):
    profitPercentage: float
    losePercentage: float
    daysToHold: float
    zigzagSpread: float

    def __init__(self, pnl: float, totalReturn: float, battingAverage: float, winLossRatio: float, 
                averageReturnPerTrade: float, standardDeviation: float, sharpRatio: float,
                profitPercentage: float, losePercentage: float, daysToHold: float, zigzagSpread: float) -> None:
        super().__init__(pnl, totalReturn, battingAverage, winLossRatio, averageReturnPerTrade, standardDeviation, sharpRatio)
        self.profitPercentage = profitPercentage
        self.losePercentage = losePercentage
        self.daysToHold = daysToHold
        self.zigzagSpread = zigzagSpread

class ReportZigZagModule(ReportModule):
    def getHeaderRowForTradesReport(self) -> List[str]:
        return["Date", "Order Date", "Symbol", "Result", "Action", "PnL", 
                "Price CreateTrade", "Price CloseTrade", "Size", "Zigzag Date", 
                "Total Invested", "Cash"]

    def getRowForTradesReport(self, item: BacktestResult) -> List[Any]:
        item: BacktestZigZagResult = item 
        return[item.closeTradeDate, item.createTradeDate, item.contract.symbol, item.type.emoji, item.action.code, 
                item.pnl, item.priceCreateTrade, item.priceCloseTrade, item.size, item.zigzagDate, item.totalInvested, item.cash]

    def createStopLossResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, loss: float, cashAvailable: float,
                                zigzagDate: date):
        super().createStopLossResult(event, bracketOrder, positionDate, -loss, cashAvailable)

        event: EventZigZag = event
        mainOrder: Order = bracketOrder.parentOrder
        stopOrder: Order = bracketOrder.stopLossOrder

        self.createResult(type= BacktestResultType.stopLoss,
                            pnl= -loss,
                            closePrice=stopOrder.price,
                            event= event,
                            mainOrder=mainOrder,
                            positionDate= positionDate,
                            cashAvailable= cashAvailable,
                            zigzagDate= zigzagDate)

    def createTakeProfitResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, profit: float, cashAvailable: float,
                                zigzagDate: date):
        super().createTakeProfitResult(event, bracketOrder, positionDate, profit, cashAvailable)

        event: EventZigZag = event
        mainOrder: Order = bracketOrder.parentOrder
        profitOrder: Order = bracketOrder.takeProfitOrder

        self.createResult(type= BacktestResultType.takeProfit,
                            pnl= profit,
                            closePrice=profitOrder.price,
                            event= event,
                            mainOrder=mainOrder,
                            positionDate= positionDate,
                            cashAvailable= cashAvailable,
                            zigzagDate= zigzagDate)

    def createLossResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, loss: float, cashAvailable: float,
                                zigzagDate: date):
        super().createLossResult(event, bracketOrder, positionDate, -loss, cashAvailable)

        event: EventZigZag = event
        mainOrder: Order = bracketOrder.parentOrder
        self.createResult(type= BacktestResultType.loss,
                            pnl= -loss,
                            closePrice=event.close,
                            event= event,
                            mainOrder=mainOrder,
                            positionDate= positionDate,
                            cashAvailable= cashAvailable,
                            zigzagDate= zigzagDate)

    def createProfitResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, profit: float, cashAvailable: float,
                                zigzagDate: date):
        super().createProfitResult(event, bracketOrder, positionDate, profit, cashAvailable)

        event: EventZigZag = event
        mainOrder: Order = bracketOrder.parentOrder
        self.createResult(type= BacktestResultType.profit,
                            pnl= profit,
                            closePrice=event.close,
                            event= event,
                            mainOrder=mainOrder,
                            positionDate= positionDate,
                            cashAvailable= cashAvailable,
                            zigzagDate= zigzagDate)

    def createResult(self, type: BacktestResultType, pnl: float, closePrice: float, event: EventZigZag, mainOrder: Order, positionDate: date, cashAvailable: float,
                                zigzagDate: date):
        result = BacktestZigZagResult(contract=event.contract, 
                                        action=mainOrder.action,
                                        type= type,
                                        createTradeDate=positionDate,
                                        closeTradeDate=event.datetime.date(),
                                        pnl= round(pnl, 2),
                                        priceCreateTrade=round(mainOrder.price, 2),
                                        priceCloseTrade=round(closePrice, 2),
                                        size=mainOrder.size,
                                        totalInvested=round(mainOrder.size*mainOrder.price, 2),
                                        cash=round(cashAvailable, 2),
                                        zigzagDate=zigzagDate)
        self.results.append(result)

    def createStrategyResult(self, dynamicParameters: List[List[float]]) -> StrategyResultModel:
        result: StrategyResultModel = super().createStrategyResult()
        item = StrategyZigzagResultModel(result.numberOfTrades ,result.pnl, result.totalReturn, result.battingAverage, result.winLossRatio,
                                        result.averageReturnPerTrade, result.standardDeviation, result.sharpRatio, 
                                        dynamicParameters[0], dynamicParameters[1], dynamicParameters[3], dynamicParameters[2])
        self.strategyResults.append(item)
        return item