from strategy.historical_data import HistoricalData
from backtest.models.base_models import BacktestDownloadModel

class BacktestDownloadModule:
    model: BacktestDownloadModel
    historicalData: HistoricalData

    def __init__(self, model: BacktestDownloadModel) -> None:
        self.model = model

        