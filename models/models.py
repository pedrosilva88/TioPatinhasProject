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

    def __init__(self, action: OrderAction, type: OrderType, totalQuantity: int, price: float, orderId = 0, takeProfitOrder = None, stopLossOrder = None, **kwargs):
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