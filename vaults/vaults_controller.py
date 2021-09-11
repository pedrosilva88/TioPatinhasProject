import asyncio
from helpers.logs import log
from vaults.vaults_protocol import VaultsControllerProtocol
from provider_factory.models import ProviderController
from portfolio.portfolio import Portfolio
from country_config.market_manager import Constants
from datetime import datetime
from pytz import timezone
from island.island import IslandProtocol
from vaults.zigzag.vault_zigzag import VaultZigZag
from vaults.stoch_diverge.vault_stoch_diverge import VaultStochDiverge
from strategy.configs.models import StrategyAction, StrategyType
from typing import List
from vaults.vault import Vault
from configs.models import TioPatinhasConfigs

# class IslandProtocol(Protocol):
#     marketWaiter: asyncio.Future

#     def subscribeStrategyEvents(self, ib: IB):
#         """Subscribe Events"""

#     def unsubscribeStrategyEvents(self, ib: IB):
#         """Subscribe Events"""    

class VaultsController(VaultsControllerProtocol):
    config: TioPatinhasConfigs
    vaults: List[Vault]
    nextVaultToRun: Vault = None
    nextActionToRun: StrategyAction = None

    portfolio: Portfolio

    delegate: IslandProtocol

    def __init__(self, delegate: IslandProtocol = None) -> None:
        self.vaults = []
        self.delegate = delegate
        self.config = TioPatinhasConfigs()
        self.portfolio = Portfolio()
        for strategyConfig in self.config.strategies:
            if strategyConfig.type == StrategyType.zigzag:
                self.vaults.append(VaultZigZag(strategyConfig, self.portfolio, self))
            elif strategyConfig.type == StrategyType.stoch_diverge:
                self.vaults.append(VaultStochDiverge(strategyConfig, self.portfolio, self))

    async def start(self):
        await self.scheduleNextOperation()

    async def createAsyncTask(self, targetDatetime: datetime):
        nowTime = datetime.now().astimezone(self.config.timezone)
        difference = (targetDatetime - nowTime)
        coro = asyncio.sleep(difference.total_seconds() + Constants.safeMarginSeconds)
        self.delegate.vaultWaiter = asyncio.ensure_future(coro)
        localTime = targetDatetime.astimezone(timezone('Europe/Lisbon'))
        log("🕐 Run Next Operation at %d/%d %d:%d 🕐" % (localTime.day, localTime.month, localTime.hour, localTime.minute))
        await asyncio.wait([self.delegate.vaultWaiter])
        self.delegate.vaultWaiter = None

    async def scheduleNextOperation(self):
        vaultToRun = None
        action = None
        actionToRun = None
        vaultToRunDatetime = None
        self.nextVaultToRun = None
        self.nextActionToRun = None

        for vault in self.vaults:
            nowTime = datetime.now(self.config.timezone)
            operationDatetime = vault.nextOperationDatetime(nowTime)
            action = vault.nextOperationAction(nowTime)
            if vaultToRunDatetime == None or operationDatetime <= vaultToRunDatetime:
                vaultToRun = vault
                vaultToRunDatetime = operationDatetime
                actionToRun = action

        
        if vaultToRun is not None and vaultToRunDatetime is not None:
            self.nextVaultToRun = vaultToRun
            self.nextActionToRun = actionToRun
            await self.createAsyncTask(vaultToRunDatetime)
            await self.runNextVaultOperation()

    async def runNextVaultOperation(self):
        await self.nextVaultToRun.runNextOperationBlock(self.nextActionToRun)
        await self.scheduleNextOperation()

    ## VaultsControllerProtocol
    @property
    def controller(self) -> ProviderController:
        return self.delegate.controller

class Constants:
    safeMarginSeconds: int = 3