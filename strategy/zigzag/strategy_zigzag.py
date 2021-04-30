from datetime import *
from helpers import log, utcToLocal, round_down
from strategy import Strategy, StrategyData, StrategyResult, StrategyResultType, StrategyConfig
from models import Order, OrderAction, OrderType, CustomBarData
from country_config import CountryConfig
from ib_insync import Fill

class StrategyZigZag(Strategy):
    # Properties

    strategyData: StrategyData = None
    strategyConfig: StrategyConfig = None
    countryConfig: CountryConfig = None  

    currentBar: CustomBarData = None
    previousBars: [CustomBarData] = None
    fill: Fill = None

    # Strategy Parameters
    profitPercentage: float = None
    willingToLose: float = None
    stopToLosePercentage: float = None
    maxToInvestPerStockPercentage: None

    minRSI: float = None
    maxRSI: float = None

    def run(self, strategyData: StrategyData, strategyConfig: StrategyConfig, countryConfig: CountryConfig):
        self.strategyData = strategyData
        self.strategyConfig = strategyConfig
        self.countryConfig = countryConfig
        self.fetchInformation()

        result = self.validateStrategy()
        if result:
            return result

        log("😁 %s 😁" % (self.strategyData.ticker.contract.symbol))
        log("😁 [%s] Bar[-6]-> RSI(%.2f) ZigZag(%s) 😁" % (self.previousBars[-6].date, self.previousBars[-6].rsi, self.previousBars[-6].zigzag))
        log("😁 [%s] Bar[-5]-> RSI(%.2f) ZigZag(%s) 😁" % (self.previousBars[-5].date, self.previousBars[-5].rsi, self.previousBars[-5].zigzag))
        log("😁 [%s] Bar[-4]-> RSI(%.2f) ZigZag(%s) 😁" % (self.previousBars[-4].date, self.previousBars[-4].rsi, self.previousBars[-4].zigzag))
        log("😁 [%s] Bar[-3]-> RSI(%.2f) ZigZag(%s) 😁" % (self.previousBars[-3].date, self.previousBars[-3].rsi, self.previousBars[-3].zigzag))
        log("😁 [%s] Bar[-2]-> RSI(%.2f) ZigZag(%s) 😁" % (self.previousBars[-2].date, self.previousBars[-2].rsi, self.previousBars[-2].zigzag))
        log("😁 [%s] Bar[-1]-> RSI(%.2f) ZigZag(%s) 😁" % (self.previousBars[-1].date, self.previousBars[-1].rsi, self.previousBars[-1].zigzag))
        log("😁 [%s] CurrentBar-> RSI(%.2f) ZigZag(%s) 😁" % (self.currentBar.date, self.currentBar.rsi, self.currentBar.zigzag))
        log("😁  😁")

        zigzagBar, zigzagIndex = self.getZigZag()
        if (zigzagBar is not None):
            if (self.currentBar.rsi > self.minRSI or self.currentBar.rsi <= self.maxRSI):
                if (zigzagBar.rsi <= self.minRSI and self.isLonging(zigzagIndex)):
                    type = StrategyResultType.Buy
                    order = self.createOrder(type)
                    return StrategyResult(strategyData.ticker, type, order)
                elif (zigzagBar.rsi >= self.maxRSI and self.isShorting(zigzagIndex)):
                    type = StrategyResultType.Sell
                    order = self.createOrder(type)
                    return StrategyResult(strategyData.ticker, type, order)
                return StrategyResult(strategyData.ticker, StrategyResultType.DoNothing, None)   
            else:
                return StrategyResult(strategyData.ticker, StrategyResultType.DoNothing, None)   
        else:
            return StrategyResult(strategyData.ticker, StrategyResultType.DoNothing, None)

    def getZigZag(self) -> (CustomBarData, int):
        totalBars = len(self.previousBars)
        index = -1 
        zigzagBar = None
        for bar in reversed(self.previousBars):
            if (bar.zigzag == True and (bar.rsi <= self.minRSI or bar.rsi >= self.maxRSI)):
                log("🎃 Bar Found %s: %d 🎃" % (self.strategyData.ticker.contract.symbol, index))
                zigzagBar = bar
                break
            index -= 1
        return (zigzagBar, index)

    def isShorting(self, startIndex: int):
        index = startIndex + 1
        while (index < -1):
            if self.previousBars[index].high < self.previousBars[index-1].high:
                log("👻 Not Shorting %.2f < %.2f 👻" % (self.previousBars[index].high, self.previousBars[index-1].high))
                return False
            index += 1 
        return True

    def isLonging(self, startIndex: int):
        index = startIndex + 1
        while (index < -1):
            if self.previousBars[index].low > self.previousBars[index-1].low:
                log("👻 Not Longing %.2f > %.2f 👻" % (self.previousBars[index].low, self.previousBars[index-1].low))
                return False
            index += 1
        return True


    # Constructor

    def fetchInformation(self):
        # Ticker Data
        self.currentBar = self.strategyData.currentBar
        self.previousBars = self.strategyData.previousBars

        # Strategy Parameters
        self.willingToLose = self.strategyConfig.willingToLose
        self.stopToLosePercentage = self.strategyConfig.stopToLosePercentage
        self.profitPercentage = self.strategyConfig.profitPercentage
        self.maxToInvestPerStockPercentage = self.strategyConfig.maxToInvestPerStockPercentage

        self.minRSI = self.strategyConfig.minRSI
        self.maxRSI = self.strategyConfig.maxRSI
    
    # Validations

    def validateStrategy(self):
        if self.strategyData.fill:
            return self.handleFill()

        elif (not self.isConfigsValid() or not self.isStrategyDataValid()):
            log("🙅‍♂️ Invalid data for %s: isConfigsValid(%s) isStrategyDataValid(%s) 🙅‍♂️" % (self.strategyData.ticker.contract.symbol, self.isConfigsValid(), self.isStrategyDataValid()))
            return StrategyResult(self.strategyData.ticker, StrategyResultType.IgnoreEvent)

        return None

    def isStrategyDataValid(self):
        return ((self.currentBar is not None) and (self.currentBar.zigzag is not None) and (self.currentBar.rsi is not None) and
                (self.currentBar.open is not None) and (self.currentBar.close is not None) and

                (self.previousBars[-1] is not None) and (self.previousBars[-1].zigzag is not None) and (self.previousBars[-1].rsi is not None) and
                (self.previousBars[-1].open is not None) and (self.previousBars[-1].close is not None) and

                (self.previousBars[-2] is not None) and (self.previousBars[-2].zigzag is not None) and (self.previousBars[-2].rsi is not None) and
                (self.previousBars[-2].open is not None) and (self.previousBars[-2].close is not None) and

                (self.previousBars[-3] is not None) and (self.previousBars[-3].zigzag is not None) and (self.previousBars[-3].rsi is not None) and
                (self.previousBars[-3].open is not None) and (self.previousBars[-3].close is not None))


    def isConfigsValid(self):
        return (self.profitPercentage > 0 and
                self.willingToLose > 0 and
                self.stopToLosePercentage > 0 and
                self.maxToInvestPerStockPercentage > 0)

    def isTimeForThisStartegyExpired(self):
        datetime = self.datetime.replace(microsecond=0).time()
        maxTime = self.strategyMaxTime.replace(microsecond=0).time()
        return datetime > maxTime

    def shouldGetStockEarnings(self):
        return False
    
    # Handlers

    def handleFill(self):
        executionDate = self.strategyData.fill.execution.time
        shares = self.strategyData.position.position

        if date.today() >= (executionDate+timedelta(days=2)).date():
            if shares > 0:
                return StrategyResult(self.strategyData.ticker, StrategyResultType.PositionExpired_Sell, None, self.strategyData.position)    
            elif shares < 0:
                return StrategyResult(self.strategyData.ticker, StrategyResultType.PositionExpired_Buy, None, self.strategyData.position)

        return StrategyResult(self.strategyData.ticker, StrategyResultType.KeepPosition)

    # Calculations
    def getOrderPrice(self, action: OrderAction):
        return (self.currentBar.high+self.currentBar.low)/2  #self.currentBar.low if action == OrderAction.Buy else self.currentBar.high

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
        action = OrderAction.Buy if type == StrategyResultType.Buy else OrderAction.Sell
        price = self.getOrderPrice(action)
        profitTarget = self.calculatePnl(action)
        stopLossPrice = self.getStopLossPrice(action)
        size = self.getSize(action)
        # minTickProfit = self.priceIncrement(profitTarget)
        # minTickLoss = self.priceIncrement(stopLossPrice)

        #print("\t⭐️ [Create] Type(%s) Size(%i) Price(%.2f) ProfitPrice(%.2f) StopLoss(%.2f) ⭐️" % (action, size, price, profitTarget, stopLossPrice))
        log("\t⭐️ [Create] Type(%s) Size(%i) Price(%.2f) ProfitPrice(%.2f) StopLoss(%.2f) ⭐️" % (action, size, price, profitTarget, stopLossPrice))

        profitOrder = Order(action.reverse, OrderType.LimitOrder, size, round(profitTarget, 2))
        stopLossOrder = Order(action.reverse, OrderType.StopOrder, size, round(stopLossPrice, 2))
        return Order(action=action, type=OrderType.MarketOrder, totalQuantity=size, price=price, takeProfitOrder=profitOrder, stopLossOrder=stopLossOrder)
