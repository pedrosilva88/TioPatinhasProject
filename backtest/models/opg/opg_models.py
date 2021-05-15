from datetime import datetime
from backtest.models.base_models import BacktestItem, BacktestResult, BacktestResultType
from models.base_models import Contract, OrderAction
from models.opg.models import EventOPG
from models.zigzag.models import EventZigZag

class BacktestZigZagItem(BacktestItem):
    event: EventOPG

    def __init__(self, contract: Contract, 
                        datetime: datetime, 
                        open: float,
                        close: float,
                        high: float,
                        low: float,
                        volume: float) -> None:
        self.event = EventOPG(contract= contract, datetime=datetime, 
                                open=open, close=close, high=high, low=low, volume=volume)

    # TODO: Não sei pa que preciso disto    
    # def ticker(self, countryConfig):
    #     formatDate = "%Y-%m-%d %H:%M:%S"
    #     stock = Stock(self.symbol, "SMART", countryConfig.currency)
    #     customDate = self.dateString
    #     if ":00+" in self.dateString:
    #         customDate = self.dateString.split(":00+")[0]+":00"
    #     elif ":00-" in self.dateString:
    #         customDate = self.dateString.split(":00-")[0]+":00"

    #     newTime = utcToLocal(datetime.strptime(customDate, formatDate), countryConfig.timezone)
    #     return Ticker(contract=stock, 
    #                         time=newTime, 
    #                         close=self.close, 
    #                         open=self.openPrice,
    #                         bid=self.bid, 
    #                         ask=self.ask, 
    #                         last=self.last,
    #                         volume=self.volume)

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