from enum import Enum
from scanner import Scanner
from strategy import Strategy, StrategyOPG
from order import Order, StockPosition
from portfolio import Portfolio

class VaultType(Enum):
    OPG_US_RTL = 1
    
    def description(self):
        if self == OPG_US_RTL: return "Opening Price Gap for US Retailers"

class Vault:
    type: VaultType
    scanner: Scanner
    strategy: Strategy
    portfolio: Portfolio

    def __init__(self, type: VaultType, scanner: Scanner, strategy: Strategy, portfolio: Portfolio):
        self.type = type
        self.scanner = scanner
        self.strategy = strategy
        self.portfolio = portfolio

def createOPGRetailVault():
    scanner = Scanner()
    scanner.getOPGRetailers()
    strategy = StrategyOPG()
    portfolio = Portfolio()
    return Vault(VaultType.OPG_US_RTL, scanner, strategy, portfolio)