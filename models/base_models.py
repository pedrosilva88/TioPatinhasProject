from country_config.models import Country

class Contract:
    symbol: str
    country: Country
    exchange: str

    def __init__(self, symbol: str, country: Country, exchange: str = "SMART") -> None:
        self.symbol = symbol
        self.country = country
        self.exchange = exchange

    @property
    def currency(self):
        return self.country.currency

class Event:
    contract: Contract
    datetime: datetime

    open: float
    close: float
    high: float
    low: float
    volume: float

    def __init__(self, contract: Contract, 
                        datetime: datetime, 
                        open: float, 
                        close: float, 
                        high: float, 
                        low: float, 
                        volume: float) -> None:
        self.contract = contract
        self.datetime = datetime
        self.open = open
        self.close = close
        self.high = high
        self.low = low
        self.volume = volume