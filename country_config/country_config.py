from enum import Enum
from pytz import timezone
from datetime import datetime, date, time

class CountryKey(Enum):
    USA = 1
    UK = 2
    Japan = 3

class CountryConfig():
    key: CountryKey
    timezone: timezone
    startSetupData: datetime
    exchangeOpenTime: datetime

    def __init__(self, key: CountryKey, timezone: timezone, startSetupData: datetime, exchangeOpenTime: datetime):
        self.key = key
        self.timezone = timezone
        self.startSetupData = timezone.localize(startSetupData, is_dst=None)
        self.exchangeOpenTime = timezone.localize(exchangeOpenTime, is_dst=None)

def getConfigFor(key: CountryKey) -> CountryConfig:
    if key == CountryKey.USA:
        return CountryConfig(key=CountryKey.USA,
                            timezone=timezone('America/New_York'),
                            startSetupData=datetime.combine(date.today(),time(9,15)),
                            exchangeOpenTime=datetime.combine(date.today(),time(9,30)))
    