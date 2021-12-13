from logging import *
from datetime import *
import logging
import sys, os
import errno

def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def createLog():
    logging.basicConfig(level=logging.WARNING)
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

def createLogReports(report: str):
    logging.basicConfig(level=logging.info)
    logger = getLogger(("Tio Patinhas - Report - %s" % (report)))
    logger.setLevel(DEBUG)

    today = datetime.today()
    dirPathMonth = ("logs/%s" % (today.strftime("%B")))
    dirPathDay = ("logs/%s/%d" % (today.strftime("%B"), today.day))
    dirPathReport = ("logs/%s/%d/%s" % (today.strftime("%B"), today.day, "Reports"))
    mkdir(dirPathMonth)
    mkdir(dirPathDay)
    mkdir(dirPathReport)
    logPath = ("logs/%s/%d/Reports/%s_(%d:%d).log" % (today.strftime("%B"), today.day, report, today.hour, today.minute))
    file = open(logPath, 'w')
    file.truncate(0)
    

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

def logExecutionZigZag(data, result):
    logger = getLog()
    if (result.type.value == 2 or result.type.value == 3):
        logger.info("⭐️ ZigZag %s: %s ⭐️" % (data.contract.symbol,
                                            result.type))

def logInitTioPatinhas():
    log("\t🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆\n")
    log("\t🦆\t\t\t   🦆\n")
    log("\t🦆   Running Tio Patinhas  🦆\n")
    log("\t🦆\t\t\t   🦆\n")
    log("\t🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆\n")

def log(str: str):
    logger = getLog()
    logger.info(str)

def logError(str: str):
    logger = getLog()
    logger.exception(str)

def logCounter(prefix: str, total: int, current: int):
    sys.stdout.write("\t %s: %i/%i \r" % (prefix, current, total) )
    if current <= total-1:
        sys.stdout.flush()
    else:
        print("")

def logImpulsePullbackReport(key: str, line: str):
    logger = getLogger(("Tio Patinhas - Report - %s" % (key)))
    logger.info(line)

def logBounceReport(key: str, line: str):
    logger = getLogger(("Tio Patinhas - Report - %s" % (key)))
    logger.info(line)

def logZigZagReport(key: str, line: str):
    logger = getLogger(("Tio Patinhas - Report - %s" % (key)))
    logger.info(line)

def logStochDivergeReport(key: str, line: str):
    logger = getLogger(("Tio Patinhas - Report - %s" % (key)))
    logger.info(line)