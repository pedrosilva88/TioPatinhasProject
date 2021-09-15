from datetime import date
import csv
from models.base_models import Contract, Event
from strategy.strategy import Strategy
from strategy.configs.models import StrategyConfig
from strategy.models import StrategyData, StrategyResult, StrategyResultType
from strategy.impulse_pullback.models import StrategyImpulsePullbackResult
from models.impulse_pullback.models import EventImpulsePullback
from typing import Any, List, Tuple, Union
from backtest.backtest_module import BacktestModule
from backtest.models.base_models import BacktestAction, ContractSymbol
from backtest.configs.models import BacktestConfigs
from helpers.date_timezone import DateSystemFormat, Helpers
from strategy.historical_data import HistoricalData

class BacktestImpulsePullbackModule(BacktestModule):
    class RunStrategyImpulsePullbackModel(BacktestModule.RunStrategyModel):
        positionIPDates: Union[str, date]
        positionIPHolds: Union[str, int]
        eventsMapper: Union[str, EventImpulsePullback]
        currentDay: date
        tradesAvailable: int
        nextDayTrades: Union[str, StrategyImpulsePullbackResult]

        def __init__(self, strategy: Strategy, strategyConfig: StrategyConfig, isForStockPerformance: bool) -> None:
            super().__init__(strategy, strategyConfig, isForStockPerformance)
            self.currentDay = None
            self.tradesAvailable = 0
            self.positionStochDates = dict()
            self.eventsMapper = dict()
            self.nextDayTrades = dict()
            self.positionStochHolds = dict()

    def __init__(self) -> None:
        super().__init__()
        #self.reportModule = ReportStochDivergeModule()

    #### READ/WRITE IN CSV FILES ####

    def addIndicatorsToStocksData(self, stocksData: Union[ContractSymbol, Tuple[Contract, List[Event]]], config: BacktestConfigs) -> Union[ContractSymbol, Tuple[Contract, List[Event]]]:
        newData: Union[str, Tuple[Contract, List[Event]]] = dict()
        for stockSymbol, (stock, bars) in stocksData.items():
            events = HistoricalData.computeEventsForImpulsePullbackStrategy(bars, config.strategy)
            if events is not None:
                newData[stockSymbol] = (stock, events)
        return newData

    def getStockFileHeaderRow(self) -> List[str]:
        return ["Symbol", "Date", "Open", "Close", "High", "Low", "Stoch_K", "Stoch_D", 
                "EMA6", "EMA18", "EMA50", "EMA100", "EMA200",
                "BB_High", "BB_Low"
                "MACD", "MACD_Signal"]

    def getStockFileDataRow(self, contract: Contract, data: EventImpulsePullback) -> List[Any]:
        symbol = contract.symbol
        date = Helpers.dateToString(data.datetime, format=DateSystemFormat)

        open = 0 if not data.open else round(data.open, 2)
        close = 0 if not data.close else round(data.close, 2)
        high = 0 if not data.high else round(data.high, 2)
        low = 0 if not data.low else round(data.low, 2)

        k = None if data.stochK is None else round(data.stochK, 2)
        d = None if data.stochD is None else round(data.stochD, 2)

        ema6 = None if data.ema6 is None else round(data.ema6, 2)
        ema18 = None if data.ema18 is None else round(data.ema18, 2)
        ema50 = None if data.ema50 is None else round(data.ema50, 2)
        ema100 = None if data.ema100 is None else round(data.ema100, 2)
        ema200 = None if data.ema200 is None else round(data.ema200, 2)

        bb_high = None if data.bollingerBandHigh is None else round(data.bollingerBandHigh, 2)
        bb_low = None if data.bollingerBandLow is None else round(data.bollingerBandLow, 2)

        macd = None if data.macd is None else round(data.macd, 2)
        macd_signal = None if data.macdEMA is None else round(data.macdEMA, 2)

        return [symbol, date, open, close, high, low, k, d, 
                ema6, ema18, ema50, ema100, ema200,
                bb_high, bb_low,
                macd, macd_signal]

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

                event = EventImpulsePullback(contract, datetime, open, close, high, low, k, d, priceDivergenceOverbought, kDivergenceOverbought, priceDivergenceOversold, kDivergenceOversold)
                contractEvents.append(event)
            line_count += 1
        return contractEvents