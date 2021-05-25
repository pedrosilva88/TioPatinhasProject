from country_config.models import Market
from datetime import datetime, time
from enum import Enum

class StrategyType(Enum):
    zigzag = 'zigzag'
    opg = 'opg'
    stochi = 'stochi'

    def strategyFromCode(code: str):
        if code == 'zigzag':
            return StrategyType.zigzag
        elif code == 'opg':
            return StrategyType.opg
        elif code == 'stochi':
            return StrategyType.stochi

class StrategyConfig:
    market: Market
    runStrategyTime: time

    willingToLose: float
    maxToInvestPerStockPercentage: float

    def __init__(self, market: Market, runStrategyTime: time, willingToLose: float, maxToInvestPerStockPercentage: float) -> None:
        self.market = market
        self.runStrategyTime = runStrategyTime
        self.willingToLose = willingToLose
        self.maxToInvestPerStockPercentage = maxToInvestPerStockPercentage

    def nextProcessDatetime(self, now: datetime) -> datetime:
        pass