from ib_insync import *
from backtest import BackTestModel, BackTestResult, BackTestDownloadModel, downloadStocksData, saveDataInCSVFile
from country_config import CountryConfig, CountryKey, getConfigFor

class BackTestSwing():
    results: [str, [BackTestResult]]
    trades: [str, [str]] = dict()
    cashAvailable = 2000
    countryCode: str
    

def createListOfBackTestModels(stock: Contract, bars: [BarData]) -> [BackTestModel]:
    models = []
    for bar in bars:
        model = BackTestModel(bar.open, bar.close, bar.low, bar.high, bar.close, bar.volume, stock.symbol, bar.date.strftime("%Y-%m-%d %H:%M:%S"), None, None)
        models.append(model)
    return models

if __name__ == '__main__':
    try:
        util.startLoop()
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=16)
        #backtest = BackTestSwing(countryKey=CountryKey.USA)
        path = ("Scanner/Swing/%s/scan.csv" % CountryKey.USA.code)
        countryConfig = getConfigFor(key=CountryKey.USA)
        modelDays = BackTestDownloadModel(path=path, numberOfDays=365, barSize="1 day")
        itemsDictionary = downloadStocksData(ib, modelDays)
        for key, (stock, mBars) in itemsDictionary.items():
            models = createListOfBackTestModels(stock, mBars)
            saveDataInCSVFile(key, models, countryConfig)
            nflx_df = util.df(mBars)
            print(nflx_df.close.rolling(20).mean())
        #backtest.run()
        #backtest.runStockPerformance()
    except (KeyboardInterrupt, SystemExit):
        None