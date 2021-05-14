from configs.models import TioPatinhasConfigs
from typing import List
from pytz import timezone
from country_config.models import Country, Market
from datetime import datetime, date, time, timedelta

def getMarketFor(country: Country) -> Market:
    if country == Country.USA:
        return Market(country= Country.USA,
                        timezone=timezone('America/New_York'),
                        openTime=datetime.combine(date.today(),time(9,30)),
                        closeTime=datetime.combine(date.today(),time(15,30)))
    if country == Country.UK:
        return Market(country= Country.UK,
                            timezone=timezone('Europe/London'),
                            openTime=datetime.combine(date.today(),time(8,0)),
                            closeTime=datetime.combine(date.today(),time(13,10)))
    if country == Country.HongKong:
        return Market(country= Country.HongKong,
                        timezone=timezone('Asia/Hong_Kong'),
                        openTime=datetime.combine(date.today(),time(9,30)),
                        closeTime=datetime.combine(date.today(),time(14,10)))

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
    nextday = date.today()+timedelta(days= 1)
    return Market(country=previousMarket.country,
                    timezone=previousMarket.timezone,
                    openTime=datetime.combine(nextday,previousMarket.openTime.time()),
                    closeTime=datetime.combine(nextday,previousMarket.closeTime.time()))