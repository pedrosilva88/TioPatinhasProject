from configs.models import TioPatinhasConfigs
from datetime import datetime
from logging import log
from models.base_models import Contract
from typing import List
from strategy.strategy import Strategy
from strategy.configs.models import StrategyConfig
from scanner import Scanner
from portfolio import Portfolio

class Vault:
    strategyConfig: StrategyConfig
    strategy: Strategy
    portfolio: Portfolio

    contracts: List[Contract]
    
    def __init__(self, strategyConfig: StrategyConfig, portfolio: Portfolio) -> None:
        self.portfolio = portfolio
        self.strategyConfig = strategyConfig

    def setupVault(self):
        log("🏃‍ Setup Vault for %s Market 🏃‍" % self.strategyConfig.market.country.code)
        configs = TioPatinhasConfigs()
        path = Scanner.getPathFor(configs.provider, 
                                            self.strategyConfig.type.value,
                                            self.strategyConfig.market.country.code)
        self.contracts = Scanner.contratcsFrom(path)

    # Reset

    def resetVault(self):
        log("🤖 Reset Vault for %s Market 🤖‍" % self.strategyConfig.market.country.code)
        self.contracts = []
        
    def nextOperationDatetime(self, now: datetime) -> datetime:
        return self.strategyConfig.nextProcessDatetime(now)

    def runNextOperationBlock(self, now: datetime):
        pass

    async def syncProviderData(self):
        pass