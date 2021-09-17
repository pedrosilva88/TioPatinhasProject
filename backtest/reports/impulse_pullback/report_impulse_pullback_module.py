from typing import Any, List
from backtest.models.base_models import BacktestResult
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
