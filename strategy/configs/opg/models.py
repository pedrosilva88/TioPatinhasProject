class StrategyOPGConfig(StrategyConfig):
    strategyValidPeriod: datetime
    strategyMaxTime: datetime
    minGap: int
    maxGap: int
    maxLastGap: int = 9
    gapProfitPercentage: float
    averageVolumePercentage: float #= 1.2 # This means 120% above

    def __init__(self, startRunningStrategy: datetime = None, strategyValidPeriod: datetime = None, strategyMaxTime: datetime = None,
                        minGap: int = None, maxGap: int = None, maxLastGap: int = None, gapProfitPercentage: float = None,
                        willingToLose: float = None, stopToLosePercentage: float = None, profitPercentage: float = None,
                        maxToInvestPerStockPercentage: float = None, averageVolumePercentage: float = None, 
                        minRSI: float = None, maxRSI: float = None):
        self.startRunningStrategy = startRunningStrategy
        self.strategyValidPeriod = strategyValidPeriod
        self.strategyMaxTime = strategyMaxTime
        self.minGap = minGap
        self.maxGap = maxGap
        self.maxLastGap = maxLastGap
        self.gapProfitPercentage = gapProfitPercentage
        self.willingToLose = willingToLose
        self.stopToLosePercentage = stopToLosePercentage
        self.maxToInvestPerStockPercentage = maxToInvestPerStockPercentage
        self.averageVolumePercentage = averageVolumePercentage
        self.profitPercentage = profitPercentage
        self.minRSI = minRSI
        self.maxRSI = maxRSI