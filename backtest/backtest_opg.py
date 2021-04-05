import os, sys
import os.path
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from IPython.display import display, clear_output
import pandas as pd
from scanner import Scanner
from strategy import StrategyOPG, StrategyData, StrategyResult, StrategyResultType, StrategyConfig, getStrategyConfigFor
from models import Order as myOrder, OrderAction
from helpers import log, utcToLocal

class BackTestOPG():
    results: [str, [BackTestResult]]
    trades: [str, [str]] = dict()
    cashAvailable = 2000
    countryCode: str
    countryConfig: CountryConfig
    strategyConfig: StrategyConfig

    def __init__(self, countryKey: CountryKey = CountryKey.USA):
        util.startLoop()
        #self.ib = IB()
        #self.ib.connect('127.0.0.1', 7497, clientId=16)
        self.strategy = StrategyOPG()
        self.countryCode = countryKey.code
        self.countryConfig = getConfigFor(key=countryKey)
        self.strategyConfig = getStrategyConfigFor(key=countryKey, timezone=self.countryConfig.timezone)

        self.results = dict()
        self.stockPerformance = dict()

    def run(self):
        models = self.loadFiles()
        print("Run Strategy")
        self.runStrategy(models)
        self.showReport()

    def runStockPerformance(self):
        models = self.loadFiles()
        print("Run Performance")
        self.runStrategy(models=models, forPerformance=True)
        self.showPerformanceReport()

    def loadFiles(self):
        scanner = Scanner()
        scanner.getOPGRetailers(path=('../scanner/Data/CSV/%s/OPG_Retails_SortFromBackTest.csv' % (self.countryCode)))
        stocks = scanner.stocks
        #stocks = [Stock("DGE","SMART",self.countryConfig.currency), Stock("HBP","SMART",self.countryConfig.currency), Stock("VUZI","SMART",self.countryConfig.currency), Stock("ASO","SMART",self.countryConfig.currency)]

        total = len(stocks)
        current = 0
        models = []
        for stock in stocks:
            current += 1
            sys.stdout.write("\t Fetching CSV Files: %i/%i \r" % (current, total) )
            if current <= total-1:
                sys.stdout.flush()
            else:
                print("")

            name = ("backtest/Data/CSV/%s/%s.csv" % (self.countryCode, stock.symbol))
            if not os.path.isfile(name):
                print("File not found ", name)
                continue
            models += self.getModelsFromCSV(name)
        print("Sort all Ticks by date")
        models.sort(key=lambda x: x.dateString, reverse=False)
        return models

    # Reports

    def saveReportResultInFile(self, data:[[]]):
        name = ("backtest/Data/CSV/%s/Report/ResultsPnL.csv" % (self.countryCode))
        with open(name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "PnL", "Trades"])
            for model in data:
                writer.writerow(model)

    def saveReportTradesInFile(self, data:[[]]):
        name = ("backtest/Data/CSV/%s/Report/ResultsTrades.csv" % (self.countryCode))
        with open(name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Symbol", "Result", "PnL", "Price CreateTrade", "Price CloseTrade", "Size", "Avg Volume",  "Volume 1st minute", "Total Invested", "Open Price", "YSTD Close Price", "Action", "Cash"])
            for model in data:
                writer.writerow(model)

    def saveReportPerformance(self, data):
        scanner = Scanner()
        scanner.getOPGRetailers(path=('../scanner/Data/CSV/%s/OPG_Retails_SortFromBackTest.csv' % (self.countryCode)))
        stocks = scanner.stocks
        name = ("backtest/Data/CSV/%s/Report/ResultsStockPerformance.csv" % (self.countryCode))
        with open(name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Symbol", "Exchange", "Currency", "OPGs Found", "Take Profit", "Profit", "StopLoss", "Loss", "Wins", "%"])
            for key, item in data.items():
                total = item[0]+item[1]+item[2]+item[3]
                wins = item[0]+item[1]
                writer.writerow([key,
                                "SMART",
                                self.countryConfig.currency,
                                total,
                                item[0],
                                item[1],
                                item[2],
                                item[3],
                                wins,
                                (wins/total)*100])
                item = list(filter(lambda x : x.symbol == key, stocks)).pop()
                stocks.remove(item)
            for item in stocks:
                writer.writerow([item.symbol,
                                "SMART",
                                self.countryConfig.currency,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0])

    def showReport(self):
        items = [[]]
        for key, array in self.results.items():
            total = 0
            for item in array:
                total += item.pnl
            items.append([key, total, len(array)])
            print("%s: %.2f€ %d" % (key, total, len(array)))

        self.saveReportResultInFile(items)

        items = [[]]
        for key, array in self.trades.items():
            for item in array:
                items.append(item)

        self.saveReportTradesInFile(items)

    def showPerformanceReport(self):
        self.saveReportPerformance(self.stockPerformance)

    def updateResults(self, key: str, value: BackTestResult):
        if key in self.results:
            self.results[key].append(value)
        else:
            self.results[key] = [value]

    def updateTrades(self, key: str, ticker: Ticker, result: BackTestResult):
        resultArray = []
        resultArray.append(key) # date
        resultArray.append(ticker.contract.symbol) # symbol
        resultArray.append(result.type.emoji()) # ✅ or ✅ ✅ or ❌  or ❌ ❌
        resultArray.append(result.pnl) # PnL
        resultArray.append(result.priceCreateTrade) # Price CreateTrade
        resultArray.append(result.priceCloseTrade) # Price CloseTrade
        resultArray.append(result.size) # Size
        resultArray.append(result.averageVolume) # AverageVolume
        resultArray.append(result.volumeFirstMinute) # VolumeFirstMinute
        resultArray.append(result.totalInvested) # Total Invested
        resultArray.append(result.openPrice) # Open Price
        resultArray.append(result.ystdClosePrice) # YSTD Close Price
        resultArray.append(result.action) # Action Long or Short
        resultArray.append(result.cash) # Cash
        
        if key in self.trades:
            self.trades[key].append(resultArray)
        else:
            self.trades[key] = [resultArray]

    def updateStockPerformance(self, ticker: Ticker, type: BackTestResultType):
        array = []
        if ticker.contract.symbol in self.stockPerformance:
            array = self.stockPerformance[ticker.contract.symbol]
        else:
            array = [0,0,0,0]

        if type == BackTestResultType.takeProfit:
            array[0] += 1
        elif type == BackTestResultType.profit:
            array[1] += 1
        elif type == BackTestResultType.stopLoss:
            array[2] += 1
        elif type == BackTestResultType.loss:
            array[3] += 1

        self.stockPerformance[ticker.contract.symbol] = array

    # Run Strategy
    
    def runStrategy(self, models: [BackTestModel], forPerformance: bool = False):
        orders: [str, myOrder] = dict()
        tempOrders: [str, myOrder] = dict()
        positions: [str, Position] = dict()
        dayTradingStocksEnded: [str] = []
        currentDay: date = None
        isForStockPerformance = forPerformance

        for model in models:
            ticker = model.ticker(self.countryConfig)
            stock = ticker.contract
            today = utcToLocal(ticker.time.replace(microsecond=0), self.countryConfig.timezone).date()
            position = None
            order = None
            if not currentDay or (currentDay != today):
                currentDay = today
                orders = dict()
                tempOrders = dict()
                positions = dict()
                dayTradingStocksEnded = []

            if ticker.contract.symbol in dayTradingStocksEnded:
                continue

            if (ticker.contract.symbol in positions and
                ticker.contract.symbol in tempOrders):
                tempOrder = tempOrders[ticker.contract.symbol]
                position = positions[ticker.contract.symbol]
                if ((tempOrder.action == OrderAction.Buy and (tempOrder.takeProfitOrder.lmtPrice < ticker.ask or (ticker.volume > 0 and ticker.last >= tempOrder.takeProfitOrder.lmtPrice))) or # or (ticker.volume > 0 and ticker.last >= tempOrder.takeProfitOrder.lmtPrice)
                    (tempOrder.action == OrderAction.Sell and (tempOrder.takeProfitOrder.lmtPrice > ticker.bid or (ticker.volume > 0 and ticker.last <= tempOrder.takeProfitOrder.lmtPrice)))): # or (ticker.volume > 0 and ticker.last <= tempOrder.takeProfitOrder.lmtPrice)
                    ganho = abs(tempOrder.takeProfitOrder.lmtPrice*tempOrder.takeProfitOrder.totalQuantity-tempOrder.lmtPrice*tempOrder.totalQuantity)
                    print("Success ✅ - %.2f FirstMinute(%d) Average(%d) Size(%.2f)\n" % (ganho, model.volumeInFirstMinuteBar, model.averageVolume, tempOrder.totalQuantity))
                    result = BackTestResult(symbol=ticker.contract.symbol, 
                                            date=ticker.time, 
                                            pnl=(ganho), 
                                            action=tempOrder.action.code, 
                                            type=BackTestResultType.takeProfit,
                                            priceCreateTrade= tempOrder.lmtPrice, 
                                            priceCloseTrade= tempOrder.takeProfitOrder.lmtPrice,
                                            size= tempOrder.totalQuantity, 
                                            averageVolume= model.averageVolume, 
                                            volumeFirstMinute= model.volumeInFirstMinuteBar, 
                                            totalInvested= tempOrder.lmtPrice*tempOrder.totalQuantity,
                                            openPrice= ticker.open, 
                                            ystdClosePrice= ticker.close,
                                            cash= self.cashAvailable)
                    if isForStockPerformance:
                        self.updateStockPerformance(ticker=ticker, type=result.type)
                    else:
                        self.updateResults(key=("%s" % ticker.time.date()), value=result)
                        self.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result)
                        self.cashAvailable += ganho
                    dayTradingStocksEnded.append(ticker.contract.symbol)
                    continue
                elif ((tempOrder.action == OrderAction.Buy and ticker.ask <= tempOrder.stopLossOrder.auxPrice) or
                    (tempOrder.action == OrderAction.Sell and ticker.bid >= tempOrder.stopLossOrder.auxPrice )):
                    perda = abs(tempOrder.stopLossOrder.auxPrice*tempOrder.stopLossOrder.totalQuantity-tempOrder.lmtPrice*tempOrder.totalQuantity)
                    print("StopLoss ❌ - %.2f FirstMinute(%d) Average(%d) Size(%.2f)\n" % (perda, model.volumeInFirstMinuteBar, model.averageVolume, tempOrder.totalQuantity))
                    result = BackTestResult(symbol=ticker.contract.symbol, 
                                            date=ticker.time, 
                                            pnl=(-perda), 
                                            action=tempOrder.action.code, 
                                            type=BackTestResultType.stopLoss,
                                            priceCreateTrade= tempOrder.lmtPrice, 
                                            priceCloseTrade= tempOrder.stopLossOrder.auxPrice,
                                            size= tempOrder.totalQuantity, 
                                            averageVolume= model.averageVolume, 
                                            volumeFirstMinute= model.volumeInFirstMinuteBar, 
                                            totalInvested= tempOrder.lmtPrice*tempOrder.totalQuantity,
                                            openPrice= ticker.open, 
                                            ystdClosePrice= ticker.close,
                                            cash= self.cashAvailable)
                    if isForStockPerformance:
                        self.updateStockPerformance(ticker=ticker, type=result.type)
                    else:
                        self.updateResults(key=("%s" % ticker.time.date()), value=result)
                        self.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result)
                        self.cashAvailable -= perda
                    dayTradingStocksEnded.append(ticker.contract.symbol)
                    continue
            elif ticker.contract.symbol in orders:
                order = orders[ticker.contract.symbol]
                if ((order.action == OrderAction.Buy and (order.lmtPrice > ticker.bid or (ticker.volume > 0 and ticker.last == order.lmtPrice))) or  # or (ticker.volume > 0 and ticker.last >= order.lmtPrice)
                    (order.action == OrderAction.Sell and (order.lmtPrice < ticker.ask or (ticker.volume > 0 and ticker.last == order.lmtPrice)))):  # or (ticker.volume > 0 and ticker.last <= order.lmtPrice)
                    tempOrders[ticker.contract.symbol] = order
                    del orders[ticker.contract.symbol]
                    positions[ticker.contract.symbol] = Position(account="",contract=stock, position=order.totalQuantity, avgCost=order.lmtPrice)
                    position = positions[ticker.contract.symbol]
                    order = None
            
            data = StrategyData(ticker, 
                                position, 
                                order, 
                                self.cashAvailable,
                                model.averageVolume,
                                model.volumeInFirstMinuteBar)
            result = self.strategy.run(data, self.strategyConfig, self.countryConfig)

            if (result.type == StrategyResultType.Buy or result.type == StrategyResultType.Sell):
                totalInPositions = self.calculatePriceInPositions(positions)
                totalInOrders = self.calculatePriceInOrders(orders)
                balance = self.cashAvailable - totalInOrders - totalInPositions
                totalOrderCost = result.order.lmtPrice*result.order.totalQuantity
                if (balance > totalOrderCost and result.order.totalQuantity > 0) or isForStockPerformance:
                    orders[ticker.contract.symbol] = result.order
                    print(result)

            elif result.type == StrategyResultType.StrategyDateWindowExpired:
                dayTradingStocksEnded.append(ticker.contract.symbol)
            elif result.type == StrategyResultType.DoNothing:
                None
            elif (result.type == StrategyResultType.PositionExpired_Buy or result.type == StrategyResultType.PositionExpired_Sell):
                dayTradingStocksEnded.append(ticker.contract.symbol)
                if (ticker.contract.symbol in positions and
                    ticker.contract.symbol in tempOrders):
                    tempOrder = tempOrders[ticker.contract.symbol]
                    position = positions[ticker.contract.symbol]
                    if ((tempOrder.action == OrderAction.Buy and (tempOrder.lmtPrice < ticker.ask)) or  # or (ticker.volume > 0 and ticker.last >= tempOrder.lmtPrice)
                        (tempOrder.action == OrderAction.Sell and (tempOrder.lmtPrice > ticker.bid))): # or ticker.last == tempOrder.lmtPrice
                        closePrice = ticker.last
                        ganho = abs(closePrice*tempOrder.takeProfitOrder.totalQuantity-tempOrder.lmtPrice*tempOrder.totalQuantity)
                        result = BackTestResult(symbol=ticker.contract.symbol, 
                                                date=ticker.time, 
                                                pnl=(ganho), 
                                                action=tempOrder.action.code, 
                                                type=BackTestResultType.profit,
                                                priceCreateTrade= tempOrder.lmtPrice, 
                                                priceCloseTrade= closePrice,
                                                size= tempOrder.totalQuantity, 
                                                averageVolume= model.averageVolume, 
                                                volumeFirstMinute= model.volumeInFirstMinuteBar, 
                                                totalInvested= tempOrder.lmtPrice*tempOrder.totalQuantity,
                                                openPrice= ticker.open, 
                                                ystdClosePrice= ticker.close,
                                                cash= self.cashAvailable)
                        if isForStockPerformance:
                            self.updateStockPerformance(ticker=ticker, type=result.type)
                        else:
                            self.updateResults(key=("%s" % ticker.time.date()), value=result)
                            self.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result)
                            self.cashAvailable += ganho
                        print("Success (not profit) ✅ - %.2f FirstMinute(%d) Average(%d) Size(%.2f)\n" % (ganho, model.volumeInFirstMinuteBar, model.averageVolume, tempOrder.totalQuantity))
                    else:
                        closePrice = ticker.last
                        perda = abs(closePrice*tempOrder.takeProfitOrder.totalQuantity-tempOrder.lmtPrice*tempOrder.totalQuantity)
                        result = BackTestResult(symbol=ticker.contract.symbol, 
                                                date=ticker.time, 
                                                pnl=(-perda), 
                                                action=tempOrder.action.code, 
                                                type=BackTestResultType.loss,
                                                priceCreateTrade= tempOrder.lmtPrice, 
                                                priceCloseTrade= closePrice,
                                                size= tempOrder.totalQuantity, 
                                                averageVolume= model.averageVolume, 
                                                volumeFirstMinute= model.volumeInFirstMinuteBar, 
                                                totalInvested= tempOrder.lmtPrice*tempOrder.totalQuantity,
                                                openPrice= ticker.open, 
                                                ystdClosePrice= ticker.close,
                                                cash= self.cashAvailable)
                        if isForStockPerformance:
                            self.updateStockPerformance(ticker=ticker, type=result.type)
                        else:
                            self.updateResults(key=("%s" % ticker.time.date()), value=result)
                            self.updateTrades(key=("%s" % ticker.time.date()), ticker=ticker, result=result)
                            self.cashAvailable -= perda
                        print("Loss ❌ - %.2f FirstMinute(%d) Average(%d) Size(%.2f)\n" % (perda, model.volumeInFirstMinuteBar, model.averageVolume, tempOrder.totalQuantity))

            elif result.type == StrategyResultType.KeepOrder:
                orders[ticker.contract.symbol] = result.order
            elif (result.type == StrategyResultType.CancelOrder or result.type == StrategyResultType.StrategyDateWindowExpiredCancelOrder):
                print("Order Cancelled")
                del orders[ticker.contract.symbol]
                dayTradingStocksEnded.append(ticker.contract.symbol)
            else:
                None

        #print("\n\nResult: LimitProfits(%d) Profits(%d) StopLosses(%d) Losses(%d) PnL(%.2f)" % (limitProfits, profits, stopLosses, losses, (totalWon-totalLoss)))

    def calculatePriceInOrders(self, orders):
        total = 0
        for key, item in orders.items():
            total += item.lmtPrice * item.totalQuantity
        return total

    def calculatePriceInPositions(self, positions):
        total = 0
        for key, item in positions.items():
            total += item.position * item.avgCost
        return total

    # Load

    def createListOfBackTestModels(self, stock: Contract, mBars: [BarData], dBars: [BarData]) -> [BackTestModel]:
        models = []
        lastDay = None
        lastAverageVolume = None
        lastVolumeFirstMinute = None
        barTodayOpen = None
        barYstdClose = None

        for mBar in mBars:
            if (not lastDay or (lastDay.replace(microsecond=0, tzinfo=None).date() != mBar.date.replace(microsecond=0, tzinfo=None).date())):
                result = self.getDayBar(mBar.date, dBars)
                averageVolume = self.getAverageVolume(mBars, mBar.date)
                lastVolumeFirstMinute = self.getVolumeInFirstMinute(mBars, mBar.date)
                if (result and result[0] and result[1]):
                    barTodayOpen = result[1].open
                    barYstdClose = result[0].close
                else:
                    barTodayOpen = None
                    barYstdClose = None
                lastDay = mBar.date.replace(microsecond=0, tzinfo=None)
            model = BackTestModel(barTodayOpen, barYstdClose, mBar.low, mBar.high, mBar.close, mBar.volume, stock.symbol, mBar.date.strftime("%Y-%m-%d %H:%M:%S"), averageVolume, lastVolumeFirstMinute)
            models.append(model)
        return models
    
    def getModelsFromCSV(self, filePath: str):
        formatDate = "%Y-%m-%d %H:%M:%S"
        models = []
        with open(filePath) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count > 0:
                    volumeMinute = None if not row[9] else float(row[9])
                    averageVolume = None if not row[8] else float(row[8])
                    openPrice = 0 if not row[3] else float(row[3])
                    close = 0 if not row[2] else float(row[2])
                    bid = 0 if not row[4] else float(row[4])
                    ask = 0 if not row[5] else float(row[5])
                    last = 0 if not row[6] else float(row[6])
                    volume = 0 if not row[7] else float(row[7])
                    models.append(BackTestModel(openPrice, close, bid, ask, last, volume, row[0], row[1], averageVolume, volumeMinute))
                line_count += 1
        return models

    def getDayBar(self, date: datetime, bars: [BarData]):
        for i in range(len(bars)):
            if date.replace(microsecond=0, tzinfo=None).date() == bars[i].date:
                if i == 0:
                    return None, None
                else:
                    return bars[i-1], bars[i]

    def getAverageVolume(self, data: [BarData], date: date):
        last = (date.year, date.month, date.day)
        firstDate = date-timedelta(days=21)
        first = (firstDate.year, firstDate.month, firstDate.day)
        filterData = list(filter(lambda x: (first < (x.date.year, x.date.month, x.date.day) < last), data))
        nBars = len(filterData)
        if nBars > 0:
            sum = 0
            for data in filterData: 
                sum += data.volume
            
            return sum/nBars
        else:
            return 0

    def getVolumeInFirstMinute(self, data: [BarData], date: date):
        target = datetime.combine(date, time(9,30))
        newTarget = self.countryConfig.timezone.localize(target, is_dst=None)
        filterData = list(filter(lambda x: newTarget == utcToLocal(x.date.replace(second=0, microsecond=0), self.countryConfig.timezone), data))
        if len(filterData) >= 1:
            total = 0
            for item in filterData:
                total += item.volume      
            return total
        else: return None
 
if __name__ == '__main__':
    try:
        backtest = BackTestOPG(countryKey=CountryKey.USA)
        modelMinutes = BackTestDownloadModel(path="", numberOfDays=365, barSize="1 min")
        modelDays = BackTestDownloadModel(path="", numberOfDays=365, barSize="1 day")
        #backtest.downloadStocksToCSVFile()
        mBars = self.downloadHistoricDataFromIB(stock, modelMinutes)
        dBars = self.downloadHistoricDataFromIB(stock, modelDays)
        models = self.createListOfBackTestModels(stock, mBars, dBars)
        self.saveDataInCSVFile(stock.symbol, models)


        backtest.run()
        #backtest.runStockPerformance()
    except (KeyboardInterrupt, SystemExit):
        None