'''
name="Tio Patinhas"
author="Pedro Silva"
author_email="pedromiguelsilva88@gmail.com"
url="https://github.com/pedrosilva88/TioPatinhasProject"
version="1"
description="A Python client library for the Interactive Brokers integration"
long_description = long_description
long_description_content_type="text/markdown"
packages=['vault, strategy, porfolio, models, scanner, country_config, logs, earnings_calendar, helpers']
zip_safe=False
'''
import sys
import asyncio
import logging
from helpers import logInitTioPatinhas, createLog
from island import *
from country_config import *

if __name__ == '__main__':
    asyncio.get_event_loop().set_debug(True)
    createLog()
    logInitTioPatinhas()
    try:
        island = Island()
        vaultZigZag = VaultZigZag(island)
        island.start(vaultZigZag)
    except (KeyboardInterrupt, SystemExit):
        island.stop()