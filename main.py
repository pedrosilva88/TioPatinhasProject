'''
name="Tio Patinhas"
author="Pedro Silva"
author_email="pedromiguelsilva88@gmail.com"
url="https://github.com/pedrosilva88/TioPatinhasProject"
version="0.1"
description="A Python client library for the Interactive Brokers integration"
long_description = long_description
long_description_content_type="text/markdown"
packages=['vault, strategie, order, screener']
zip_safe=False
'''

import asyncio
import logging
from helpers import logInitTioPatinhas
from island import *

if __name__ == '__main__':
    logInitTioPatinhas()
    asyncio.get_event_loop().set_debug(True)
    #util.logToConsole(logging.DEBUG)
    try:
        island = Island()
        vaultOPG = createOPGRetailVault()
        island.start(vaultOPG)
    except (KeyboardInterrupt, SystemExit):
        island.stop()