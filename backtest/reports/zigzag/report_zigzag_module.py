
from datetime import date
from backtest.models.base_models import BacktestResultType
from backtest.models.zigzag.zigzag_models import BacktestZigZagResult
from backtest.reports.report_module import ReportModule
from models.base_models import Event, BracketOrder, Order
from models.zigzag.models import EventZigZag

class ReportZigZagModule(ReportModule):
    def createStopLossResult(self, event: Event, bracketOrder: BracketOrder, positionDate: date, loss: float, cashAvailable: float,
                                zigzagDate: date):
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
        super().createLossResult(event, bracketOrder, positionDate, loss, cashAvailable)

        event: EventZigZag = event
        mainOrder: Order = bracketOrder.parentOrder
        self.createResult(type= BacktestResultType.loss,
                            pnl= loss,
                            closePrice=event.lastPrice,
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
                            closePrice=event.lastPrice,
                            event= event,
                            mainOrder=mainOrder,
                            positionDate= positionDate,
                            cashAvailable= cashAvailable,
                            zigzagDate= zigzagDate)

    def createResult(self, type: BacktestResultType, pnl: float, closePrice: float, event: EventZigZag, mainOrder: Order, positionDate: date, cashAvailable: float,
                                zigzagDate: date):
        result = BacktestZigZagResult(contract=event.contract.symbol, 
                                        action=mainOrder.action.code,
                                        type= type,
                                        createTradeDate=positionDate,
                                        closeTradeDate=event.datetime.date(),
                                        pnl= pnl,
                                        priceCreateTrade=mainOrder.price,
                                        priceCloseTrade=closePrice,
                                        size=mainOrder.size,
                                        cash=cashAvailable,
                                        zigzagDate=zigzagDate)
        self.results.append(result)