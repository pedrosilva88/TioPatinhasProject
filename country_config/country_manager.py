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