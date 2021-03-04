from strategy import StrategyData, StrategyResult, StrategyResultType

def logExecutionTicker(data: StrategyData, result: StrategyResult):
    print("⭐️[%i/%i %i:%i:%i] Ticker %s: %s / Last(%.2f) Open(%.2f) Close(%.2f) ⭐️" % (data.datetime.day, 
                                                                                    data.datetime.month, 
                                                                                    data.datetime.hour, 
                                                                                    data.datetime.minute, 
                                                                                    data.datetime.second, 
                                                                                    data.ticker.symbol,
                                                                                    result.type,
                                                                                    data.lastPrice,
                                                                                    data.openPrice,
                                                                                    data.ystdClosePrice))