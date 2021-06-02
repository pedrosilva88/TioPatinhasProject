from strategy.zigzag.models import StrategyZigZagData, StrategyZigZagResult
from typing import List, Tuple
from ib_insync import Fill
from helpers import log
from strategy import Strategy
from strategy.models import StrategyData, StrategyResult, StrategyResultType
from strategy.configs.zigzag.models import StrategyZigZagConfig
from models.base_models import Order, OrderAction, OrderType
from models.zigzag.models import EventZigZag

class StrategyZigZag(Strategy):
    # Properties

    strategyData: StrategyZigZagData = None
    strategyConfig: StrategyZigZagConfig = None

    currentBar: EventZigZag = None
    previousBars: List[EventZigZag] = None
    fill: Fill = None

    # Strategy Parameters
    profitPercentage: float = None
    willingToLose: float = None
    stopToLosePercentage: float = None
    maxToInvestPerStockPercentage: None

    minRSI: float = None
    maxRSI: float = None

    def run(self, strategyData: StrategyZigZagData, strategyConfig: StrategyZigZagConfig):
        self.strategyData = strategyData
        self.strategyConfig = strategyConfig
        self.fetchInformation()

        result = self.validateStrategy()
        if result:
            return result

        log("😁 %s 😁" % (self.strategyData.contract.symbol))
        log("😁 [%s] Bar[-4]-> RSI(%.2f) ZigZag(%s) 😁" % (self.previousBars[-4].datetime.date(), self.previousBars[-4].rsi, self.previousBars[-4].zigzag))
        log("😁 [%s] Bar[-3]-> RSI(%.2f) ZigZag(%s) 😁" % (self.previousBars[-3].datetime.date(), self.previousBars[-3].rsi, self.previousBars[-3].zigzag))
        log("😁 [%s] Bar[-2]-> RSI(%.2f) ZigZag(%s) 😁" % (self.previousBars[-2].datetime.date(), self.previousBars[-2].rsi, self.previousBars[-2].zigzag))
        log("😁 [%s] Bar[-1]-> RSI(%.2f) ZigZag(%s) 😁" % (self.previousBars[-1].datetime.date(), self.previousBars[-1].rsi, self.previousBars[-1].zigzag))
        log("😁 [%s] CurrentBar-> RSI(%.2f) ZigZag(%s) 😁" % (self.currentBar.datetime.date(), self.currentBar.rsi, self.currentBar.zigzag))
        log("😁  😁")

        zigzagBar, zigzagIndex = self.getZigZag()
        if (zigzagBar is not None):
            if (self.currentBar.rsi >= self.minRSI or self.currentBar.rsi <= self.maxRSI):
                if (zigzagBar.rsi <= self.minRSI and self.isLonging(zigzagIndex)):
                    type = StrategyResultType.Buy
                    order = self.createOrder(type)
                    return StrategyZigZagResult(strategyData.contract, self.currentBar, type, zigzagIndex, order, None)
                elif (zigzagBar.rsi >= self.maxRSI and self.isShorting(zigzagIndex)):
                    type = StrategyResultType.Sell
                    order = self.createOrder(type)
                    return StrategyZigZagResult(strategyData.contract, self.currentBar, type, zigzagIndex, order, None)
                return StrategyZigZagResult(strategyData.contract, self.currentBar, StrategyResultType.DoNothing, None)   
            else:
                return StrategyZigZagResult(strategyData.contract, self.currentBar, StrategyResultType.DoNothing, None)   
        else:
            return StrategyZigZagResult(strategyData.contract, self.currentBar, StrategyResultType.DoNothing, None)

    def getZigZag(self) -> Tuple[EventZigZag, int]:
        totalBars = len(self.previousBars)
        index = -1 
        zigzagBar = None
        for bar in reversed(self.previousBars):
            if (bar.zigzag == True and (bar.rsi <= self.minRSI or bar.rsi >= self.maxRSI) and index < -1):
                log("🎃 Bar Found %s: %d 🎃" % (self.strategyData.ticker.contract.symbol, index))
                zigzagBar = bar
                break
            index -= 1
        return (zigzagBar, index)

    def isShorting(self, startIndex: int):
        index = startIndex + 1
        while (index <= 0):
            if index == 0:
                if (self.previousBars[index-1].high < self.currentBar.high):
                    log("👻 (%.2f) Not Shorting %.2f < %.2f 👻" % (index, self.previousBars[index-1].high, self.currentBar.high))
                    return False
                else:
                    log("👻 😁 (%.2f) Shorting %.2f > %.2f 😁 👻" % (index, self.previousBars[index-1].high, self.currentBar.high))
            elif (self.previousBars[index-1].high < self.previousBars[index].high):
                log("👻  (%.2f) Not Shorting %.2f < %.2f 👻" % (index, self.previousBars[index-1].high, self.previousBars[index].high))
                return False
            else:
                log("👻 😁 (%.2f) Shorting %.2f > %.2f 😁 👻" % (index, self.previousBars[index-1].high, self.previousBars[index].high))
            index += 1 
        return True

    def isLonging(self, startIndex: int):
        index = startIndex + 1
        while (index <= 0):
            if index == 0:
                if (self.previousBars[index-1].low > self.currentBar.low):
                    log("👻  (%.2f) Not Longing %.2f > %.2f 👻" % (index, self.previousBars[index-1].low, self.currentBar.low))
                    return False
                else:
                    log("👻 😁 (%.2f) Longing %.2f < %.2f 😁 👻" % (index, self.previousBars[index-1].low, self.currentBar.low))
            elif (self.previousBars[index-1].low > self.previousBars[index].low):
                log("👻 (%.2f) Not Longing %.2f > %.2f 👻" % (index, self.previousBars[index-1].low, self.previousBars[index].low))
                return False
            else:
                log("👻 😁 (%.2f) Longing %.2f < %.2f 😁 👻" % (index, self.previousBars[index-1].low, self.previousBars[index].low))
            index += 1
        return True


    # Constructor

    def fetchInformation(self):
        # Ticker Data
        self.currentBar = self.strategyData.event
        self.previousBars = self.strategyData.previousEvents

        # Strategy Parameters
        self.willingToLose = self.strategyConfig.willingToLose
        self.stopToLosePercentage = self.strategyConfig.stopToLosePercentage
        self.profitPercentage = self.strategyConfig.profitPercentage
        self.maxToInvestPerStockPercentage = self.strategyConfig.maxToInvestPerStockPercentage

        self.minRSI = self.strategyConfig.minRSI
        self.maxRSI = self.strategyConfig.maxRSI
    
    # Validations

    def validateStrategy(self):
        handleFillResult = None
        if self.strategyData.fill:
            handleFillResult = self.handleFill()

        if handleFillResult is None:
            if (not self.isConfigsValid() or not self.isStrategyDataValid()):
                return StrategyZigZagResult(self.strategyData.contract, self.currentBar, StrategyResultType.IgnoreEvent)
            else: 
                return None
        else:
            return handleFillResult

    def isStrategyDataValid(self):
        return ((self.currentBar is not None) and (self.currentBar.zigzag is not None) and (self.currentBar.rsi is not None) and
                (self.currentBar.open is not None) and (self.currentBar.close is not None) and

                (self.previousBars[-1] is not None) and (self.previousBars[-1].zigzag is not None) and (self.previousBars[-1].rsi is not None) and
                (self.previousBars[-1].open is not None) and (self.previousBars[-1].close is not None) and

                (self.previousBars[-2] is not None) and (self.previousBars[-2].zigzag is not None) and (self.previousBars[-2].rsi is not None) and
                (self.previousBars[-2].open is not None) and (self.previousBars[-2].close is not None) and

                (self.previousBars[-3] is not None) and (self.previousBars[-3].zigzag is not None) and (self.previousBars[-3].rsi is not None) and
                (self.previousBars[-3].open is not None) and (self.previousBars[-3].close is not None) and

                (self.previousBars[-4] is not None) and (self.previousBars[-4].zigzag is not None) and (self.previousBars[-4].rsi is not None) and
                (self.previousBars[-4].open is not None) and (self.previousBars[-4].close is not None))


    def isConfigsValid(self):
        return (self.profitPercentage > 0 and
                self.willingToLose > 0 and
                self.stopToLosePercentage > 0 and
                self.maxToInvestPerStockPercentage > 0)
    
    # Handlers

    def handleFill(self):
        today = self.strategyData.today # date.today() #date(2021, 5, 21)
        now = self.strategyData.now #datetime.now() #datetime(2021,5,21,17,30) 

        executionDate = self.strategyData.fill.date
        dateLimit = today-timedelta(days=6)

        if (self.strategyData.position is None and
            dateLimit <= executionDate):
            log("🥵 Cant do nothing with Stock (%s) - You had a Fill for this stock in the last 6 days 🥵" % self.strategyData.ticker.contract.symbol)
            return StrategyResult(self.strategyData.ticker, StrategyResultType.DoNothing)

        elif self.strategyData.position is not None:
            shares = self.strategyData.position.position
            closeMarketDate = self.countryConfig.closeMarket.astimezone(timezone('UTC'))
            if (now.hour == (closeMarketDate-timedelta(hours=2)).hour and today >= (executionDate+timedelta(days=0))):
                if shares > 0:
                    return StrategyResult(self.strategyData.ticker, StrategyResultType.PositionExpired_Sell, None, self.strategyData.position)    
                elif shares < 0:
                    return StrategyResult(self.strategyData.ticker, StrategyResultType.PositionExpired_Buy, None, self.strategyData.position)
            log("🥵 Cant do nothing with Stock (%s) - You already have a position and it's not expired 🥵" % self.strategyData.ticker.contract.symbol)
            return StrategyResult(self.strategyData.ticker, StrategyResultType.KeepPosition)

        return None

    # Calculations
    def getOrderPrice(self, action: OrderAction):
        return self.currentBar.lastPrice #(self.currentBar.high+self.currentBar.low)/2  #self.currentBar.low if action == OrderAction.Buy else self.currentBar.high

    def calculatePnl(self, action: OrderAction):
        price = self.getOrderPrice(action)
        if action == OrderAction.Buy:
            return price + price * self.profitPercentage
        elif action == OrderAction.Sell:
            return price - price * self.profitPercentage

    def getStopLossPrice(self, action: OrderAction):
        price = self.getOrderPrice(action)
        totalCash = self.strategyData.totalCash
        stopLossPriceRatio = price*self.stopToLosePercentage

        return price - stopLossPriceRatio if action == OrderAction.Buy else price + stopLossPriceRatio

    def getSize(self, action: OrderAction):
        price = self.getOrderPrice(action)
        totalCash = self.strategyData.totalCash
        portfolioLoss = totalCash * self.willingToLose
        stopLossPriceRatio = price*self.stopToLosePercentage

        return int(min(portfolioLoss/stopLossPriceRatio, (totalCash*self.maxToInvestPerStockPercentage)/price))

    # Final Operations

    def createOrder(self, type: StrategyResultType):
        log("🎃 OrderPrice used for %s: %.2f 🎃" % (self.strategyData.ticker.contract.symbol, self.currentBar.lastPrice))
        action = OrderAction.Buy if type == StrategyResultType.Buy else OrderAction.Sell
        price = self.getOrderPrice(action)
        profitTarget = self.calculatePnl(action)
        stopLossPrice = self.getStopLossPrice(action)
        size = self.getSize(action)
        # minTickProfit = self.priceIncrement(profitTarget)
        # minTickLoss = self.priceIncrement(stopLossPrice)

        log("\t⭐️ [Create] Type(%s) Size(%i) Price(%.2f) ProfitPrice(%.2f) StopLoss(%.2f) ⭐️" % (action, size, price, profitTarget, stopLossPrice))

        profitOrder = Order(action.reverse, OrderType.LimitOrder, size, round(profitTarget, 2))
        stopLossOrder = Order(action.reverse, OrderType.StopOrder, size, round(stopLossPrice, 2))
        return Order(action=action, type=OrderType.MarketOrder, totalQuantity=size, price=price, takeProfitOrder=profitOrder, stopLossOrder=stopLossOrder)
