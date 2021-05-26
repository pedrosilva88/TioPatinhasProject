from enum import Enum
from typing import Any, List
from models.base_models import Contract, Event

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

    def __init__(self, version: str, tradingMode: str, user: str, password: str, 
                endpoint: str, port: str, clientID: str,
                connectTimeout: int, appStartupTime: int, appTimeout: int, readOnly: bool,
                useController: bool,) -> None:
        self.version = version
        self.tradingMode = tradingMode
        self.user = user
        self.password = password
        self.endpoint = endpoint
        self.port = port
        self.clientID = clientID

        self.connectTimeout = connectTimeout
        self.appStartupTime = appStartupTime
        self.appTimeout = appTimeout
        self.readOnly = readOnly

        self.useController = useController
        

class ProviderClient:
    provider: Provider
    providerConfigs = ProviderConfigs
    session: Any

    def run(self):
        pass

    def connect(self):
        pass

    async def connectAsync(self):
        pass

    def downloadHistoricalData(self, stock: Contract, days: int, barSize: str) -> List[Event]:
        pass

    async def downloadHistoricalDataAsync(self, stock: Contract, days: int, barSize: str) -> List[Event]:
        pass

class ProviderController:
    provider: Provider
    runner: Any