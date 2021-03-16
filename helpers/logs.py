from logging import *

def createLog():
    logger = getLogger("Tio Patinhas")
    logger.setLevel(DEBUG)

    with open('logs/tioPatinhas.log', 'w'):
        pass

    # Create handlers
    f_handler = FileHandler('logs/tioPatinhas.log')
    f_handler.setLevel(DEBUG)

    # Create formatters and add it to handlers
    f_format = Formatter('%(message)s')
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(f_handler)
    return logger

def getLog() -> Logger:
    return getLogger("Tio Patinhas")

def logExecutionTicker(data, result):
    logger = getLog()
    if (result.type.value == 2 or result.type.value == 3):
        logger.info("⭐️[%i/%i %i:%i:%i] Ticker %s: %s / LastBid(%.2f) LastAsk(%.2f) Open(%.2f) Close(%.2f) ⭐️" % (data.ticker.time.day, 
                                                                                                            data.ticker.time.month, 
                                                                                                            data.ticker.time.hour, 
                                                                                                            data.ticker.time.minute, 
                                                                                                            data.ticker.time.second, 
                                                                                                            data.ticker.contract.symbol,
                                                                                                            result.type,
                                                                                                            data.ticker.bid,
                                                                                                            data.ticker.ask,
                                                                                                            data.ticker.open,
                                                                                                            data.ticker.close))

def logInitTioPatinhas():
    logger = getLog()
    logger.info("\t🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆\n")
    logger.info("\t🦆\t\t\t   🦆\n")
    logger.info("\t🦆   Running Tio Patinhas  🦆\n")
    logger.info("\t🦆\t\t\t   🦆\n")
    logger.info("\t🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆\n")

def log(str: str):
    logger = getLog()
    logger.info(str)