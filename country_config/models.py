from datetime import datetime, timezone as tz
from enum import Enum

class Country(Enum):
    USA = 1
    UK = 2
    HongKong = 3
    Japan = 4
    Germany = 5
    Spain = 6

    @property
    def code(self):
        if self == Country.USA: return "US"
        if self == Country.UK: return "UK"
        if self == Country.HongKong: return "HK"
        if self == Country.Japan: return "JPN"
        if self == Country.Germany: return "DE"
        if self == Country.Spain: return "ES"

    @property
    def currency(self):
        if self == Country.USA: return "USD"
        if self == Country.UK: return "GBP"
        if self == Country.HongKong: return "???"
        if self == Country.Japan: return "???"
        if self == Country.Germany: return "EUR"
        if self == Country.Spain: return "EUR"

class Market():
    country: Country
    timezone: tz
    openTime: datetime
    closeTime: datetime

    def __init__(self, country: Country, timezone: tz, openTime: datetime, closeTime: datetime):
        self.country = country
        self.timezone = timezone
        self.openTime = timezone.localize(openTime, is_dst=None)
        self.closeTime = timezone.localize(closeTime, is_dst=None)