from logging import *
import sys
from strategy import StrategyData, StrategyResult, StrategyResultType

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

def logExecutionTicker(data: StrategyData, result: StrategyResult):
    logger = getLog()
    if (result.type == StrategyResultType.Buy or result.type == StrategyResultType.Sell):
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
    log("\t🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆\n")
    log("\t🦆\t\t\t   🦆\n")
    log("\t🦆   Running Tio Patinhas  🦆\n")
    log("\t🦆\t\t\t   🦆\n")
    log("\t🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆\n")

def log(str: str):
    logger = getLog()
    logger.info(str)

def logCounter(prefix: str, total: int, current: int):
    sys.stdout.write("\t %s: %i/%i \r" % (prefix, current, total) )
    if current <= total-1:
        sys.stdout.flush()
    else:
        print("")