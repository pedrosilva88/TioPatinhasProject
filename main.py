'''
name="Tio Patinhas"
author="Pedro Silva"
author_email="pedromiguelsilva88@gmail.com"
url="https://github.com/pedrosilva88/TioPatinhasProject"
version="0.1"
description="A Python client library for the Interactive Brokers integration"
long_description = long_description
long_description_content_type="text/markdown"
packages=['vault, strategy, order, scanner']
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
        path = sys.argv[1]
        island = Island(configPath=path)
        vaultOPG = Vault(island)
        island.start(vaultOPG)
    except (KeyboardInterrupt, SystemExit):
        island.stop()