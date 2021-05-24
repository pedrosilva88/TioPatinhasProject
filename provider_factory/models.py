from models.base_models import Contract, Event
from configs.models import Provider
from enum import Enum
from typing import Any, List

class Provider(Enum):
    TWS = "TWS"
    Coinbase = "Coinbase"
    Binance = "Binance"

class ProviderConfigs:
    version: str
    tradingMode: str
    user: str
    password: str

    endpoint: str
    port: str
    clientID: str

    connectTimeout: int
    appStartupTime: int
    appTimeout: int
    readOnly: bool

    useController: bool

class ProviderClient:
    provider: Provider
    session: Any

    def downloadHistoricalData(self, stock: Contract, days: int, barSize: str) -> List[Event]:
        pass

class ProviderController:
    provider: Provider
    runner: Any