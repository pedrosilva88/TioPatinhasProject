from datetime import time, datetime
from strategy.models import StrategyConfig

class StrategyZigZagConfig(StrategyConfig):
    minRSI: float
    maxRSI: float
    rsiOffsetDays: int
    zigzagSpread: float
    stopToLosePercentage: float
    profitPercentage: float

    runPositionsCheckTime: time

    def __init__(self, runStrategyTime: time,
                        willingToLose: float, stopToLosePercentage: float, profitPercentage: float,
                        maxToInvestPerStockPercentage: float, 
                        minRSI: float, maxRSI: float,
                        rsiOffsetDays: int, zigzagSpread:float,
                        runPositionsCheckTime: time):

        StrategyConfig.__init__(self, runStrategyTime=runStrategyTime, willingToLose=willingToLose, maxToInvestPerStockPercentage=maxToInvestPerStockPercentage)
        self.willingToLose = willingToLose
        self.stopToLosePercentage = stopToLosePercentage
        self.maxToInvestPerStockPercentage = maxToInvestPerStockPercentage
        self.profitPercentage = profitPercentage

        self.minRSI = minRSI
        self.maxRSI = maxRSI
        self.rsiOffsetDays = rsiOffsetDays
        self.zigzagSpread = zigzagSpread

        self.runPositionsCheckTime = runPositionsCheckTime

    def nextProcessDatetime(self, now: datetime) -> datetime:
        # TODO tenho que terminar esta logica. Basicamente tenho que verificar se ainda posso correr esta estrategia hoje, ou validar as positions. 
        # Senao tenho que gerar uma data para o dia seguinte
        return now