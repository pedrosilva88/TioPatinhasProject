from configs.models import TioPatinhasConfigs
from typing import List
from pytz import timezone
from country_config.models import Country, Market
from datetime import datetime, date, time, timedelta

def getMarketFor(country: Country) -> Market:
    if country == Country.USA:
        return Market(country= Country.USA,
                        timezone= USATimezone,
                        openTime= USAOpenTime,
                        closeTime= USACloseTime)
    if country == Country.UK:
        return Market(country= Country.UK,
                            timezone= UKTimezone,
                            openTime= UKOpenTime,
                            closeTime= UKCloseTime)
    if country == Country.HongKong:
        return Market(country= Country.HongKong,
                        timezone= HKTimezone,
                        openTime= HKOpenTime,
                        closeTime= HKCloseTime)

def getCurrentMarket(markets: List[Market]) -> Market:
    localTimezone = TioPatinhasConfigs().timezone
    currentDate = datetime.now().astimezone(localTimezone)
    markets.sort(key=lambda x: x.openTime.astimezone(localTimezone))
    currentMarket = markets[0]

    for item in markets:
        if item.openTime.astimezone(localTimezone) > currentDate:
            currentMarket = item
            break

    return currentMarket

def updateMarketConfigForNextDay(previousMarket: Market) -> Market:
    nextday = tomorrow
    return Market(country=previousMarket.country,
                    timezone=previousMarket.timezone,
                    openTime=datetime.combine(nextday,previousMarket.openTime.time()),
                    closeTime=datetime.combine(nextday,previousMarket.closeTime.time()))

# Constants

# General
tomorrow = date.today()+timedelta(days= 1)

# USA
USATimezone = timezone('America/New_York')
USAOpenTime = datetime.combine(date.today(),time(9,30))
USACloseTime = datetime.combine(date.today(),time(15,30))

# UK
UKTimezone = timezone('Europe/London')
UKOpenTime = datetime.combine(date.today(),time(8,0))
UKCloseTime = datetime.combine(date.today(),time(13,10))

# HongKong
HKTimezone = timezone('Asia/Hong_Kong')
HKOpenTime = datetime.combine(date.today(),time(9,10))
HKCloseTime = datetime.combine(date.today(),time(14,10))