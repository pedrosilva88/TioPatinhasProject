from dataclasses import dataclass
from strategy.configs.models import StrategyConfig
from strategy.models import StrategyData, StrategyResult

@dataclass
class Strategy:
    def run(self, strategyData: StrategyData, strategyConfigs: StrategyConfig) -> StrategyResult:
        """
        Override This method
        """
        pass