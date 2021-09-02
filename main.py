'''
name="Tio Patinhas"
author="Pedro Silva"
author_email="pedromiguelsilva88@gmail.com"
url="https://github.com/pedrosilva88/TioPatinhasProject"
version="1.5"
description="A Python client library for the Interactive Brokers integration"
long_description = long_description
long_description_content_type="text/markdown"
packages=[backtest, configs, country_config, database, earnings_calendar, helpers, 
            island, logs, models, portfolio, provider_factory, scanner, strategy, vaults]
zip_safe=False
'''
import asyncio
from helpers import logInitTioPatinhas, createLog
from island import *
from country_config import *

if __name__ == '__main__':
    asyncio.get_event_loop()
    createLog()
    logInitTioPatinhas()
    try:
        island = Island()
        island.start()
    except (KeyboardInterrupt, SystemExit):
        island.stop()