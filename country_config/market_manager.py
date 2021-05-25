from typing import List
from pytz import timezone
from country_config.models import Country, Market
from datetime import datetime, date, time, timedelta

class MarketManager:
    def getMarketFor(country: Country) -> Market:
        if country == Country.USA:
            return Market(country= Country.USA,
                            timezone= Constants.USA.timezone,
                            openTime= Constants.USA.openTime,
                            closeTime= Constants.USA.closeTime)
        if country == Country.UK:
            return Market(country= Country.UK,
                                timezone= Constants.UK.timezone,
                                openTime= Constants.UK.openTime,
                                closeTime= Constants.UK.closeTime)
        if country == Country.HongKong:
            return Market(country= Country.HongKong,
                            timezone= Constants.HK.timezone,
                            openTime= Constants.HK.openTime,
                            closeTime= Constants.HK.closeTime)

    def getCurrentMarket(markets: List[Market], localTimezone: timezone) -> Market:
        currentDate = datetime.now().astimezone(localTimezone)
        markets.sort(key=lambda x: x.openTime.astimezone(localTimezone))
        currentMarket = markets[0]

        for item in markets:
            if item.openTime.astimezone(localTimezone) > currentDate:
                currentMarket = item
                break

        return currentMarket

    def updateMarketConfigForNextDay(previousMarket: Market) -> Market:
        nextday = Constants.General.tomorrow
        return Market(country=previousMarket.country,
                        timezone=previousMarket.timezone,
                        openTime=datetime.combine(nextday,previousMarket.openTime.time()),
                        closeTime=datetime.combine(nextday,previousMarket.closeTime.time()))

class Constants:
    class General:
        tomorrow = date.today()+timedelta(days= 1)    
    class USA:
        timezone = timezone('America/New_York')
        openTime = datetime.combine(date.today(),time(9,30))
        closeTime = datetime.combine(date.today(),time(15,30))
    class UK:
        timezone = timezone('Europe/London')
        openTime = datetime.combine(date.today(),time(8,0))
        closeTime = datetime.combine(date.today(),time(13,10))
    class HK:
        timezone = timezone('Asia/Hong_Kong')
        openTime = datetime.combine(date.today(),time(9,10))
        closeTime = datetime.combine(date.today(),time(14,10))