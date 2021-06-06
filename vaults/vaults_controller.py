import asyncio
from datetime import datetime, timezone
from vaults.zigzag.vault_zigzag import VaultZigZag
from strategy.configs.models import StrategyType
from typing import List
from vaults.models import Vault
from configs.models import TioPatinhasConfigs

class VaultsController:
    vaults: List[Vault]
    nextVaultToRun: Vault = None

    def __init__(self) -> None:
        self.vaults = []
        config = TioPatinhasConfigs()
        for strategyConfig in config.strategies:
            if strategyConfig.type == StrategyType.zigzag:
                self.vaults.append(VaultZigZag())

    async def start(self):
        await self.scheduleNextOperation()

    async def createAsyncTask(self, targetDatetime: datetime):
        nowTime = datetime.now()
        difference = (targetDatetime - nowTime)
        coro = asyncio.sleep(difference.total_seconds())
        self.delegate.marketWaiter = asyncio.ensure_future(coro)
        await asyncio.wait([self.delegate.marketWaiter])
        self.delegate.marketWaiter = None

    async def scheduleNextOperation(self):
        config = TioPatinhasConfigs()
        vaultToRun = None
        vaultToRunDatetime = None
        self.nextVaultToRun = None

        for vault in self.vaults:
            operationDatetime = vault.nextOperationDatetime().astimezone(config.timezone)
            if vaultToRunDatetime == None or operationDatetime <= vaultToRunDatetime:
                vaultToRun = vault
                vaultToRunDatetime = operationDatetime
        
        if vaultToRun is not None and vaultToRunDatetime is not None:
            self.nextVaultToRun = vaultToRun
            await self.createAsyncTask(vaultToRunDatetime)
            self.runNextVaultOperation()

    async def runNextVaultOperation(self):
        await self.nextVaultToRun.nextOperationBlock()
        await self.scheduleNextOperation()

