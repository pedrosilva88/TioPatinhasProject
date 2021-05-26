from country_config.models import Country

def getCountryFromCode(code: str) -> Country:
    if code == 'US':
        return Country.USA
    elif code == 'UK':
        return Country.UK
    elif code == 'HK':
        return Country.HongKong
    elif code == 'JPN':
        return Country.Japan

def getCountryFromCurrency(currency: str) -> Country:
    if currency == 'USD':
        return Country.USA
    elif currency == 'GBP':
        return Country.UK
    elif currency == '???':
        return Country.HongKong
    elif currency == '???':
        return Country.Japan