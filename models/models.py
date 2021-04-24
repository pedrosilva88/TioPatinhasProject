from enum import Enum
from datetime import datetime
from ib_insync import IB, Contract as ibContract, Order as ibOrder, LimitOrder as ibLimitOrder, MarketOrder as ibMarketOrder, StopOrder as ibStopOrder, RealTimeBarList, ContractDetails, PriceIncrement, BarData

class StockInfo:
    symbol: str
    lastExecution: datetime
    averageVolume: float
    volumeFirstMinute: float
    realTimeBarList: RealTimeBarList
    contractDetails: ContractDetails
    priceRules: [PriceIncrement]

    def __init__(self, symbol: str, lastExecution: datetime = None, 
                        averageVolume: float = None, volumeFirstMinute: float = None, 
                        realTimeBarList: RealTimeBarList = None, contractDetails: ContractDetails = None, 
                        priceRules: [PriceIncrement] = None):
        self.symbol = symbol
        self.lastExecution = lastExecution
        self.averageVolume = averageVolume
        self.volumeFirstMinute = volumeFirstMinute
        self.realTimeBarList = realTimeBarList
        self.contractDetails = contractDetails
        self.priceRules = priceRules

class OrderAction(Enum):
    Buy = "BUY"
    Sell = "SELL"

    @property
    def reverse(self):
        return OrderAction.Sell if self == OrderAction.Buy else OrderAction.Buy

    @property
    def code(self):
        return "Long" if self == OrderAction.Buy else "Short"

class OrderType(Enum):
    LimitOrder = "LMT"
    MarketOrder = "MKT"
    StopOrder = "STP"

class Order(ibOrder):
    takeProfitOrder = None
    stopLossOrder = None

    def __init__(self, action: OrderAction, type: OrderType, totalQuantity: int, price: float = None, orderId = 0, takeProfitOrder = None, stopLossOrder = None, **kwargs):
        ibOrder.__init__(self, orderId=orderId, 
                                orderType=type, action=action, 
                                totalQuantity=totalQuantity, 
                                lmtPrice=round(price, 2), **kwargs)
        

        parentId = orderId
        if isinstance(takeProfitOrder, Order):
            self.takeProfitOrder = ibLimitOrder(action=takeProfitOrder.action, 
                                                totalQuantity=takeProfitOrder.totalQuantity, 
                                                lmtPrice=round(takeProfitOrder.lmtPrice, 2),
                                                parentId=parentId,
                                                orderId=takeProfitOrder.orderId)
        if isinstance(stopLossOrder, Order):

            self.stopLossOrder = ibStopOrder(action=stopLossOrder.action, 
                                            totalQuantity=stopLossOrder.totalQuantity, 
                                            stopPrice=round(stopLossOrder.lmtPrice, 2),
                                            parentId=parentId,
                                            orderId=stopLossOrder.orderId)

class CustomBarData(BarData):
    zigzag: bool
    rsi: float

    def __init__(self, barData: BarData, zigzag: bool, rsi: float):
        BarData.__init__(self)
        self.date = barData.date
        self.open = barData.open
        self.close = barData.close
        self.high = barData.high
        self.low = barData.low

        self.volume = barData.volume
        self.average = barData.average
        self.barCount = barData.barCount

        self.zigzag = zigzag
        self.rsi = rsi
        