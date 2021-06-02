
from _typeshed import SupportsReadline
from datetime import date
from backtest.models.base_models import BacktestResultType
from backtest.models.zigzag.zigzag_models import BacktestZigZagResult
from backtest.reports.report_module import ReportModule
from models.base_models import Event, BracketOrder, Order
from models.zigzag.models import EventZigZag

class ReportZigZagModule(ReportModule):
    def createStopLossResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, loss: float, cashAvailable: float):
        super().createStopLossResult(event, bracketOrder, positionDate, loss, cashAvailable)

        event: EventZigZag = event
        mainOrder: Order = bracketOrder.parentOrder
        stopOrder: Order = bracketOrder.stopLossOrder

        self.createResult(type= BacktestResultType.stopLoss,
                            pnl= loss,
                            closePrice=stopOrder.price,
                            event= event,
                            mainOrder=mainOrder,
                            positionDate= positionDate,
                            cashAvailable= cashAvailable)


    def createTakeProfitResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, profit: float, cashAvailable: float):
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
                            cashAvailable= cashAvailable)

    def createLossResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, loss: float, cashAvailable: float):
        super().createLossResult(event, bracketOrder, positionDate, loss, cashAvailable)

        event: EventZigZag = event
        mainOrder: Order = bracketOrder.parentOrder
        self.createResult(type= BacktestResultType.loss,
                            pnl= loss,
                            closePrice=event.lastPrice,
                            event= event,
                            mainOrder=mainOrder,
                            positionDate= positionDate,
                            cashAvailable= cashAvailable)

    def createProfitResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, profit: float, cashAvailable: float):
        super().createProfitResult(event, bracketOrder, positionDate, profit, cashAvailable)

        event: EventZigZag = event
        mainOrder: Order = bracketOrder.parentOrder
        self.createResult(type= BacktestResultType.profit,
                            pnl= profit,
                            closePrice=event.lastPrice,
                            event= event,
                            mainOrder=mainOrder,
                            positionDate= positionDate,
                            cashAvailable= cashAvailable)

    def createResult(self, type: BacktestResultType, pnl: float, closePrice: float, event: EventZigZag, mainOrder: Order, positionDate: date, cashAvailable: float):
        result = BacktestZigZagResult(contract=event.contract.symbol, 
                                        action=mainOrder.action.code,
                                        type= type,
                                        createTradeDate=positionDate,
                                        closeTradeDate=event.datetime.date(),
                                        pnl= pnl,
                                        priceCreateTrade=mainOrder.price,
                                        priceCloseTrade=closePrice,
                                        size=mainOrder.size,
                                        cash=cashAvailable)
        self.results.append(result)