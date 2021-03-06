from enum import Enum
from datetime import datetime
from ib_insync import IB, Contract as ibContract, Order as ibOrder, LimitOrder as ibLimitOrder, MarketOrder as ibMarketOrder, StopOrder as ibStopOrder

class OrderAction(Enum):
    Buy = "BUY"
    Sell = "SELL"

    @property
    def reverse(self):
        return OrderAction.Sell if self == OrderAction.Buy else OrderAction.Buy

class OrderType(Enum):
    LimitOrder = "LMT"
    MarketOrder = "MKT"
    StopOrder = "STP"

class Order(ibOrder):
    takeProfitOrder = None
    stopLossOrder = None

    def __init__(self, action: OrderAction, type: OrderType, totalQuantity: int, price: float, takeProfitOrder = None, stopLossOrder = None, **kwargs):
        ibOrder.__init__(self, orderType=type, action=action,
                                totalQuantity=totalQuantity, 
                                lmtPrice=round(price, 2), **kwargs)
        
        if isinstance(takeProfitOrder, Order):
            self.takeProfitOrder = ibLimitOrder(takeProfitOrder.action, 
                                                takeProfitOrder.totalQuantity, 
                                                round(takeProfitOrder.lmtPrice, 2))

        if isinstance(stopLossOrder, Order):
            self.stopLossOrder = ibStopOrder(stopLossOrder.action, 
                                            stopLossOrder.totalQuantity, 
                                            round(stopLossOrder.lmtPrice, 2))