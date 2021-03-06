from strategy import StrategyData, StrategyResult, StrategyResultType

def logExecutionTicker(data: StrategyData, result: StrategyResult):
    print("⭐️[%i/%i %i:%i:%i] Ticker %s: %s / Last(%.2f) Open(%.2f) Close(%.2f) ⭐️" % (data.ticker.time.day, 
                                                                                    data.ticker.time.month, 
                                                                                    data.ticker.time.hour, 
                                                                                    data.ticker.time.minute, 
                                                                                    data.ticker.time.second, 
                                                                                    data.ticker.contract.symbol,
                                                                                    result.type,
                                                                                    data.ticker.last,
                                                                                    data.ticker.open,
                                                                                    data.ticker.close))

def logInitTioPatinhas():
    print("\t🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆\n")
    print("\t🦆\t\t\t   🦆\n")
    print("\t🦆   Running Tio Patinhas  🦆\n")
    print("\t🦆\t\t\t   🦆\n")
    print("\t🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆 🦆\n")