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

        # if (self.currentBar.date.year == 2021 and self.currentBar.date.month == 1 or
        #     self.currentBar.date.year == 2020 and self.currentBar.date.month == 13) :
        log("😁 %s -> High[-1](%.2f) High[-2](%.2f) RSI[-3](%.2f) ZigZag[-3](%s) 😁" % (self.strategyData.ticker.contract.symbol, self.previousBars[-1].high, self.previousBars[-2].high, self.previousBars[-3].rsi, self.previousBars[-3].zigzag))
        if (self.previousBars[-3].zigzag == True and (self.previousBars[-3].rsi <= self.minRSI or self.previousBars[-3].rsi >= self.maxRSI) and
            self.previousBars[-2].zigzag == False and self.previousBars[-1].zigzag == False):
            if (self.currentBar.rsi > self.minRSI or self.currentBar.rsi <= self.maxRSI):
                if (self.previousBars[-3].rsi <= self.minRSI and
                    self.previousBars[-2].low < self.previousBars[-1].low):
                    type = StrategyResultType.Buy
                    order = self.createOrder(type)
                    return StrategyResult(strategyData.ticker, type, order)
                elif (self.previousBars[-3].rsi >= self.maxRSI and
                      self.previousBars[-2].high > self.previousBars[-1].high):
                    
                    # if (self.currentBar.date.year == 2021 and self.currentBar.date.month == 1 or
                    #     self.currentBar.date.year == 2020 and self.currentBar.date.month == 13):
                    #     print(self.previousBars[-1].high, self.previousBars[-2].high, self.previousBars[-3].zigzag)

                    type = StrategyResultType.Sell
                    order = self.createOrder(type)
                    return StrategyResult(strategyData.ticker, type, order)
                return StrategyResult(strategyData.ticker, StrategyResultType.DoNothing, None)   
            else:
                return StrategyResult(strategyData.ticker, StrategyResultType.DoNothing, None)   
        else:
            return StrategyResult(strategyData.ticker, StrategyResultType.DoNothing, None)

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
