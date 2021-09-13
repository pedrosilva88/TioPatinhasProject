from datetime import date
from models.base_models import BracketOrder, Event, Order, OrderAction
from models.stoch_diverge.models import EventStochDiverge
from backtest.models.stoch_diverge.stoch_diverge_models import BacktestStochDivergeResult
from backtest.models.base_models import BacktestResult, BacktestResultType
from typing import Any, List
from backtest.reports.report_module import ReportModule, StrategyResultModel

class StrategyStochDivergeResultModel(StrategyResultModel):
    willingToLose: float
    winLossTarget: float
    minTakeProfit: float
    takeProfitSafeMargin: float

    def __init__(self, numberOfTrades: int, pnl: float, totalReturn: float, battingAverage: float, winLossRatio: float, 
                averageReturnPerTrade: float, standardDeviation: float, sharpRatio: float,
                willingToLose: float, winLossTarget: float, minTakeProfit: float, takeProfitSafeMargin: float) -> None:
        super().__init__(numberOfTrades, pnl, totalReturn, battingAverage, winLossRatio, averageReturnPerTrade, standardDeviation, sharpRatio)
        self.willingToLose = willingToLose
        self.winLossTarget= winLossTarget
        self.minTakeProfit = minTakeProfit 
        self.takeProfitSafeMargin = takeProfitSafeMargin

class ReportStochDivergeModule(ReportModule):
    def getHeaderRowForTradesReport(self) -> List[str]:
        return["Date", "Order Date", "Symbol", "Result", "PnL", 
                "Price CreateTrade", "Price CloseTrade", "Size", 
                "Total Invested", "Action", "Cash", 
                "Candles To Hold", "TP Target", "SL Target"]
                
    def getRowForTradesReport(self, item: BacktestResult) -> List[Any]:
        item: BacktestStochDivergeResult = item 
        return[item.closeTradeDate, item.createTradeDate, item.contract.symbol, item.type.emoji, 
                item.pnl, item.priceCreateTrade, item.priceCloseTrade, item.size, item.totalInvested, item.action.code, item.cash,
                item.candlesToHold, item.profitTarget, item.stopLossTarget]

    def getHeaderRowForStrategyReport(self) -> List[str]:
        return["PnL", "Total Return", "Batting Average", "Win/Loss Ratio", 
                "Avg. return Per Trade", "Stand Deviation", "Sharp Ratio", "Number Of Trades","Willing To Lose", 
                "WinLoss Target", "Min TakeProfit", "TakeProfit Margin"]

    def getRowForStrategyReport(self, item: StrategyResultModel) -> List[Any]:
        item: StrategyStochDivergeResultModel = item
        return [item.pnl, item.totalReturn, item.battingAverage, item.winLossRatio,
                item.averageReturnPerTrade, item.standardDeviation, item.sharpRatio, item.numberOfTrades, 
                item.willingToLose, item.winLossTarget, item.minTakeProfit, item.takeProfitSafeMargin]

    
    def createStopLossResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, loss: float, cashAvailable: float,
                            candlesToHold: int):
        super().createStopLossResult(event, bracketOrder, positionDate, -loss, cashAvailable)

        event: EventStochDiverge = event
        mainOrder: Order = bracketOrder.parentOrder
        stopOrder: Order = bracketOrder.stopLossOrder

        self.createResult(type= BacktestResultType.stopLoss,
                            pnl= -loss,
                            closePrice=stopOrder.price,
                            event= event,
                            mainOrder=mainOrder,
                            positionDate= positionDate,
                            cashAvailable= cashAvailable,
                            candlesToHold= candlesToHold,
                            profitPrice=bracketOrder.takeProfitOrder.price,
                            stopLossPrice=bracketOrder.stopLossOrder.price)

    def createTakeProfitResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, profit: float, cashAvailable: float,
                                candlesToHold: int):
        super().createTakeProfitResult(event, bracketOrder, positionDate, profit, cashAvailable)

        event: EventStochDiverge = event
        mainOrder: Order = bracketOrder.parentOrder
        profitOrder: Order = bracketOrder.takeProfitOrder

        self.createResult(type= BacktestResultType.takeProfit,
                            pnl= profit,
                            closePrice=profitOrder.price,
                            event= event,
                            mainOrder=mainOrder,
                            positionDate= positionDate,
                            cashAvailable= cashAvailable,
                            candlesToHold= candlesToHold,
                            profitPrice=bracketOrder.takeProfitOrder.price,
                            stopLossPrice=bracketOrder.stopLossOrder.price)

    def createLossResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, loss: float, cashAvailable: float,
                                candlesToHold: int):
        super().createLossResult(event, bracketOrder, positionDate, -loss, cashAvailable)

        event: EventStochDiverge = event
        mainOrder: Order = bracketOrder.parentOrder
        self.createResult(type= BacktestResultType.loss,
                            pnl= -loss,
                            closePrice=event.close,
                            event= event,
                            mainOrder=mainOrder,
                            positionDate= positionDate,
                            cashAvailable= cashAvailable,
                            candlesToHold= candlesToHold,
                            profitPrice=bracketOrder.takeProfitOrder.price,
                            stopLossPrice=bracketOrder.stopLossOrder.price)

    def createProfitResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, profit: float, cashAvailable: float,
                                candlesToHold: int):
        super().createProfitResult(event, bracketOrder, positionDate, profit, cashAvailable)

        event: EventStochDiverge = event
        mainOrder: Order = bracketOrder.parentOrder
        self.createResult(type= BacktestResultType.profit,
                            pnl= profit,
                            closePrice=event.close,
                            event= event,
                            mainOrder=mainOrder,
                            positionDate= positionDate,
                            cashAvailable= cashAvailable,
                            candlesToHold= candlesToHold,
                            profitPrice=bracketOrder.takeProfitOrder.price,
                            stopLossPrice=bracketOrder.stopLossOrder.price)

    def createResult(self, type: BacktestResultType, pnl: float, closePrice: float, event: EventStochDiverge, mainOrder: Order, positionDate: date, cashAvailable: float,
                                candlesToHold: int, profitPrice: float, stopLossPrice: float):
        gapPrice = profitPrice/mainOrder.price if mainOrder.action == OrderAction.Sell else mainOrder.price/profitPrice
        profitTarget = abs(1-gapPrice)
        gapPrice = stopLossPrice/mainOrder.price if mainOrder.action == OrderAction.Buy else mainOrder.price/stopLossPrice
        stopLossTarget = abs(1-gapPrice)
        result = BacktestStochDivergeResult(contract=event.contract, 
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
                                        candlesToHold=candlesToHold,
                                        profitTarget=round(profitTarget, 3),
                                        stopLossTarget=round(stopLossTarget, 3))
        self.results.append(result)


    def createStrategyResult(self, dynamicParameters: List[List[float]]) -> StrategyResultModel:
        result: StrategyResultModel = super().createStrategyResult(dynamicParameters)
        item = StrategyStochDivergeResultModel(result.numberOfTrades,
                                        round(result.pnl, 4), 
                                        round(result.totalReturn, 4), 
                                        round(result.battingAverage, 4), 
                                        round(result.winLossRatio, 4),
                                        round(result.averageReturnPerTrade, 4), 
                                        round(result.standardDeviation, 4), 
                                        round(result.sharpRatio, 4), 
                                        dynamicParameters[0], dynamicParameters[1], dynamicParameters[2], 
                                        dynamicParameters[3])
        self.strategyResults.append(item)
        return item

    