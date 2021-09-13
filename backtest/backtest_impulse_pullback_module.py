from datetime import date
from typing import Union
from backtest.backtest_module import BacktestModule


class BacktestImpulsePullbackModule(BacktestModule):
    class RunStrategyImpulsePullbackModel(BacktestModule.RunStrategyModel):
        positionStochDates: Union[str, date]
        positionStochHolds: Union[str, int]
        eventsMapper: Union[str, EventStochDiverge]
        currentDay: date
        tradesAvailable: int
        nextDayTrades: Union[str, StrategyStochDivergeResult]

        def __init__(self, strategy: Strategy, strategyConfig: StrategyConfig, isForStockPerformance: bool) -> None:
            super().__init__(strategy, strategyConfig, isForStockPerformance)
            self.databaseModule = DatabaseModule()
            self.databaseModule.openDatabaseConnectionForBacktest()
            self.databaseModule.deleteFills(self.databaseModule.getFills())

            self.currentDay = None
            self.tradesAvailable = 0
            self.positionStochDates = dict()
            self.eventsMapper = dict()
            self.nextDayTrades = dict()
            self.positionStochHolds = dict()

    def __init__(self) -> None:
        super().__init__()
        self.reportModule = ReportStochDivergeModule()

    #### READ/WRITE IN CSV FILES ####

    def addIndicatorsToStocksData(self, stocksData: Union[ContractSymbol, Tuple[Contract, List[Event]]], config: BacktestConfigs) -> Union[ContractSymbol, Tuple[Contract, List[Event]]]:
        newData: Union[str, Tuple[Contract, List[Event]]] = dict()
        for stockSymbol, (stock, bars) in stocksData.items():
            events = HistoricalData.computeEventsForStochDivergeStrategy(bars, config.strategy)
            if events is not None:
                newData[stockSymbol] = (stock, events)
        return newData

    def getStockFileHeaderRow(self) -> List[str]:
        return ["Symbol", "Date", "Open", "Close", "High", "Low", "%K", "%D", "HH_Close", "LL_Close", "HL_Stoch", "LH_Stoch"]

    def getStockFileDataRow(self, contract: Contract, data: EventStochDiverge) -> List[Any]:
        symbol = contract.symbol
        date = Helpers.dateToString(data.datetime, format=DateSystemFormat)

        open = 0 if not data.open else round(data.open, 2)
        close = 0 if not data.close else round(data.close, 2)
        high = 0 if not data.high else round(data.high, 2)
        low = 0 if not data.low else round(data.low, 2)

        k = None if data.k is None else data.k
        d = None if data.d is None else data.d
        priceDivergenceOverbought = None if data.priceDivergenceOverbought is None else Helpers.dateToString(data.priceDivergenceOverbought, format=DateSystemFormat)
        kDivergenceOverbought = None if data.kDivergenceOverbought is None else Helpers.dateToString(data.kDivergenceOverbought, format=DateSystemFormat)
        priceDivergenceOversold = None if data.priceDivergenceOversold is None else Helpers.dateToString(data.priceDivergenceOversold, format=DateSystemFormat)
        kDivergenceOversold = None if data.kDivergenceOversold is None else Helpers.dateToString(data.kDivergenceOversold, format=DateSystemFormat)

        return [symbol, date, open, close, high, low, k, d, priceDivergenceOverbought, priceDivergenceOversold, kDivergenceOversold, kDivergenceOverbought]

    def parseCSVFile(self, reader: csv.reader) -> List[Event]:
        configs = BacktestConfigs()
        line_count = 0
        contractEvents = []
        for row in reader:
            if line_count > 0:
                symbol = None if not row[0] else row[0]
                contract = Contract(symbol, configs.country)

                datetimeStr = None if not row[1] else row[1]
                datetime = Helpers.stringToDate(datetimeStr, DateSystemFormat)

                open = 0 if not row[2] else float(row[2])
                close = 0 if not row[3] else float(row[3])
                high = 0 if not row[4] else float(row[4])
                low = 0 if not row[5] else float(row[5])

                k = None if not row[6] else float(row[6])
                d = None if not row[7] else float(row[7])
                datetimeStr = None if not row[8] else row[8]
                priceDivergenceOverbought = None if not datetimeStr else Helpers.stringToDate(datetimeStr, DateSystemFormat)
                datetimeStr = None if not row[9] else row[9]
                priceDivergenceOversold = None if not datetimeStr else Helpers.stringToDate(datetimeStr, DateSystemFormat)
                datetimeStr = None if not row[10] else row[10]
                kDivergenceOversold = None if not datetimeStr else Helpers.stringToDate(datetimeStr, DateSystemFormat)
                datetimeStr = None if not row[11] else row[11]
                kDivergenceOverbought = None if not datetimeStr else Helpers.stringToDate(datetimeStr, DateSystemFormat)

                event = EventStochDiverge(contract, datetime, open, close, high, low, k, d, priceDivergenceOverbought, kDivergenceOverbought, priceDivergenceOversold, kDivergenceOversold)
                contractEvents.append(event)
            line_count += 1
        return contractEvents