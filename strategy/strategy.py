from dataclasses import dataclass
from helpers import log
from strategy.configs.models import StrategyConfig
from strategy.models import StrategyData, StrategyResult, StrategyResultType
from models.base_models import BracketOrder, Order, OrderAction, OrderType

@dataclass
class Strategy:
    strategyData: StrategyData = None
    strategyConfig: StrategyConfig = None

    def run(self, strategyData: StrategyData, strategyConfig: StrategyConfig) -> StrategyResult:
        """
        Override This method
        """
        pass

    # Calculations
    
    def getOrderPrice(self, action: OrderAction):
        pass

    def calculatePnl(self, action: OrderAction):
        pass

    def getStopLossPrice(self, action: OrderAction):
        pass

    def getSize(self, action: OrderAction):
        pass

    # Create Order

    def createOrder(self, type: StrategyResultType):
        action = OrderAction.Buy if type == StrategyResultType.Buy else OrderAction.Sell
        price = self.getOrderPrice(action)
        profitTarget = self.calculatePnl(action)
        stopLossPrice = self.getStopLossPrice(action)
        size = self.getSize(action)

        mainOrderType = self.strategyConfig.orderType
        profitOrder = Order(action.reverse, mainOrderType, size, round(profitTarget, 2))
        stopLossOrder = Order(action.reverse, OrderType.StopOrder, size, round(stopLossPrice, 2))
        parentOrder = Order(action, OrderType.LimitOrder, size, round(price, 2))
        return BracketOrder(parentOrder, profitOrder, stopLossOrder)
