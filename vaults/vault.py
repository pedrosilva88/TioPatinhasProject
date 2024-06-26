from pytz import timezone
from vaults.vaults_controller import VaultsControllerProtocol
from configs.models import TioPatinhasConfigs
from datetime import datetime
from helpers.logs import log
from models.base_models import Contract
from typing import List
from strategy.strategy import Strategy
from strategy.configs.models import StrategyAction, StrategyConfig
from scanner import Scanner
from portfolio import Portfolio

class Vault:
    configs: TioPatinhasConfigs
    strategyConfig: StrategyConfig
    strategy: Strategy
    portfolio: Portfolio

    contracts: List[Contract]

    delegate: VaultsControllerProtocol
    
    def __init__(self, strategyConfig: StrategyConfig, portfolio: Portfolio, delegate: VaultsControllerProtocol) -> None:
        self.portfolio = portfolio
        self.strategyConfig = strategyConfig
        self.delegate = delegate

    def setupVault(self):
        log("🏃‍ Setup Vault for %s Market 🏃‍" % self.strategyConfig.market.country.code)
        self.configs = TioPatinhasConfigs()
        path = Scanner.getPathFor(self.configs.provider.value, 
                                            self.strategyConfig.type.folderName,
                                            self.strategyConfig.market.country.code)
        self.contracts = Scanner.contratcsFrom(path)

    # Reset

    def resetVault(self):
        log("🤖 Reset Vault for %s Market 🤖‍" % self.strategyConfig.market.country.code)
        self.contracts = []
        
    def nextOperationDatetime(self, now: datetime) -> datetime:
        return self.strategyConfig.nextProcessDatetime(now)
    
    def nextOperationAction(self, now: datetime) -> StrategyAction:
        return self.strategyConfig.nextAction(now)

    def runNextOperationBlock(self, action: StrategyAction):
        pass

    async def syncProviderData(self):
        log("📣 Sync Provider Data 📣")
        await self.delegate.controller.provider.syncData()
