from datetime import datetime
from strategy.strategy import Strategy
from strategy.configs.models import StrategyConfig
from typing import Callable

class Vault:
    strategyConfig: StrategyConfig
    strategy: Strategy
    
    def nextOperationDatetime(self, now: datetime) -> datetime:
        return self.strategyConfig.nextProcessDatetime(now)

    def nextOperationBlock(self, now: datetime) -> Callable:
        pass