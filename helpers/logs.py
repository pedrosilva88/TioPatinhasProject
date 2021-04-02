from logging import *
from datetime import *
import sys, os

def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def createLog():
    logger = getLogger("Tio Patinhas")
    logger.setLevel(DEBUG)

    today = datetime.today()
    dirPathMonth = ("logs/%s" % (today.strftime("%B")))
    dirPathDay = ("logs/%s/%d" % (today.strftime("%B"), today.day))
    mkdir(dirPathMonth)
    mkdir(dirPathDay)
    logPath = ("logs/%s/%d/TioPatinhas(%d:%d).log" % (today.strftime("%B"), today.day, today.hour, today.minute))
    with open(logPath, 'w'):
        pass

    # Create handlers
    f_handler = FileHandler(logPath)
    f_handler.setLevel(DEBUG)

    # Create formatters and add it to handlers
    f_format = Formatter('[%(asctime)s] -> %(message)s', "%H:%M:%S")
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
