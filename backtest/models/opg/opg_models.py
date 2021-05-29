from datetime import datetime
from backtest.models.base_models import BacktestResult, BacktestResultType
from models.base_models import Contract, OrderAction
from models.opg.models import EventOPG
from models.zigzag.models import EventZigZag

# class BacktestOPGItem(BacktestItem):
#     event: EventOPG

#     def __init__(self, contract: Contract, 
#                         datetime: datetime, 
#                         open: float,
#                         close: float,
#                         high: float,
#                         low: float,
#                         volume: float) -> None:
#         self.event = EventOPG(contract= contract, datetime=datetime, 
#                                 open=open, close=close, high=high, low=low, volume=volume)

class BacktestOPGResult(BacktestResult):
    openPrice: float
    yesterdayClosePrice: float
    averageVolume: float
    volumeFirstMinute: float

    def __init__(self, contract: Contract, 
                action: OrderAction, type: BacktestResultType,
                createTradeDate: datetime, closeTradeDate: datetime, 
                pnl: float, priceCreateTrade: float, priceCloseTrade: float, size: int,
                cash: float,
                averageVolume: float, volumeFirstMinute: float, totalInvested: float,
                openPrice: float, ystdClosePrice: float):
        BacktestResult.__init__(self, contract= contract, action= action, type= type, 
                                createTradeDate= createTradeDate, closeTradeDate= closeTradeDate,
                                pnl= pnl, priceCreateTrade= priceCreateTrade, priceCloseTrade= priceCreateTrade, size= size, 
                                cash= cash)

        self.averageVolume =  averageVolume
        self.volumeFirstMinute =  volumeFirstMinute
        self.openPrice = openPrice
        self.yesterdayClosePrice = ystdClosePrice