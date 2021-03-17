from pytz import timezone
from datetime import datetime

def utcToLocal(datetime: datetime, timezone:timezone):
    return datetime.astimezone(timezone)


# local = pytz.timezone('America/New_York')
# naive_1 = datetime(2021, 3, 12, 9, 30, 0, 0)
# naive_2 = datetime(2021, 3, 15, 9, 30, 0, 0)
# local_dt_1 = local.localize(naive_1, is_dst=None)
# local_dt_2 = local.localize(naive_1, is_dst=None)
# utc_dt_1 = local_dt_1.astimezone(pytz.utc)
# utc_dt_2 = local_dt_2.astimezone(pytz.utc)

# utc = datetime.utcnow()
# from_zone = tz.gettz('UTC')
# to_zone = tz.gettz('America/New_York')
