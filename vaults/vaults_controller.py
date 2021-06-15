import asyncio
from vaults.vaults_protocol import VaultsControllerProtocol
from provider_factory.models import ProviderController
from portfolio.portfolio import Portfolio
from country_config.market_manager import Constants
from datetime import datetime
from island.island import IslandProtocol
from vaults.zigzag.vault_zigzag import VaultZigZag
from strategy.configs.models import StrategyType
from typing import List
from vaults.models import Vault
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

    async def start(self):
        await self.scheduleNextOperation()

    async def createAsyncTask(self, targetDatetime: datetime):
        nowTime = datetime.now().astimezone(self.config.timezone)
        difference = (targetDatetime - nowTime)
        coro = asyncio.sleep(difference.total_seconds() + Constants.safeMarginSeconds)
        self.delegate.vaultWaiter = asyncio.ensure_future(coro)
        await asyncio.wait([self.delegate.vaultWaiter])
        self.delegate.vaultWaiter = None

    async def scheduleNextOperation(self):
        vaultToRun = None
        vaultToRunDatetime = None
        self.nextVaultToRun = None

        for vault in self.vaults:
            nowTime = datetime.now().astimezone(self.config.timezone)
            operationDatetime = vault.nextOperationDatetime(nowTime).astimezone(self.config.timezone)
            if vaultToRunDatetime == None or operationDatetime <= vaultToRunDatetime:
                vaultToRun = vault
                vaultToRunDatetime = operationDatetime
        
        if vaultToRun is not None and vaultToRunDatetime is not None:
            self.nextVaultToRun = vaultToRun
            await self.createAsyncTask(vaultToRunDatetime)
            await self.runNextVaultOperation()

    async def runNextVaultOperation(self):
        nowTime = datetime.now().astimezone(self.config.timezone)
        await self.nextVaultToRun.runNextOperationBlock(nowTime)
        await self.scheduleNextOperation()

    class Constants:
        safeMarginSeconds: int = 3

    ## VaultsControllerProtocol

    def controller(self) -> ProviderController:
        return self.delegate.controller