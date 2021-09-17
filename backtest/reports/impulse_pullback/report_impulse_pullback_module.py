from datetime import date
from strategy.impulse_pullback.models import StrategyImpulsePullbackResultResultType
from models.impulse_pullback.models import EventImpulsePullback
from models.base_models import BracketOrder, Event, Order, OrderAction
from typing import Any, List
from backtest.models.base_models import BacktestResult, BacktestResultType
from backtest.models.impulse_pullback.impulse_pullback_models import BacktestImpulsePullbackResult
from backtest.reports.report_module import ReportModule, StrategyResultModel


class StrategyImpulsePullbackResultModel(StrategyResultModel):

    def __init__(self, numberOfTrades: int, pnl: float, totalReturn: float, battingAverage: float, winLossRatio: float, 
                averageReturnPerTrade: float, standardDeviation: float, sharpRatio: float) -> None:
        super().__init__(numberOfTrades, pnl, totalReturn, battingAverage, winLossRatio, averageReturnPerTrade, standardDeviation, sharpRatio)

class ReportImpulsePullbackModule(ReportModule):
    def getHeaderRowForTradesReport(self) -> List[str]:
        return["Date", "Order Date", "Symbol", "Result", "Criteria", "PnL", 
                "Price CreateTrade", "Price CloseTrade", "Size", 
                "Total Invested", "Action", "Cash"]
                
    def getRowForTradesReport(self, item: BacktestResult) -> List[Any]:
        item: BacktestImpulsePullbackResult = item 
        return[item.closeTradeDate, item.createTradeDate, item.contract.symbol, item.type.emoji, item.criteria, 
                item.pnl, item.priceCreateTrade, item.priceCloseTrade, item.size, item.totalInvested, item.action.code, item.cash]

    def getHeaderRowForStrategyReport(self) -> List[str]:
        return["PnL", "Total Return", "Batting Average", "Win/Loss Ratio", 
                "Avg. return Per Trade", "Stand Deviation", "Sharp Ratio", "Number Of Trades"]

    def getRowForStrategyReport(self, item: StrategyResultModel) -> List[Any]:
        item: StrategyImpulsePullbackResultModel = item
        return [item.pnl, item.totalReturn, item.battingAverage, item.winLossRatio,
                item.averageReturnPerTrade, item.standardDeviation, item.sharpRatio, item.numberOfTrades]
    
    def createStopLossResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, loss: float, cashAvailable: float,
                            criteria: StrategyImpulsePullbackResultResultType):
        super().createStopLossResult(event, bracketOrder, positionDate, -loss, cashAvailable)

        event: EventImpulsePullback = event
        mainOrder: Order = bracketOrder.parentOrder
        stopOrder: Order = bracketOrder.stopLossOrder

        self.createResult(type= BacktestResultType.stopLoss,
                            pnl= -loss,
                            closePrice=stopOrder.price,
                            event= event,
                            mainOrder=mainOrder,
                            positionDate= positionDate,
                            cashAvailable= cashAvailable,
                            criteria= criteria)

    def createTakeProfitResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, profit: float, cashAvailable: float,
                                criteria: StrategyImpulsePullbackResultResultType):
        super().createTakeProfitResult(event, bracketOrder, positionDate, profit, cashAvailable)

        event: EventImpulsePullback = event
        mainOrder: Order = bracketOrder.parentOrder
        profitOrder: Order = bracketOrder.takeProfitOrder

        self.createResult(type= BacktestResultType.takeProfit,
                            pnl= profit,
                            closePrice=profitOrder.price,
                            event= event,
                            mainOrder=mainOrder,
                            positionDate= positionDate,
                            cashAvailable= cashAvailable,
                            criteria= criteria)

    def createLossResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, loss: float, cashAvailable: float,
                                criteria: StrategyImpulsePullbackResultResultType):
        super().createLossResult(event, bracketOrder, positionDate, -loss, cashAvailable)

        event: EventImpulsePullback = event
        mainOrder: Order = bracketOrder.parentOrder
        self.createResult(type= BacktestResultType.loss,
                            pnl= -loss,
                            closePrice=event.close,
                            event= event,
                            mainOrder=mainOrder,
                            positionDate= positionDate,
                            cashAvailable= cashAvailable,
                            criteria= criteria)

    def createProfitResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, profit: float, cashAvailable: float,
                                criteria: StrategyImpulsePullbackResultResultType):
        super().createProfitResult(event, bracketOrder, positionDate, profit, cashAvailable)

        event: EventImpulsePullback = event
        mainOrder: Order = bracketOrder.parentOrder
        self.createResult(type= BacktestResultType.profit,
                            pnl= profit,
                            closePrice=event.close,
                            event= event,
                            mainOrder=mainOrder,
                            positionDate= positionDate,
                            cashAvailable= cashAvailable,
                            criteria=criteria)

    def createResult(self, type: BacktestResultType, pnl: float, closePrice: float, event: EventImpulsePullback, mainOrder: Order, positionDate: date, cashAvailable: float,
                    criteria: StrategyImpulsePullbackResultResultType):
        result = BacktestImpulsePullbackResult(contract=event.contract, 
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
                                        criteria= criteria.emoji)
        self.results.append(result)


    def createStrategyResult(self, dynamicParameters: List[List[float]]) -> StrategyResultModel:
        result: StrategyResultModel = super().createStrategyResult(dynamicParameters)
        item = StrategyImpulsePullbackResultModel(result.numberOfTrades,
                                        round(result.pnl, 4), 
                                        round(result.totalReturn, 4), 
                                        round(result.battingAverage, 4), 
                                        round(result.winLossRatio, 4),
                                        round(result.averageReturnPerTrade, 4), 
                                        round(result.standardDeviation, 4), 
                                        round(result.sharpRatio, 4))
        self.strategyResults.append(item)
        return item
