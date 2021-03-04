from enum import Enum
from ib_insync import IB, Ticker, Contract, Stock
from helpers import logExecutionTicker
from scanner import Scanner
from strategy import Strategy, StrategyOPG, StrategyData, StrategyResult, StrategyResultType
from order import Order, StockPosition
from portfolio import Portfolio

class VaultType(Enum):
    OPG_US_RTL = 1
    
    def description(self):
        if self == OPG_US_RTL: return "Opening Price Gap for US Retailers"

class Vault:
    type: VaultType
    ib: IB
    scanner: Scanner
    strategy: Strategy
    portfolio: Portfolio

    def __init__(self, type: VaultType, scanner: Scanner, strategy: Strategy, portfolio: Portfolio):
        self.type = type
        self.scanner = scanner
        self.strategy = strategy
        self.portfolio = portfolio

    # Strategy

    def runStrategy(self, data: StrategyData):
        return self.strategy.run(data)

    def excuteTicker(self, ticker: Ticker):
        position = self.getPosition(ticker)
        order = self.getOrder(ticker)

        data = StrategyData(self.getTicker(ticker.contract.symbol), 
                            ticker.time, 
                            ticker.close, 
                            ticker.open, 
                            ticker.last, 
                            position, 
                            order, 
                            self.portfolio.cashBalance)

        result = self.runStrategy(data)
        logExecutionTicker(data, result)
        self.handleStrategyResult(result, ticker.contract)

    def handleStrategyResult(self, result: StrategyResult, contract: Contract):
        if ((result.type == StrategyResultType.Buy or result.type == StrategyResultType.Sell) and
            self.canCreateOrder(result.order)):
            return self.createOrder(result.order)

        elif (result.type == StrategyResultType.StrategyDateWindowExpired or result.type == StrategyResultType.DoNothing):
            return self.unsubscribeTicker(contract)

        elif (result.type == StrategyResultType.PositionExpired_Buy or result.type == StrategyResultType.PositionExpired_Sell):
            return self.cancelPosition(result.position)

        elif result.type == StrategyResultType.KeepOrder:
            return None #self.vault.portfolio.updateOrder(self.ib, result.order) Ainda preciso ver isto melhor. Preciso de olhar po Bid/Ask para fazer update do lmtPrice

        elif result.type == StrategyResultType.StrategyDateWindowExpiredCancelOrder:
            return self.cancelOrder(result.order)
        return

    # Portfolio

    def updatePortfolio(self):
        return self.portfolio.updatePortfolio(self.ib, self.getTicker)

    def getPosition(self, ticker: Ticker):
        return self.portfolio.getPosition(ticker)

    def getOrder(self, ticker: Ticker):
        return self.portfolio.getOrder(ticker)

    # Portfolio - Manage Orders

    def canCreateOrder(self, order: Order):
        return self.portfolio.canCreateOrder(self.ib, order)

    def createOrder(self, order: Order):
        return self.portfolio.createOrder(self.ib, order)

    def cancelOrder(self, order: Order):
        return self.portfolio.cancelOrder(self.ib, order)

    # Portfolio - Manage Positions

    def cancelPosition(self, position: StockPosition):
        return self.portfolio.cancelPosition(self.ib, position)

    # Scanner

    @property
    def tickers(self):
        return self.scanner.tickers

    def getTicker(self, symbol: str):
        return self.scanner.getTicker(symbol)

    def subscribeTickers(self):
        contracts = [Stock(ticker.symbol, 'SMART', 'USD') for ticker in self.tickers]
        for contract in contracts:
            self.subscribeTicker(contract)

    # IB

    def unsubscribeTicker(self, contract: Contract):
        ## Além de fazer cancelmarketData também devia de limpar na list de stocks que tenho no scanner
        self.ib.cancelMktData(contract)
        return 

    def subscribeTicker(self, contract: Contract):
        self.ib.reqMktData(contract)

def createOPGRetailVault():
    scanner = Scanner()
    scanner.getOPGRetailers()
    strategy = StrategyOPG()
    portfolio = Portfolio()
    return Vault(VaultType.OPG_US_RTL, scanner, strategy, portfolio)