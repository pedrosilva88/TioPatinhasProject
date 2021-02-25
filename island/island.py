from enum import Enum
from ib_insync import *
from scanner import *

class VaultType(Enum):
    OPG_US_RTL = 1
    
    def description(self):
        if self == OPG_US_RTL: return "Opening Price Gap for US Retailers"

class Vault:
    def __init__(self, type, scanner, strategie = None):
        self.type = type
        self.scanner = scanner
        self.strategie = strategie
        self.position = None
        self.order = None

class Island:
    def __init__(self):
        self.ib = IB()

    async def run(self, vault):
        with await self.ib.connectAsync():
            contracts = [
                Stock(symbol, 'SMART', 'USD')
                for symbol in vault.scanner]
            for contract in contracts:
                self.ib.reqMktData(contract)

            async for tickers in self.ib.pendingTickersEvent:
                for ticker in tickers:
                    print(ticker)

    def stop(self):
        self.ib.disconnect()



def createOPGRetailVault():
    scanner = Scanner().OPGRetailers()
    return Vault(VaultType.OPG_US_RTL, scanner)