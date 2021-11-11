from datetime import date
from strategy.bounce.models import StrategyBounceResultType
from models.bounce.models import EventBounce
from models.base_models import BracketOrder, Event, Order, OrderAction
from typing import Any, List
from backtest.models.base_models import BacktestResult, BacktestResultType
from backtest.models.bounce.bounce_models import BacktestBounceResult
from backtest.reports.report_module import ReportModule, StrategyResultModel

class StrategyBounceResultModel(StrategyResultModel):

    def __init__(self, numberOfTrades: int, pnl: float, totalReturn: float, battingAverage: float, winLossRatio: float, 
                averageReturnPerTrade: float, standardDeviation: float, sharpRatio: float) -> None:
        super().__init__(numberOfTrades, pnl, totalReturn, battingAverage, winLossRatio, averageReturnPerTrade, standardDeviation, sharpRatio)

class ReportBounceModule(ReportModule):
    def getHeaderRowForTradesReport(self) -> List[str]:
        return["Date", "Order Date", "Symbol", "Result", "PnL", 
                "Price CreateTrade", "Price CloseTrade", "Size", 
                "Total Invested", "Action", "Cash",
                "ConfirmationCandle", "ReversalCandle", "ReversalType", "EMA"]
                
    def getRowForTradesReport(self, item: BacktestResult) -> List[Any]:
        item: BacktestBounceResult = item 
        return[item.closeTradeDate, item.createTradeDate, item.contract.symbol, item.type.emoji, item.pnl, 
                item.priceCreateTrade, item.priceCloseTrade, item.size, 
                item.totalInvested, item.action.code, item.cash,
                item.confirmationCandle.datetime.date(), item.reversalCandle.datetime.date(), item.reversalType, item.ema]

    def getHeaderRowForStrategyReport(self) -> List[str]:
        return["PnL", "Total Return", "Batting Average", "Win/Loss Ratio", 
                "Avg. return Per Trade", "Stand Deviation", "Sharp Ratio", "Number Of Trades"]

    def getRowForStrategyReport(self, item: StrategyResultModel) -> List[Any]:
        item: StrategyBounceResultModel = item
        return [item.pnl, item.totalReturn, item.battingAverage, item.winLossRatio,
                item.averageReturnPerTrade, item.standardDeviation, item.sharpRatio, item.numberOfTrades]
    
    def createStopLossResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, loss: float, cashAvailable: float,
                            confirmationCandle: EventBounce, reversalCandle: EventBounce, reversalType: str, ema: int):
        super().createStopLossResult(event, bracketOrder, positionDate, -loss, cashAvailable)

        event: EventBounce = event
        mainOrder: Order = bracketOrder.parentOrder
        stopOrder: Order = bracketOrder.stopLossOrder

        self.createResult(type= BacktestResultType.stopLoss,
                            pnl= -loss,
                            closePrice=stopOrder.price,
                            event= event,
                            mainOrder=mainOrder,
                            positionDate= positionDate,
                            cashAvailable= cashAvailable,
                            confirmationCandle= confirmationCandle,
                            reversalCandle= reversalCandle,
                            reversalType= reversalType,
                            ema= ema)

    def createTakeProfitResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, profit: float, cashAvailable: float,
                                confirmationCandle: EventBounce, reversalCandle: EventBounce, reversalType: str, ema: int):
        super().createTakeProfitResult(event, bracketOrder, positionDate, profit, cashAvailable)

        event: EventBounce = event
        mainOrder: Order = bracketOrder.parentOrder
        profitOrder: Order = bracketOrder.takeProfitOrder

        self.createResult(type= BacktestResultType.takeProfit,
                            pnl= profit,
                            closePrice=profitOrder.price,
                            event= event,
                            mainOrder=mainOrder,
                            positionDate= positionDate,
                            cashAvailable= cashAvailable,
                            confirmationCandle= confirmationCandle,
                            reversalCandle= reversalCandle,
                            reversalType= reversalType,
                            ema= ema)

    def createLossResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, loss: float, cashAvailable: float,
                                confirmationCandle: EventBounce, reversalCandle: EventBounce, reversalType: str, ema: int):
        super().createLossResult(event, bracketOrder, positionDate, -loss, cashAvailable)

        event: EventBounce = event
        mainOrder: Order = bracketOrder.parentOrder
        self.createResult(type= BacktestResultType.loss,
                            pnl= -loss,
                            closePrice=event.close,
                            event= event,
                            mainOrder=mainOrder,
                            positionDate= positionDate,
                            cashAvailable= cashAvailable,
                            confirmationCandle= confirmationCandle,
                            reversalCandle= reversalCandle,
                            reversalType= reversalType,
                            ema= ema)

    def createProfitResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, profit: float, cashAvailable: float,
                                confirmationCandle: EventBounce, reversalCandle: EventBounce, reversalType: str, ema: int):
        super().createProfitResult(event, bracketOrder, positionDate, profit, cashAvailable)

        event: EventBounce = event
        mainOrder: Order = bracketOrder.parentOrder
        self.createResult(type= BacktestResultType.profit,
                            pnl= profit,
                            closePrice=event.close,
                            event= event,
                            mainOrder=mainOrder,
                            positionDate= positionDate,
                            cashAvailable= cashAvailable,
                            confirmationCandle= confirmationCandle,
                            reversalCandle= reversalCandle,
                            reversalType= reversalType,
                            ema= ema)

    def createResult(self, type: BacktestResultType, pnl: float, closePrice: float, event: EventBounce, mainOrder: Order, positionDate: date, cashAvailable: float,
                    confirmationCandle: EventBounce, reversalCandle: EventBounce, reversalType: str, ema: int):
        result = BacktestBounceResult(contract=event.contract, 
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
                                        confirmationCandle= confirmationCandle,
                                        reversalCandle= reversalCandle,
                                        reversalType= reversalType,
                                        ema= ema)
        self.results.append(result)


    def createStrategyResult(self, dynamicParameters: List[List[float]]) -> StrategyResultModel:
        result: StrategyResultModel = super().createStrategyResult(dynamicParameters)
        item = StrategyBounceResultModel(result.numberOfTrades,
                                        round(result.pnl, 4), 
                                        round(result.totalReturn, 4), 
                                        round(result.battingAverage, 4), 
                                        round(result.winLossRatio, 4),
                                        round(result.averageReturnPerTrade, 4), 
                                        round(result.standardDeviation, 4), 
                                        round(result.sharpRatio, 4))
        self.strategyResults.append(item)
        return item