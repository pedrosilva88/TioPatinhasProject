from country_config import models
import csv, distutils, math
from database.model import FillDB
from datetime import date, timedelta
from strategy.zigzag.models import StrategyZigZagData, StrategyZigZagResult
from strategy.models import StrategyData, StrategyResult, StrategyResultType
from typing import Any, List, Tuple, Union
from country_config.market_manager import MarketManager

from helpers.date_timezone import Helpers
from backtest.models.base_models import BacktestAction, ContractSymbol
from backtest.backtest_module import BacktestModule
from backtest.configs.models import BacktestConfigs

from strategy.configs.models import StrategyConfig
from strategy.configs.factory.strategy_config_factory import StrategyConfigFactory
from strategy.strategy import Strategy
from strategy.historical_data import HistoricalData
from strategy.zigzag.strategy_zigzag import StrategyZigZag

from models.zigzag.models import EventZigZag, ZigZagType
from models.base_models import Contract, Event, Position

from database.database_module import DatabaseModule

class BacktestZigZagModule(BacktestModule):
    class RunStrategyZigZagModel(BacktestModule.RunStrategyModel):
        databaseModule: DatabaseModule
        currentDay: date
        tradesAvailable: int

        def __init__(self, strategy: Strategy, strategyConfig: StrategyConfig, isForStockPerformance: bool) -> None:
            super().__init__(strategy, strategyConfig, isForStockPerformance)
            self.databaseModule = DatabaseModule()
            self.databaseModule.openDatabaseConnectionForBacktest()
            self.databaseModule.deleteFills(self.databaseModule.getFills())
            
            self.currentDay = None
            self.tradesAvailable = 0

    #### READ/WRITE IN CSV FILES ####

    def addIndicatorsToStocksData(self, stocksData: Union[ContractSymbol, Tuple[Contract, List[Event]]], config: BacktestConfigs) -> Union[ContractSymbol, Tuple[Contract, List[Event]]]:
        newData: Union[str, Tuple[Contract, List[Event]]] = dict()
        for stockSymbol, (stock, bars) in stocksData.items():
            newData[stockSymbol] = (stock, HistoricalData.computeEventsForZigZagStrategy(bars, config.strategy))
        return newData

    def getStockFileHeaderRow(self) -> List[str]:
        return ["Symbol", "Date", "Open", "Close", "High", "Low", "ZigZag", "ZigZagType", "RSI"]

    def getStockFileDataRow(self, contract: Contract, data: EventZigZag) -> List[Any]:
        symbol = contract.symbol
        date = Helpers.dateToString(data.datetime)

        open = 0 if not data.open else round(data.open, 2)
        close = 0 if not data.close else round(data.close, 2)
        high = 0 if not data.high else round(data.high, 2)
        low = 0 if not data.low else round(data.low, 2)

        zigzag = False if data.zigzag is None else data.zigzag
        zigzagType = None if data.zigzagType is None else data.zigzagType.value
        rsi = None if data.rsi is None else round(data.rsi, 2)

        return [symbol, date, open, close, high, low, zigzag, zigzagType, rsi]

    def parseCSVFile(reader: csv.reader) -> List[Event]:
        configs = BacktestConfigs()
        line_count = 0
        contractEvents = []
        for row in reader:
            if line_count > 0:
                symbol = None if not row[0] else float(row[0])
                contract = Contract(symbol, configs.country)

                datetimeStr = None if not row[1] else float(row[1])
                datetime = Helpers.stringToDate(datetimeStr)

                open = 0 if not row[2] else float(row[2])
                close = 0 if not row[3] else float(row[3])
                high = 0 if not row[4] else float(row[4])
                low = 0 if not row[5] else float(row[5])

                zigzag = False if not row[6] else bool(distutils.util.strtobool(row[6]))
                zigzagType = None if not row[7] else ZigZagType(int(row[7]))
                rsi = 0 if not row[8] else float(row[8])

                event = EventZigZag(contract, datetime, open, close, high, low, zigzag, zigzagType, rsi)
                contractEvents.append(event)
            line_count += 1
        return contractEvents

    #### RUN STRATEGY ####

    def setupRunStrategy(self):
        config = BacktestConfigs()
        isForStockPerformance = True if config.action == BacktestAction.runStockPerformance else False
        strategyConfig = StrategyConfigFactory.createZigZagStrategyFor(MarketManager.getMarketFor(config.country))
        self.strategyModel = self.RunStrategyZigZagModel(StrategyZigZag(), strategyConfig, isForStockPerformance)

    def clearOldFills(self, event: Event):
        model: BacktestZigZagModule.RunStrategyZigZagModel = self.strategyModel
        fills = model.databaseModule.getFills()
        limitDate = event.datetime.date()-timedelta(days=40)
        filteredFills = list(filter(lambda x: x.date < limitDate, fills))
        model.databaseModule.deleteFills(filteredFills)

    def getFill(self, contract: Contract):
        model: BacktestZigZagModule.RunStrategyZigZagModel = self.strategyModel
        fills = model.databaseModule.getFills()
        filteredFills = list(filter(lambda x: contract.symbol == x.symbol, fills))
        filteredFills.sort(key=lambda x: x.date, reverse=True)
        if len(filteredFills) > 0:
            return filteredFills[0]
        return None

    def validateCurrentDay(self, event: Event):
        model: BacktestZigZagModule.RunStrategyZigZagModel = self.strategyModel
        if model.currentDay != event.datetime.date() or model.isForStockPerformance == True:
            balance = self.getBalance()
            model.tradesAvailable = 0
            if model.isForStockPerformance:
                model.tradesAvailable = 9999
            else:
                result = math.floor(balance/150000)
                if balance - (150000*result) >= 6000:
                    model.tradesAvailable = result+1
                else: 
                    model.tradesAvailable = result

            self.clearOldFills(event) 
            model.currentDay = None
    
    def getStrategyData(self, event: Event, events: List[Event], index: int):
        event: EventZigZag = event
        events: List[EventZigZag] = events
        daysBefore = 5
        previousEvents = self.getPreviousEvents(event, events, index, daysBefore)
        if len(previousEvents) < daysBefore:
            return None
        
        fill = self.getFill(event.contract)
        balance = self.getBalance()

        return StrategyZigZagData(contract= event.contract,
                                    totalCash= balance,
                                    event= event,
                                    previousEvents= previousEvents,
                                    position= None,
                                    fill= fill)
        
    def getPercentageChange(self, current, previous):
        if current == previous:
            return 100.0
        try:
            return (abs(current - previous) / previous) * 100.0
        except ZeroDivisionError:
            return 0

    def getPreviousEvents(self, event: EventZigZag, events: List[EventZigZag], currentPosition: int, daysBefore: int = 5):
        previousDays: List[EventZigZag] = []
        position = 0
        zigzagFound = False
        for x in range(daysBefore):            
            previousDataFound = False
            while (previousDataFound == False and
                    currentPosition-position > 0):
                position += 1
                item = events[currentPosition-position]
                if item.symbol == event.contract.symbol:
                    previousDataFound = True
                    previousDays.append(item)
                    if zigzagFound == True:
                        item.zigzag = False
                    elif item.zigzag == True:
                        zigzagFound = True

        for index, previousEvent in enumerate(previousDays, start=0):
            if index > 0 and previousEvent is not None and previousEvent.zigzag == True:
                shouldHaveZigZag = False
                for j in range(0, index-1):
                    item = previousDays[j]
                    previousEventValue = previousEvent.high if previousEvent.zigzagType == ZigZagType.high else previousEvent.low
                    itemEventValue = item.low if previousEvent.zigzagType == ZigZagType.high else item.high 
                    perfentageGap = self.getPercentageChange(previousEventValue, itemEventValue)
                    if perfentageGap >= 5:
                        shouldHaveZigZag = True
                previousEvent.zigzag = shouldHaveZigZag

        return previousDays

    def handleStrategyResult(self, event: Event, events: List[Event], result: StrategyResult, currentPosition: int):
        result: StrategyZigZagResult = result
        model: BacktestZigZagModule.RunStrategyZigZagModel = self.strategyModel
        if ((result.type == StrategyResultType.Buy or result.type == StrategyResultType.Sell) and model.tradesAvailable > 0):
            balance = self.getBalance()
            totalOrderCost = result.order.parentOrder.price*result.order.parentOrder.size
            if (balance > totalOrderCost and result.order.totalQuantity > 0) or model.isForStockPerformance:
                identifier = self.uniqueIdentifier(result.contract.symbol, result.event.datetime.date)
                model.positions[identifier] = (result.order,
                                                Position(contract=result.contract, size= result.order.parentOrder.size),
                                                result.event.datetime.date)
                print(result)
                model.tradesAvailable -= 1
                newFill = FillDB(result.contract.symbol, result.event.datetime.date())
                model.databaseModule.createFill(newFill)
        model.currentDay = event.datetime.date
        if len(events) > currentPosition+1 and events[currentPosition+1].datetime.date != model.currentDay:
#                 handleProfitAndStop(backtestModel, backtestReport, model, tempOrders, isForStockPerformance)
#                 handleExpiredFills(backtestModel, backtestReport, model, tempOrders, isForStockPerformance)



# class BackTestSwing():
#     results: Union[str, List[BackTestResult]]
#     trades: Union[str, List[str]]
#     cashAvailable: float
#     countryConfig: CountryConfig
#     strategyConfig: StrategyConfig

#     def __init__(self):
#         self.results = dict()
#         self.trades = dict()
#         self.cashAvailable = 10000
#         self.countryConfig = getConfigFor(CountryKey.USA)
#         self.strategyConfig= getStrategyConfigFor(key=self.countryConfig.key, timezone=self.countryConfig.timezone)

# def showPlot(mBars: List[BarData], zigzags:List[int]):
#     i = 0
#     dates = []
#     items = []
#     isForLow = True
#     for bar in mBars:
#         zigzag = zigzags[i]
#         if zigzag != 0:
#             dates.append(bar.date)
#             if isForLow:
#                 items.append(bar.low)
#                 isForLow = False
#             else:
#                 items.append(bar.high)
#                 isForLow = True

#         i += 1
#     plt.style.use('ggplot')

#     # Extracting Data for plotting
#     ohlc = util.df(mBars, ['date', 'open', 'high', 'low', 'close'])
#     ohlc['date'] = pd.to_datetime(ohlc['date'])
#     ohlc['date'] = ohlc['date'].apply(mpl_dates.date2num)
#     ohlc = ohlc.astype(float)

#     # Creating Subplots
#     fig, ax = plt.subplots()

#     candlestick_ohlc(ax, ohlc.values, width=0.6, colorup='green', colordown='red', alpha=0.8)

#     # Setting labels & titles
#     ax.set_xlabel('Date')
#     ax.set_ylabel('Price')
#     fig.suptitle('Daily Candlestick Chart of NIFTY50')

#     ax.plot(dates, items, color='blue', label='ZigZag')

#     fig.suptitle('Daily Candlestick Chart of PG with ZigZag')

#     plt.legend()

#     # Formatting Date
#     date_format = mpl_dates.DateFormatter('%d-%m-%Y')
#     ax.xaxis.set_major_formatter(date_format)
#     fig.autofmt_xdate()

#     fig.tight_layout()

#     plt.show()


# def runStockPerformance():
#     models = loadStocks("scan_to_download.csv")
#     print("Run Performance")
#     model = BackTestSwing()
#     report = BackTestReport()
#     runStrategy(backtestModel=model, backtestReport=report, models=models, forPerformance=True)

#     stocksPath = ("Scanner/ZigZag/%s/scan_to_download.csv" % CountryKey.USA.code)
#     path = ("backtest/Data/CSV/%s/ZigZag/Report" % (CountryKey.USA.code))
#     report.showPerformanceReport(path, stocksPath, model.countryConfig)

# def handleProfitAndStop(backtestModel: BackTestSwing, backtestReport: BackTestReport, model: BackTestModel, tempOrders: Union[str, Tuple[myOrder, Position, date, Ticker]], isForStockPerformance: bool):
#     orders = tempOrders.copy()
#     if (len(orders.values()) > 0):
#         for tempOrder, position, positionDate, ticker in orders.values():
#             if ((tempOrder.action == "BUY" and tempOrder.stopLossOrder.auxPrice > ticker.bid) or
#                     (tempOrder.action == "SELL" and tempOrder.stopLossOrder.auxPrice < ticker.ask)):
#                 perda = abs(tempOrder.stopLossOrder.auxPrice*tempOrder.stopLossOrder.totalQuantity-tempOrder.lmtPrice*tempOrder.totalQuantity)
#                 print("[%s] ❌ ❌ (%s) -> %.2f Size(%.2f) [%.2f]\n" % (ticker.time.date(), ticker.contract.symbol, perda, tempOrder.totalQuantity, backtestModel.cashAvailable))
#                 result = BackTestResult(symbol=ticker.contract.symbol, 
#                                         date=ticker.time, 
#                                         pnl=(-perda), 
#                                         action="Long" if tempOrder.action == "BUY" else "Short", 
#                                         type=BackTestResultType.stopLoss,
#                                         priceCreateTrade= tempOrder.lmtPrice, 
#                                         priceCloseTrade= tempOrder.stopLossOrder.auxPrice,
#                                         size= tempOrder.totalQuantity, 
#                                         averageVolume= model.averageVolume, 
#                                         volumeFirstMinute= model.volumeInFirstMinuteBar, 
#                                         totalInvested= tempOrder.lmtPrice*tempOrder.totalQuantity,
#                                         openPrice= ticker.open, 
#                                         ystdClosePrice= ticker.close,
#                                         cash= backtestModel.cashAvailable,
#                                         orderDate = positionDate.date())
#                 if isForStockPerformance:
#                     backtestReport.updateStockPerformance(ticker=ticker, type=result.type)
#                     backtestReport.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result, zigzag=True)
#                 else:
#                     backtestReport.updateResults(key=("%s" % ticker.time.date()), value=result)
#                     backtestReport.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result, zigzag=True)
#                     backtestModel.cashAvailable -= perda
#                 tempOrders.pop(magicKey(position.contract.symbol, positionDate))
#             elif ((tempOrder.action == "BUY" and tempOrder.takeProfitOrder.lmtPrice <= ticker.ask) or
#                     (tempOrder.action == "SELL" and tempOrder.takeProfitOrder.lmtPrice >= ticker.bid)):
#                 ganho = abs(tempOrder.takeProfitOrder.lmtPrice*tempOrder.takeProfitOrder.totalQuantity-tempOrder.lmtPrice*tempOrder.totalQuantity)
#                 print("[%s] ✅ ✅ (%s) -> %.2f Size(%.2f) high(%.2f) low(%.2f) [%.2f]\n" % (ticker.time.date(), ticker.contract.symbol, ganho, tempOrder.totalQuantity, ticker.ask, ticker.bid, backtestModel.cashAvailable))
#                 result = BackTestResult(symbol=ticker.contract.symbol, 
#                                         date=ticker.time, 
#                                         pnl=(ganho), 
#                                         action="Long" if tempOrder.action == "BUY" else "Short", 
#                                         type=BackTestResultType.takeProfit,
#                                         priceCreateTrade= tempOrder.lmtPrice, 
#                                         priceCloseTrade= tempOrder.takeProfitOrder.lmtPrice,
#                                         size= tempOrder.totalQuantity, 
#                                         averageVolume= model.averageVolume, 
#                                         volumeFirstMinute= model.volumeInFirstMinuteBar, 
#                                         totalInvested= tempOrder.lmtPrice*tempOrder.totalQuantity,
#                                         openPrice= ticker.open, 
#                                         ystdClosePrice= ticker.close,
#                                         cash= backtestModel.cashAvailable,
#                                         orderDate = positionDate.date())
#                 if isForStockPerformance:
#                     backtestReport.updateStockPerformance(ticker=ticker, type=result.type)
#                     backtestReport.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result, zigzag=True)
#                 else:
#                     backtestReport.updateResults(key=("%s" % ticker.time.date()), value=result)
#                     backtestReport.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result, zigzag=True)
#                     backtestModel.cashAvailable += ganho
#                 tempOrders.pop(magicKey(position.contract.symbol, positionDate))

# def handleExpiredFills(backtestModel: BackTestSwing, backtestReport: BackTestReport, model: BackTestModel, tempOrders: Union[str, Tuple[myOrder, Position, date, Ticker]], isForStockPerformance: bool):
#     orders = tempOrders.copy()
#     if (len(orders.values()) > 0):
#         for tempOrder, position, positionDate, ticker in orders.values():
#             if ticker.time.date() >= (positionDate+timedelta(days=0)).date():
#                 if ((tempOrder.action == "BUY" and (tempOrder.lmtPrice <= ticker.last)) or
#                     (tempOrder.action == "SELL" and (tempOrder.lmtPrice >= ticker.last))):
#                     closePrice = ticker.last
#                     ganho = abs(closePrice*tempOrder.takeProfitOrder.totalQuantity-tempOrder.lmtPrice*tempOrder.totalQuantity)
#                     result = BackTestResult(symbol=ticker.contract.symbol, 
#                                             date=ticker.time, 
#                                             pnl=(ganho), 
#                                             action="Long" if tempOrder.action == "BUY" else "Short", 
#                                             type=BackTestResultType.profit,
#                                             priceCreateTrade= tempOrder.lmtPrice, 
#                                             priceCloseTrade= closePrice,
#                                             size= tempOrder.totalQuantity, 
#                                             averageVolume= model.averageVolume, 
#                                             volumeFirstMinute= model.volumeInFirstMinuteBar, 
#                                             totalInvested= tempOrder.lmtPrice*tempOrder.totalQuantity,
#                                             openPrice= ticker.open, 
#                                             ystdClosePrice= ticker.close,
#                                             cash= backtestModel.cashAvailable,
#                                             orderDate = positionDate.date())
#                     if isForStockPerformance:
#                         backtestReport.updateStockPerformance(ticker=ticker, type=result.type)
#                         backtestReport.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result, zigzag=True)
#                     else:
#                         backtestReport.updateResults(key=("%s" % ticker.time.date()), value=result)
#                         backtestReport.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result, zigzag=True)
#                         backtestModel.cashAvailable += ganho
#                     print("[%s] ✅ (%s) -> %.2f Size(%.2f) [%.2f]\n" % (ticker.time.date(), ticker.contract.symbol, ganho, tempOrder.totalQuantity, backtestModel.cashAvailable))
#                 else:
#                     closePrice = ticker.last
#                     perda = abs(closePrice*tempOrder.totalQuantity-tempOrder.lmtPrice*tempOrder.totalQuantity)
#                     result = BackTestResult(symbol=ticker.contract.symbol, 
#                                             date=ticker.time, 
#                                             pnl=(-perda), 
#                                             action="Long" if tempOrder.action == "BUY" else "Short", 
#                                             type=BackTestResultType.loss,
#                                             priceCreateTrade= tempOrder.lmtPrice, 
#                                             priceCloseTrade= closePrice,
#                                             size= tempOrder.totalQuantity, 
#                                             averageVolume= model.averageVolume, 
#                                             volumeFirstMinute= model.volumeInFirstMinuteBar, 
#                                             totalInvested= tempOrder.lmtPrice*tempOrder.totalQuantity,
#                                             openPrice= ticker.open, 
#                                             ystdClosePrice= ticker.close,
#                                             cash= backtestModel.cashAvailable,
#                                             orderDate = positionDate.date())
#                     if isForStockPerformance:
#                         backtestReport.updateStockPerformance(ticker=ticker, type=result.type)
#                         backtestReport.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result, zigzag=True)
#                     else:
#                         backtestReport.updateResults(key=("%s" % ticker.time.date()), value=result)
#                         backtestReport.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result, zigzag=True)
#                         backtestModel.cashAvailable -= perda
#                     print("[%s] ❌ (%s) -> %.2f Size(%.2f) [%.2f]\n" % (ticker.time.date(), ticker.contract.symbol, perda, tempOrder.totalQuantity, backtestModel.cashAvailable))
#                 tempOrders.pop(magicKey(position.contract.symbol, positionDate))

# def runStrategy(backtestModel: BackTestSwing, backtestReport: BackTestReport, models: List[BackTestModel], forPerformance: bool = False):
#     strategy = StrategyZigZag()
#     tempOrders: Union[str, Tuple[myOrder, Position, date]] = dict()
#     isForStockPerformance = forPerformance
#     dayChecked = None
#     tradesAvailable = 0

#     databaseModule = DatabaseModule()
#     databaseModule.openDatabaseConnectionForBacktest()
#     databaseModule.deleteFills(databaseModule.getFills())

#     i = 0
#     for model in models:
#         ticker = model.ticker(backtestModel.countryConfig)
#         stock = ticker.contract

#         if dayChecked != ticker.time or isForStockPerformance == True:
#             totalInPositions = calculatePriceInPositions(tempOrders)
#             balance = backtestModel.cashAvailable - totalInPositions

#             tradesAvailable = 0
#             if isForStockPerformance:
#                 tradesAvailable = 2000
#             # elif balance/2 >= 6000 and balance < 150000:
#             #     tradesAvailable = 2
#             else:
#                 if backtestModel.cashAvailable > 150000:
#                     backtestModel.strategyConfig.maxToInvestPerStockPercentage = 1
#                 result = math.floor(balance/150000)
#                 if balance - (150000*result) >= 6000:
#                     tradesAvailable = result+1
#                 else: 
#                     tradesAvailable = result

#             clearOldFills(ticker, databaseModule) 
#             dayChecked = None

#         result = None
#         previousModels = getPreviousBarsData(model, models, i)
#         if (previousModels[0] is not None and
#             previousModels[1] is not None and
#             previousModels[2] is not None and
#             previousModels[3] is not None and
#             previousModels[4] is not None and
#             previousModels[5] is not None):
#             previousBars = [createCustomBarData(previousModels[5], backtestModel.countryConfig),
#                             createCustomBarData(previousModels[4], backtestModel.countryConfig),
#                             createCustomBarData(previousModels[3], backtestModel.countryConfig),
#                             createCustomBarData(previousModels[2], backtestModel.countryConfig),
#                             createCustomBarData(previousModels[1], backtestModel.countryConfig),
#                             createCustomBarData(previousModels[0], backtestModel.countryConfig)]
#             currentBar = createCustomBarData(model, backtestModel.countryConfig)
#             fill = getFill(ticker, databaseModule)
#             if isForStockPerformance == False:
#                 totalInPositions = calculatePriceInPositions(tempOrders)
#                 balance = backtestModel.cashAvailable - totalInPositions
#             else:
#                 balance = 6000
#             data = StrategyData(ticker=ticker, 
#                                 position=None, 
#                                 order=None, 
#                                 totalCash=min(balance, 150000),
#                                 previousBars=previousBars,
#                                 currentBar=currentBar,
#                                 fill=fill)
            
#             for bar in previousBars:
#                 if getPercentageChange(currentBar.close, bar.close) < 5:
#                     bar.zigzag = False
            
#             result = strategy.run(data, backtestModel.strategyConfig, backtestModel.countryConfig)
#             if ((result.type == StrategyResultType.Buy or result.type == StrategyResultType.Sell) and tradesAvailable > 0):
#                 totalInPositions = calculatePriceInPositions(tempOrders)
#                 balance = backtestModel.cashAvailable - totalInPositions
#                 totalOrderCost = result.order.lmtPrice*result.order.totalQuantity
#                 if (balance > totalOrderCost and result.order.totalQuantity > 0) or isForStockPerformance:
#                     tempOrders[magicKey(ticker.contract.symbol, ticker.time)] = (result.order,
#                                                                                     Position(account="",contract=stock, position=result.order.totalQuantity, avgCost=result.order.lmtPrice),
#                                                                                     ticker.time,
#                                                                                     ticker)
#                     print(result)
#                     tradesAvailable -= 1
#                     newFill = FillDB(ticker.contract.symbol, ticker.time.date())
#                     databaseModule.createFill(newFill)
#             else:
#                 for key, tupe in tempOrders.items():
#                     if key.split("_")[0] == ticker.contract.symbol:
#                         lista = list(tupe)
#                         lista[3] = ticker
#                         tempOrders[key] = tuple(lista)

#             dayChecked = ticker.time
#             if len(models) > i+1 and models[i+1].ticker(backtestModel.countryConfig).time != dayChecked:
#                 handleProfitAndStop(backtestModel, backtestReport, model, tempOrders, isForStockPerformance)
#                 handleExpiredFills(backtestModel, backtestReport, model, tempOrders, isForStockPerformance)
#         i += 1



# def createCustomBarData(model: BackTestModel, countryConfig: CountryConfig):
#     barData = BarData(date=model.ticker(countryConfig).time,
#                         open=model.openPrice,
#                         high=model.ask,
#                         low=model.bid,
#                         close=model.close,
#                         volume=model.volume)
#     return CustomBarData(barData, model.zigzag, model.rsi, barData.open)


# def magicKey(symbol: str, date: datetime):
#     return ("%s_%s" % (symbol, date.strftime("%y%m%d")))

# def showGraphFor(symbol: str):
#     ib = IB()
#     ib.connect('127.0.0.1', 7497, clientId=16)
#     stock = Stock(symbol, "SMART", "USD")
#     model = BackTestDownloadModel(path="", numberOfDays=225, barSize="1 day") # 5Years = 1825 days
#     bars = downloadHistoricDataFromIB(ib, stock, model)
    
#     closes = util.df(bars)['close']
#     lows = util.df(bars)['low']
#     highs = util.df(bars)['high']
#     RSI = computeRSI(closes, 14)
#     pivots = peak_valley_pivots_candlestick(closes.values, highs.values, lows.values, 0.05, -0.05)
#     showPlot(bars, pivots)

# # if __name__ == '__main__':
#     try:
#         #showGraphFor("AZPN")

#         #downloadData()
#         #runStockPerformance()
#         run()
        
#     except (KeyboardInterrupt, SystemExit) as e:
#         print(e)