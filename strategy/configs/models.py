from models.base_models import OrderType
from country_config.models import Market
from datetime import datetime, time
from enum import Enum

class StrategyType(Enum):
    none = 'none'
    combined = 'combined'
    zigzag = 'zigzag'
    opg = 'opg'
    stoch_diverge = 'stoch_diverge'
    stoch_sma = 'stoch_sma'
    impulse_pullback = 'impulse_pullback'
    bounce = 'bounce'

    def strategyFromCode(code: str):
        if code == 'none':
            return StrategyType.none
        elif code == 'combined':
            return StrategyType.combined
        elif code == 'zigzag':
            return StrategyType.zigzag
        elif code == 'opg':
            return StrategyType.opg
        elif code == 'stoch_diverge':
            return StrategyType.stoch_diverge
        elif code == 'stoch_sma':
            return StrategyType.stoch_sma
        elif code == 'impulse_pullback':
            return StrategyType.impulse_pullback
        elif code == 'bounce':
            return StrategyType.bounce

    @property
    def folderName(self) -> str:
        if self == StrategyType.none or self == StrategyType.combined:
            return "_raw"
        elif self == StrategyType.zigzag:
            return "zigzag"
        elif self == StrategyType.opg:
            return "opg"
        elif self == StrategyType.stoch_diverge:
            return "stoch_diverge"
        elif self == StrategyType.stoch_sma:
            return "stoch_sma"
        elif self == StrategyType.impulse_pullback:
            return "impulse_pullback"
        elif self == StrategyType.bounce:
            return "bounce"

class StrategyAction(Enum):
    runStrategy = 0
    checkPositions = 1

class StrategyConfig:
    market: Market
    type: StrategyType
    runStrategyTime: time

    stopToLosePercentage: float
    profitPercentage: float
    willingToLose: float
    maxToInvestPerStockPercentage: float
    maxToInvestPerStrategy: float
    orderType: OrderType

    def __init__(self, market: Market, runStrategyTime: time, 
                willingToLose: float, stopToLosePercentage: float, profitPercentage: float,
                maxToInvestPerStockPercentage: float,
                maxToInvestPerStrategy: float,
                orderType: OrderType) -> None:
        self.market = market
        self.runStrategyTime = runStrategyTime
        self.stopToLosePercentage = stopToLosePercentage
        self.profitPercentage = profitPercentage
        self.willingToLose = willingToLose
        self.maxToInvestPerStockPercentage = maxToInvestPerStockPercentage
        self.maxToInvestPerStrategy = maxToInvestPerStrategy
        self.orderType = orderType

    def nextProcessDatetime(self, now: datetime) -> datetime:
        pass

    def nextAction(self, now: datetime) -> StrategyAction:
        pass