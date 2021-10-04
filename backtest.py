from backtest.backtest_impulse_pullback_module import BacktestImpulsePullbackModule
from backtest.backtest_stoch_diverge_module import BacktestStochDivergeModule
from strategy.configs.models import StrategyType
from backtest.configs.models import BacktestConfigs
from backtest.backtest_zigzag_module import BacktestZigZagModule
from backtest.backtest_module import BacktestModule

def createBacktestModule() -> BacktestModule:
    config = BacktestConfigs()
    if config.strategyType == StrategyType.zigzag:
        return BacktestZigZagModule()
    elif config.strategyType == StrategyType.stoch_diverge:
        return BacktestStochDivergeModule()
    elif config.strategyType == StrategyType.impulse_pullback:
        return BacktestImpulsePullbackModule()
    return None


if __name__ == '__main__':
    try:
        module = createBacktestModule()
        module.runBacktest()
    except (KeyboardInterrupt, SystemExit):
        None


# from backtest.scanner.scanner_manager import BacktestScannerManager
# from scanner import Scanner
# pathDownload = "backtest/scanner/Data/CSV/TWS/impulse_pullback/US/scan_to_download.csv"
# pathDownloadPremium = "backtest/scanner/Data/CSV/TWS/impulse_pullback/US/scan_to_download_premium.csv"
# stocksDownload = Scanner.contratcsFrom(pathDownload)
# stocksDownloadPremium = Scanner.contratcsFrom(pathDownloadPremium)

# inDownloadArray = []
# outDownloadArray = []
# for item in stocksDownload:
#     exist = False
#     for index, copy in enumerate(stocksDownloadPremium):
#         # if index > 780 and index < 790:
#         #     print(copy.symbol, len(copy.symbol))
#         if copy.symbol == item.symbol:
#             exist = True
#             break
#     # print("")
#     if exist:
#         inDownloadArray.append(item)
#     else:
#         outDownloadArray.append(item)
# print(len(inDownloadArray))
# print(len(outDownloadArray))
# for i in outDownloadArray:
#     print("%s,%s,%s" % (i.symbol, i.exchange, i.currency))


# import pandas as pd
# import numpy as np
# import requests
# from termcolor import colored as cl
# from math import floor
# import matplotlib.pyplot as plt

# plt.rcParams['figure.figsize'] = (20, 10)
# plt.style.use('fivethirtyeight')

# def get_historical_data(symbol, start_date = None):
#     api_key = 'Y7V622JJ4L6THQVA'
#     api_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={api_key}&outputsize=full'
#     raw_df = requests.get(api_url).json()
#     df = pd.DataFrame(raw_df[f'Time Series (Daily)']).T
#     df = df.rename(columns = {'1. open': 'open', '2. high': 'high', '3. low': 'low', '4. close': 'Close', '5. adjusted close': 'adj close', '6. volume': 'volume'})
#     for i in df.columns:
#         df[i] = df[i].astype(float)
#     df.index = pd.to_datetime(df.index)
#     df = df.iloc[::-1].drop(['7. dividend amount', '8. split coefficient'], axis = 1)
#     if start_date:
#         df = df[df.index >= start_date]
#     return df

# nflx = get_historical_data('NFLX', '2015-01-01')
# nflx.head()

# def get_stoch(symbol, k_period, d_period, start_date):
#     api_key = 'Y7V622JJ4L6THQVA'
#     url = f'https://www.alphavantage.co/query?function=STOCH&symbol={symbol}&interval=daily&fastkperiod={k_period}&slowdperiod={d_period}&apikey={api_key}'
#     raw = requests.get(url).json()
#     df = pd.DataFrame(raw['Technical Analysis: STOCH']).T.iloc[::-1]
#     df = df[df.index >= start_date]
#     df.index = pd.to_datetime(df.index)
#     df = df.astype(float)
#     return df['SlowK'], df['SlowD']

# nflx['%k'], nflx['%d'] = get_stoch('NFLX', 14, 3, '2015-01-01')
# nflx = nflx.dropna()
# nflx.head()

# def plot_stoch(symbol, price, k, d):
#     ax1 = plt.subplot2grid((9, 1), (0,0), rowspan = 5, colspan = 1)
#     ax2 = plt.subplot2grid((9, 1), (6,0), rowspan = 3, colspan = 1)
#     ax1.plot(price)
#     ax1.set_title(f'{symbol} STOCK PRICE')
#     ax2.plot(k, color = 'deepskyblue', linewidth = 1.5, label = '%K')
#     ax2.plot(d, color = 'orange', linewidth = 1.5, label = '%D')
#     ax2.axhline(80, color = 'black', linewidth = 1, linestyle = '--')
#     ax2.axhline(20, color = 'black', linewidth = 1, linestyle = '--')
#     ax2.set_title(f'{symbol} STOCH')
#     ax2.legend()
#     plt.show()
    
# # plot_stoch('NFLX', nflx['Close'], nflx['%k'], nflx['%d'])

# def implement_stoch_strategy(prices, k, d):    
#     buy_price = []
#     sell_price = []
#     stoch_signal = []
#     signal = 0

#     for i in range(len(prices)):
#         if k[i] < 20 and d[i] < 20 and k[i] < d[i]:
#             if signal != 1:
#                 buy_price.append(prices[i])
#                 sell_price.append(np.nan)
#                 signal = 1
#                 stoch_signal.append(signal)
#             else:
#                 buy_price.append(np.nan)
#                 sell_price.append(np.nan)
#                 stoch_signal.append(0)
#         elif k[i] > 80 and d[i] > 80 and k[i] > d[i]:
#             if signal != -1:
#                 buy_price.append(np.nan)
#                 sell_price.append(prices[i])
#                 signal = -1
#                 stoch_signal.append(signal)
#             else:
#                 buy_price.append(np.nan)
#                 sell_price.append(np.nan)
#                 stoch_signal.append(0)
#         else:
#             buy_price.append(np.nan)
#             sell_price.append(np.nan)
#             stoch_signal.append(0)
            
#     return buy_price, sell_price, stoch_signal
            
# buy_price, sell_price, stoch_signal = implement_stoch_strategy(nflx['Close'], nflx['%k'], nflx['%d'])

# # ax1 = plt.subplot2grid((9, 1), (0,0), rowspan = 5, colspan = 1)
# # ax2 = plt.subplot2grid((9, 1), (6,0), rowspan = 3, colspan = 1)
# # ax1.plot(nflx['Close'], color = 'skyblue', label = 'NFLX')
# # ax1.plot(nflx.index, buy_price, marker = '^', color = 'green', markersize = 10, label = 'BUY SIGNAL', linewidth = 0)
# # ax1.plot(nflx.index, sell_price, marker = 'v', color = 'r', markersize = 10, label = 'SELL SIGNAL', linewidth = 0)
# # ax1.legend(loc = 'upper left')
# # ax1.set_title('NFLX STOCK PRICE')
# # ax2.plot(nflx['%k'], color = 'deepskyblue', linewidth = 1.5, label = '%K')
# # ax2.plot(nflx['%d'], color = 'orange', linewidth = 1.5, label = '%D')
# # ax2.axhline(80, color = 'black', linewidth = 1, linestyle = '--')
# # ax2.axhline(20, color = 'black', linewidth = 1, linestyle = '--')
# # ax2.set_title('NFLX STOCH')
# # ax2.legend()
# # plt.show()

# position = []
# for i in range(len(stoch_signal)):
#     if stoch_signal[i] > 1:
#         position.append(0)
#     else:
#         position.append(1)
        
# for i in range(len(nflx['Close'])):
#     if stoch_signal[i] == 1:
#         position[i] = 1
#     elif stoch_signal[i] == -1:
#         position[i] = 0
#     else:
#         position[i] = position[i-1]
        
# k = nflx['%k']
# d = nflx['%d']
# close_price = nflx['Close']
# stoch_signal = pd.DataFrame(stoch_signal).rename(columns = {0:'stoch_signal'}).set_index(nflx.index)
# position = pd.DataFrame(position).rename(columns = {0:'stoch_position'}).set_index(nflx.index)

# frames = [close_price, k, d, stoch_signal, position]
# strategy = pd.concat(frames, join = 'inner', axis = 1)

# #strategy.tail()

# print(strategy)

# nflx_ret = pd.DataFrame(np.diff(nflx['Close'])).rename(columns = {0:'returns'})
# stoch_strategy_ret = []

# print(nflx_ret)

# for i in range(len(nflx_ret)):
#     try:
#         returns = nflx_ret['returns'][i]*strategy['stoch_position'][i]
#         stoch_strategy_ret.append(returns)
#     except:
#         pass
# #print(stoch_strategy_ret)
# stoch_strategy_ret_df = pd.DataFrame(stoch_strategy_ret).rename(columns = {0:'stoch_returns'})

# investment_value = 10000
# number_of_stocks = floor(investment_value/nflx['Close'][-1])
# stoch_investment_ret = []

# for i in range(len(stoch_strategy_ret_df['stoch_returns'])):
#     returns = number_of_stocks*stoch_strategy_ret_df['stoch_returns'][i]
#     stoch_investment_ret.append(returns)

# stoch_investment_ret_df = pd.DataFrame(stoch_investment_ret).rename(columns = {0:'investment_returns'})
# total_investment_ret = round(sum(stoch_investment_ret_df['investment_returns']), 2)
# profit_percentage = floor((total_investment_ret/investment_value)*100)
# print(cl('Profit gained from the STOCH strategy by investing $10k in NFLX : {}'.format(total_investment_ret), attrs = ['bold']))
# print(cl('Profit percentage of the STOCH strategy : {}%'.format(profit_percentage), attrs = ['bold']))

# def get_benchmark(start_date, investment_value):
#     spy = get_historical_data('SPY', start_date)['Close']
#     benchmark = pd.DataFrame(np.diff(spy)).rename(columns = {0:'benchmark_returns'})
    
#     investment_value = investment_value
#     number_of_stocks = floor(investment_value/spy[-1])
#     benchmark_investment_ret = []
    
#     for i in range(len(benchmark['benchmark_returns'])):
#         returns = number_of_stocks*benchmark['benchmark_returns'][i]
#         benchmark_investment_ret.append(returns)

#     benchmark_investment_ret_df = pd.DataFrame(benchmark_investment_ret).rename(columns = {0:'investment_returns'})
#     return benchmark_investment_ret_df

# benchmark = get_benchmark('2015-01-01', 10000)
# investment_value = 10000
# total_benchmark_investment_ret = round(sum(benchmark['investment_returns']), 2)
# benchmark_profit_percentage = floor((total_benchmark_investment_ret/investment_value)*100)
# print(cl('Benchmark profit by investing $10k : {}'.format(total_benchmark_investment_ret), attrs = ['bold']))
# print(cl('Benchmark Profit percentage : {}%'.format(benchmark_profit_percentage), attrs = ['bold']))
# print(cl('STOCH Strategy profit is {}% higher than the Benchmark Profit'.format(profit_percentage - benchmark_profit_percentage), attrs = ['bold']))

# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# import pandas_datareader as web
# from strategy.historical_data import *
# from provider_factory.provider_module import ProviderModule
# from scanner import Scanner
# from backtest.download_module.download_module import BacktestDownloadModule
# import matplotlib.dates as mpl_dates
# from mplfinance import plot

# #symbol = 'MSFT'
# #df = web.DataReader(symbol, 'yahoo', '2015-01-01', '2016-01-01')

# config = BacktestConfigs()
# client = ProviderModule.createClient(config.provider, config.providerConfigs)
# client.connect()
# stocks = Scanner.contratcsFrom(config.downloadModel.path)
# stocksData = BacktestDownloadModule.downloadStocks(client, stocks, config.downloadModel.numberOfDays, config.downloadModel.barSize)

# for stockSymbol, (stock, bars) in stocksData.items():
#     ema = HistoricalData.calculateEMA(bars, 50)
#     bollingerBands = HistoricalData.calculateBollingerBands(bars)
#     macd = HistoricalData.calculateMACD(bars)
#     if stock.symbol == "TSLA":
#         ohlc = DataFrame.from_records([event.to_dict() for event in bars], columns=['datetime', 'open', 'high', 'low', 'close'])
#         ohlc.index = pd.DatetimeIndex(ohlc['datetime'])
#         ohlc['datetime'] = pd.to_datetime(ohlc['datetime'])
#         ohlc['datetime'] = ohlc['datetime'].apply(mpl_dates.date2num)
#         ohlc = ohlc.astype(float)

#         import numpy as np

#         items = []

#         for i, event in enumerate(bars):
#             items.append([event.datetime, macd[i]])
#             print(event.datetime, macd[i])
            
#         lista = dict(alines=items, colors=['b'])
#         # plt.title(stock.symbol + ' Bollinger Bands')
#         # plt.xlabel('Days')
#         # plt.ylabel('Closing Prices')
#         # plot(ohlc, type='candlestick', style='charles',
#         #     title='Chart',
#         #     ylabel='Price',
#         #     alines=lista)

#         # plt.plot(bollingerBands["high"], label='Bollinger Up', c='g')
#         # plt.plot(bollingerBands["low"], label='Bollinger Down', c='r')
#         # plt.show()