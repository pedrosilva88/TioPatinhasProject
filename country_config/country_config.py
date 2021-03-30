from enum import Enum
from pytz import timezone
from datetime import datetime, date, time

class CountryKey(Enum):
    USA = 1
    UK = 2
    HongKong = 3
    Japan = 4

    @property
    def code(self):
        if self == CountryKey.USA: return "US"
        if self == CountryKey.UK: return "UK"
        if self == CountryKey.HongKong: return "HK"
        if self == CountryKey.Japan: return "JPN"

class CountryConfig():
    key: CountryKey
    currency: str
    timezone: timezone
    startSetupData: datetime
    exchangeOpenTime: datetime
    closeMarket: datetime
    nItems: int

    def __init__(self, key: CountryKey, timezone: timezone, currency: str, startSetupData: datetime, exchangeOpenTime: datetime, closeMarket: datetime, nItems: int):
        self.key = key
        self.timezone = timezone
        self.currency = currency
        self.startSetupData = timezone.localize(startSetupData, is_dst=None)
        self.exchangeOpenTime = timezone.localize(exchangeOpenTime, is_dst=None)
        self.closeMarket = timezone.localize(closeMarket, is_dst=None)
        self.nItems = nItems

def getConfigFor(key: CountryKey) -> CountryConfig:
    if key == CountryKey.USA:
        return CountryConfig(key=CountryKey.USA,
                            timezone=timezone('America/New_York'),
                            currency="USD",
                            startSetupData=datetime.combine(date.today(),time(8,30)),
                            exchangeOpenTime=datetime.combine(date.today(),time(9,30)),
                            closeMarket=datetime.combine(date.today(),time(14,10)),
                            nItems=82)
    if key == CountryKey.UK:
        return CountryConfig(key=CountryKey.UK,
                            timezone=timezone('Europe/London'),
                            currency="GBP",
                            startSetupData=datetime.combine(date.today(),time(7,30)),
                            exchangeOpenTime=datetime.combine(date.today(),time(8,0)),
                            closeMarket=datetime.combine(date.today(),time(13,10)),
                            nItems= 61)

    if key == CountryKey.HongKong:
        return CountryConfig(key=CountryKey.HongKong,
                            timezone=timezone('Asia/Hong_Kong'),
                            currency="HK",
                            startSetupData=datetime.combine(date.today(),time(8,30)),
                            exchangeOpenTime=datetime.combine(date.today(),time(9,30)),
                            closeMarket=datetime.combine(date.today(),time(14,10)),
                            nItems= 10)

def getCurrentMarketConfig() -> CountryConfig:
    currentDate = datetime.now().astimezone(timezone('UTC'))
    markets = [getConfigFor(CountryKey.USA),
                getConfigFor(CountryKey.UK)]

    markets.sort(key=lambda x: x.startSetupData.astimezone(timezone('UTC')))
    currentMarket = markets[0]
    for item in markets:
        if item.startSetupData.astimezone(timezone('UTC')) > currentDate:
            currentMarket = item
            break

    return currentMarket

def updateMarketConfigForNextDay(previousConfig: CountryConfig) -> CountryConfig:
    return CountryConfig(key=previousConfig.key,
                            timezone=previousConfig.timezone,
                            currency=previousConfig.currency,
                            startSetupData=datetime.combine(date.today()+datetime.timedelta(days= 1),previousConfig.startSetupData.time),
                            exchangeOpenTime=datetime.combine(date.today()+datetime.timedelta(days= 1),previousConfig.exchangeOpenTime.time),
                            closeMarket=datetime.combine(date.today()+datetime.timedelta(days= 1),previousConfig.closeMarket.time),
                            nItems=previousConfig.nItems)
