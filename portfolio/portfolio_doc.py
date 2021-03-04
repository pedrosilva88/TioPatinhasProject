

# Preciso de olhar po Bid/Ask para definir o lmtPrice que coloco na Order

# Deixar de ter MarketOrders e passar a ter LmtPrice Order

# Atualizar o LmtPrice de uma Order olhando para o LastBid & LastAsk

# Ter uma lógica para escolher o ECN em vez de ser o SMART. ne que seja para já o BYX

# Usar o cancelMktData para deixar de escutar uma derterminada stock

# Stock(ticker, "SMART", "USD") Esta parte do "SMART" e "USD" tem que ser mais dinamica

# Quando tiver a trabalhar em multiplos paises devo usar um logica de timeout para o script "descansar" e acordar quando for necessario

# Ter um bot ligado ao telegram para me dar relatorios, estado actual de orders/positions, cacelar orders. 

# Tenho que conseguir calcular as comissoes que cada order me vai custar. Isto tudo antes de executar a order. Pode não compensar executar a order.





# 
# 
# ib.reqPositions()
# ib.reqPositionsAsync
# cancelPositions

### ib.reqPositions ###
[Position(account='DU3352788', contract=Stock(conId=75197507, symbol='EXPR', exchange='NYSE', currency='USD', localSymbol='EXPR', tradingClass='EXPR'), position=5.0, avgCost=2.8), Position(account='DU3352788', contract=Stock(conId=47527197, symbol='EVK', exchange='NASDAQ', currency='USD', localSymbol='EVK', tradingClass='NMS'), position=0.0, avgCost=0.0), Position(account='DU3352788', contract=Stock(conId=47527197, symbol='EVK', exchange='NASDAQ', currency='USD', localSymbol='EVK', tradingClass='NMS'), position=0.0, avgCost=0.0), Position(account='DU3352788', contract=Stock(conId=47527197, symbol='EVK', exchange='NASDAQ', currency='USD', localSymbol='EVK', tradingClass='NMS'), position=-5.0, avgCost=3.29), Position(account='DU3352788', contract=Stock(conId=75197507, symbol='EXPR', exchange='NYSE', currency='USD', localSymbol='EXPR', tradingClass='EXPR'), position=5.0, avgCost=2.828), Position(account='DU3352788', contract=Stock(conId=47527197, symbol='EVK', exchange='NASDAQ', currency='USD', localSymbol='EVK', tradingClass='NMS'), position=-5.0, avgCost=3.2541642)]

### ib.positions() ###
[Position(account='DU3352788', contract=Stock(conId=75197507, symbol='EXPR', exchange='NYSE', currency='USD', localSymbol='EXPR', tradingClass='EXPR'), position=5.0, avgCost=2.828), Position(account='DU3352788', contract=Stock(conId=47527197, symbol='EVK', exchange='NASDAQ', currency='USD', localSymbol='EVK', tradingClass='NMS'), position=-5.0, avgCost=3.2541642)]

########## cancelMktData ###########

# ib.reqAccountSummaryAsync
# ib.reqAccountSummary
# cancelAccountSummary
#
# ib.reqAccountUpdates
# ib.reqAccountUpdatesAsync

# ib.reqCurrentTime



# ib.reqAllOpenOrders
# ib.reqAllOpenOrdersAsync
# ib.reqOpenOrders
# ib.reqOpenOrdersAsync
# placeOrder
# cancelOrder

[Trade(contract=Stock(conId=81330131, symbol='KMF', right='?', exchange='SMART', currency='USD', localSymbol='KMF', tradingClass='KMF'), 
       order=Order(permId=852390126, action='SELL', totalQuantity=4.0, orderType='LMT', 
                     lmtPrice=7.89, auxPrice=0.0, tif='DAY', ocaType=3, orderRef='MktDepth', 
                     trailStopPrice=5.34, openClose='', eTradeOnly=False, firmQuoteOnly=False, volatilityType=0, deltaNeutralOrderType='None', 
                     referencePriceType=0, account='DU3352788', clearingIntent='IB', adjustedOrderType='None', cashQty=0.0, dontUseAutoPriceForHedge=True), 
       orderStatus=OrderStatus(orderId=0, status='Submitted', filled=0.0, remaining=4.0, avgFillPrice=0.0, 
                                   permId=852390126, parentId=0, lastFillPrice=0.0, clientId=0, whyHeld='', mktCapPrice=0.0), 
       fills=[], 
       log=[TradeLogEntry(time=datetime.datetime(2021, 3, 2, 17, 59, 8, 722816, tzinfo=datetime.timezone.utc), status='Submitted', message='')]), 
Trade(contract=Stock(conId=12442, symbol='SAN', right='?', exchange='SMART', currency='USD', localSymbol='SAN', tradingClass='SAN'), 
       order=Order(permId=852390134, action='BUY', totalQuantity=5.0, orderType='LMT', lmtPrice=1.8, auxPrice=0.0, tif='DAY', ocaType=3, 
                     orderRef='MktDepth', trailStopPrice=4.5, openClose='', eTradeOnly=False, firmQuoteOnly=False, volatilityType=0, deltaNeutralOrderType='None', 
                     referencePriceType=0, account='DU3352788', clearingIntent='IB', adjustedOrderType='None', cashQty=0.0, dontUseAutoPriceForHedge=True), 
       orderStatus=OrderStatus(orderId=0, status='Submitted', filled=0.0, remaining=5.0, avgFillPrice=0.0, permId=852390134, parentId=0, lastFillPrice=0.0, clientId=0, 
                                   whyHeld='', mktCapPrice=0.0), 
       fills=[], 
       log=[TradeLogEntry(time=datetime.datetime(2021, 3, 2, 17, 59, 8, 723549, tzinfo=datetime.timezone.utc), status='Submitted', message='')])]



[Trade(contract=Stock(conId=27021698, symbol='OGZD', right='?', exchange='SMART', currency='USD', localSymbol='OGZD', tradingClass='OGZD'), 
       order=Order(permId=1438599791, action='BUY', orderType='MKT', lmtPrice=6.078, auxPrice=0.0, tif='DAY', ocaType=3, orderRef='MktDepth', trailStopPrice=7.078, openClose='', 
                     volatilityType=0, deltaNeutralOrderType='None', referencePriceType=0, account='DU3352788', clearingIntent='IB', cashQty=0.0, dontUseAutoPriceForHedge=True, 
                     filledQuantity=4.0, refFuturesConId=2147483647, shareholder='Not an insider or substantial shareholder'), 
       orderStatus=OrderStatus(orderId=0, status='Filled', filled=0, remaining=0, avgFillPrice=0.0, permId=0, parentId=0, lastFillPrice=0.0, clientId=0, whyHeld='', mktCapPrice=0.0), 
       fills=[Fill(contract=Stock(conId=27021698, symbol='OGZD', right='?', exchange='SMART', currency='USD', localSymbol='OGZD', tradingClass='OGZD'), 
                     execution=Execution(execId='0000e859.603f1a4b.01.01', time=datetime.datetime(2021, 3, 3, 8, 49, 29, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', 
                                          exchange='LSEIOB1', side='BOT', shares=4.0, price=6.074, permId=1438599791, clientId=0, orderId=0, liquidation=0, cumQty=4.0, avgPrice=6.074, 
                                          orderRef='MktDepth', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), 
                     commissionReport=CommissionReport(execId='0000e859.603f1a4b.01.01', commission=5.0, currency='USD', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), 
                     time=datetime.datetime(2021, 3, 3, 8, 49, 29, tzinfo=datetime.timezone.utc))], 
       log=[TradeLogEntry(time=datetime.datetime(2021, 3, 3, 8, 49, 29, tzinfo=datetime.timezone.utc), status='Filled', message='Fill 4.0@6.074')]), 

Trade(contract=Stock(conId=27021698, symbol='OGZD', right='?', exchange='SMART', currency='USD', localSymbol='OGZD', tradingClass='OGZD'), 
       order=Order(permId=1438599793, action='SELL', totalQuantity=4.0, orderType='LMT', lmtPrice=9.566, auxPrice=0.0, tif='DAY', ocaGroup='1438599791', ocaType=3, orderRef='MktDepth', 
                     trailStopPrice=7.078, openClose='', eTradeOnly=False, firmQuoteOnly=False, volatilityType=0, deltaNeutralOrderType='None', referencePriceType=0, account='DU3352788', 
                     clearingIntent='IB', adjustedOrderType='None', cashQty=0.0, dontUseAutoPriceForHedge=True), 
       orderStatus=OrderStatus(orderId=0, status='PreSubmitted', filled=0.0, remaining=4.0, avgFillPrice=0.0, permId=1438599793, parentId=0, lastFillPrice=0.0, clientId=0, whyHeld='', mktCapPrice=0.0), 
       fills=[], 
       log=[TradeLogEntry(time=datetime.datetime(2021, 3, 3, 8, 52, 23, 196144, tzinfo=datetime.timezone.utc), status='PreSubmitted', message='')]), 
Trade(contract=Stock(conId=27021698, symbol='OGZD', right='?', exchange='SMART', currency='USD', localSymbol='OGZD', tradingClass='OGZD'), 
       order=Order(permId=1438599792, action='SELL', totalQuantity=4.0, orderType='STP', lmtPrice=0.0, auxPrice=2.1, tif='DAY', ocaGroup='1438599791', ocaType=3, orderRef='MktDepth', 
                     trailStopPrice=2.1, openClose='', eTradeOnly=False, firmQuoteOnly=False, volatilityType=0, deltaNeutralOrderType='None', referencePriceType=0, 
                     account='DU3352788', clearingIntent='IB', adjustedOrderType='None', cashQty=0.0, dontUseAutoPriceForHedge=True), 
       orderStatus=OrderStatus(orderId=0, status='PreSubmitted', filled=0.0, remaining=4.0, avgFillPrice=0.0, permId=1438599792, parentId=0, lastFillPrice=0.0, clientId=0, whyHeld='trigger', mktCapPrice=0.0), fills=[], log=[TradeLogEntry(time=datetime.datetime(2021, 3, 3, 8, 52, 23, 196889, tzinfo=datetime.timezone.utc), status='PreSubmitted', message='')])]


### ib.reqAllOpenOrders ###
[Order(permId=1038919788, 
        action='SELL', 
        totalQuantity=5.0, 
        orderType='LMT', 
        lmtPrice=4.54, 
        auxPrice=0.0, tif='DAY', ocaType=3, orderRef='MktDepth', 
        trailStopPrice=6.5, openClose='', eTradeOnly=False, firmQuoteOnly=False, volatilityType=0, deltaNeutralOrderType='None', 
        referencePriceType=0, account='DU3352788', clearingIntent='IB', adjustedOrderType='None', cashQty=0.0, dontUseAutoPriceForHedge=True),
 Order(permId=1038919793, 
        action='BUY', 
        totalQuantity=5.0, 
        orderType='LMT', 
        lmtPrice=1.22, 
        auxPrice=0.0, tif='DAY', ocaType=3, orderRef='MktDepth', trailStopPrice=3.73, openClose='', eTradeOnly=False, firmQuoteOnly=False, volatilityType=0, deltaNeutralOrderType='None', referencePriceType=0, account='DU3352788', clearingIntent='IB', adjustedOrderType='None', cashQty=0.0, dontUseAutoPriceForHedge=True)]




       Trade(contract=Stock(conId=27021698, symbol='OGZD', right='?', exchange='SMART', currency='USD', localSymbol='OGZD', tradingClass='OGZD'), 
              order=Order(permId=1438599793, action='SELL', totalQuantity=4.0, orderType='LMT', lmtPrice=9.566, auxPrice=0.0, tif='DAY', ocaGroup='1438599791', ocaType=3, orderRef='MktDepth', trailStopPrice=7.078, openClose='', eTradeOnly=False, firmQuoteOnly=False, volatilityType=0, deltaNeutralOrderType='None', referencePriceType=0, account='DU3352788', clearingIntent='IB', adjustedOrderType='None', cashQty=0.0, dontUseAutoPriceForHedge=True), orderStatus=OrderStatus(orderId=0, status='PreSubmitted', filled=0.0, remaining=4.0, avgFillPrice=0.0, permId=1438599793, parentId=0, lastFillPrice=0.0, clientId=0, whyHeld='', mktCapPrice=0.0), fills=[], log=[TradeLogEntry(time=datetime.datetime(2021, 3, 3, 10, 1, 49, 980829, tzinfo=datetime.timezone.utc), status='PreSubmitted', message='')]), 
       Trade(contract=Stock(conId=27021698, symbol='OGZD', right='?', exchange='SMART', currency='USD', localSymbol='OGZD', tradingClass='OGZD'), 
              order=Order(permId=1438599792, action='SELL', totalQuantity=4.0, orderType='STP', lmtPrice=0.0, auxPrice=2.1, tif='DAY', ocaGroup='1438599791', ocaType=3, orderRef='MktDepth', trailStopPrice=2.1, openClose='', eTradeOnly=False, firmQuoteOnly=False, volatilityType=0, deltaNeutralOrderType='None', referencePriceType=0, account='DU3352788', clearingIntent='IB', adjustedOrderType='None', cashQty=0.0, dontUseAutoPriceForHedge=True), orderStatus=OrderStatus(orderId=0, status='PreSubmitted', filled=0.0, remaining=4.0, avgFillPrice=0.0, permId=1438599792, parentId=0, lastFillPrice=0.0, clientId=0, whyHeld='trigger', mktCapPrice=0.0), fills=[], log=[TradeLogEntry(time=datetime.datetime(2021, 3, 3, 10, 1, 49, 980829, tzinfo=datetime.timezone.utc), status='PreSubmitted', message='')])]




2021-03-03 14:30:39.224173+00:00
Type(OrderType.Short) Size(2) Price(119.45) ProfitPrice(119.28) StopLoss(125.42)
Result for GME: Sell 💚

2021-03-03 14:30:39.224173+00:00
The GAP is poor or don't exist. Do nothing! 1.38 - -0.21 ( 15.23 - 15.44 )
Result for M: DoNothing 💚

2021-03-03 14:30:39.224173+00:00
The GAP is poor or don't exist. Do nothing! 0.75 - -0.02 ( 2.65 - 2.67 )
Result for EXPR: DoNothing 💚

2021-03-03 14:30:34.040289+00:00
The GAP is poor or don't exist. Do nothing! 1.23 - -0.34 ( 27.73 - 28.07 )
Result for BBBY: DoNothing 💚

2021-03-03 14:30:39.222953+00:00
The GAP is poor or don't exist. Do nothing! 0.98 - 0.13 ( 13.23 - 13.10 )
Result for CLNE: DoNothing 💚

2021-03-03 14:30:39.224173+00:00
The GAP is poor or don't exist. Do nothing! 0.55 - 0.71 ( 130.11 - 129.40 )
Result for WMT: DoNothing 💚

2021-03-03 14:30:39.224173+00:00
The GAP is poor or don't exist. Do nothing! 0.04 - 0.01 ( 25.73 - 25.72 )
Result for GPS: DoNothing 💚

2021-03-03 14:30:37.274656+00:00
The GAP is poor or don't exist. Do nothing! 0.63 - 0.30 ( 47.44 - 47.14 )
Result for WBA: DoNothing 💚

2021-03-03 14:30:39.224173+00:00
The GAP is poor or don't exist. Do nothing! 0.77 - 0.51 ( 66.21 - 65.70 )
Result for TJX: DoNothing 💚

2021-03-03 14:30:37.274656+00:00
The GAP is poor or don't exist. Do nothing! 0.81 - 0.08 ( 9.91 - 9.83 )
Result for LOTZ: DoNothing 💚

2021-03-03 14:30:39.224173+00:00
The GAP is poor or don't exist. Do nothing! 0.24 - 0.26 ( 107.20 - 106.94 )
Result for SBUX: DoNothing 💚

2021-03-03 14:30:39.224173+00:00
The GAP is poor or don't exist. Do nothing! 22.48 - -4.05 ( 18.02 - 22.07 )
Result for MIK: DoNothing 💚

2021-03-03 14:30:39.224173+00:00
Type(OrderType.Long) Size(8) Price(35.40) ProfitPrice(36.01) StopLoss(33.63)
Result for JWN: Buy 💔 (Earnings) # ainda nao terminou

2021-03-03 14:30:41.147125+00:00
Type(OrderType.Short) Size(13) Price(21.93) ProfitPrice(22.85) StopLoss(23.03)
Result for VUZI: Sell 💚

2021-03-03 14:30:43.152379+00:00
The GAP is poor or don't exist. Do nothing! 0.84 - -0.48 ( 57.36 - 57.84 )
Result for KSS: DoNothing 💚

--------

[AccountValue(account='DU3352788', tag='AccountCode', value='DU3352788', currency='', modelCode=''), 
AccountValue(account='DU3352788', tag='AccountOrGroup', value='DU3352788', currency='BASE', modelCode=''), 
ccountValue(account='DU3352788', tag='AccountOrGroup', value='DU3352788', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='AccountOrGroup', value='DU3352788', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='AccountReady', value='true', currency='', modelCode=''), 
AccountValue(account='DU3352788', tag='AccountType', value='INDIVIDUAL', currency='', modelCode=''),
 AccountValue(account='DU3352788', tag='AccruedCash', value='0.00', currency='BASE', modelCode=''), 
 AccountValue(account='DU3352788', tag='AccruedCash', value='0.00', currency='EUR', modelCode=''), 
 AccountValue(account='DU3352788', tag='AccruedCash', value='0.00', currency='USD', modelCode=''), 
 AccountValue(account='DU3352788', tag='AccruedDividend', value='0.00', currency='EUR', modelCode=''), 
 AccountValue(account='DU3352788', tag='AvailableFunds', value='379.59', currency='EUR', modelCode=''), 
 AccountValue(account='DU3352788', tag='Billable', value='0.00', currency='EUR', modelCode=''), 
 AccountValue(account='DU3352788', tag='BuyingPower', value='2530.60', currency='EUR', modelCode=''), 
 AccountValue(account='DU3352788', tag='CashBalance', value='2772.8573', currency='BASE', modelCode=''), 
 AccountValue(account='DU3352788', tag='CashBalance', value='2500.00', currency='EUR', modelCode=''),
  AccountValue(account='DU3352788', tag='CashBalance', value='328.1792', currency='USD', modelCode=''), 
  AccountValue(account='DU3352788', tag='CorporateBondValue', value='0.00', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='CorporateBondValue', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='CorporateBondValue', value='0.00', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='Currency', value='BASE', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='Currency', value='EUR', currency='EUR', modelCode=''), 
ccountValue(account='DU3352788', tag='Currency', value='USD', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='Cushion', value='0.833218', currency='', modelCode=''), 
ccountValue(account='DU3352788', tag='EquityWithLoanValue', value='2379.60', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='ExcessLiquidity', value='1982.72', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='ExchangeRate', value='1.00', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='ExchangeRate', value='1.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='ExchangeRate', value='0.831428', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='FullAvailableFunds', value='379.59', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='FullExcessLiquidity', value='1982.72', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='FullInitMarginReq', value='2000.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='FullMaintMarginReq', value='396.87', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='FundValue', value='0.00', currency='BASE', modelCode=''),
AccountValue(account='DU3352788', tag='FundValue', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='FundValue', value='0.00', currency='USD', modelCode=''),
AccountValue(account='DU3352788', tag='FutureOptionValue', value='0.00', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='FutureOptionValue', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='FutureOptionValue', value='0.00', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='FuturesPNL', value='0.00', currency='BASE', modelCode=''),
AccountValue(account='DU3352788', tag='FuturesPNL', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='FuturesPNL', value='0.00', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='FxCashBalance', value='0.00', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='FxCashBalance', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='FxCashBalance', value='0.00', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='GrossPositionValue', value='393.26', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='Guarantee', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='IndianStockHaircut', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='InitMarginReq', value='2000.00', currency='EUR', modelCode=''), 

AccountValue(account='DU3352788', tag='Leverage-S', value='0.17', currency='', modelCode=''), 
AccountValue(account='DU3352788', tag='LookAheadAvailableFunds', value='379.59', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='LookAheadExcessLiquidity', value='1982.72', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='LookAheadInitMarginReq', value='2000.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='LookAheadMaintMarginReq', value='396.87', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='LookAheadNextChange', value='1614891600', currency='', modelCode=''), 
AccountValue(account='DU3352788', tag='MaintMarginReq', value='396.87', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='MoneyMarketFundValue', value='0.00', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='MoneyMarketFundValue', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='MoneyMarketFundValue', value='0.00', currency='USD', modelCode=''), 

AccountValue(account='DU3352788', tag='NLVAndMarginInReview', value='false', currency='', modelCode=''), 

AccountValue(account='DU3352788', tag='NetLiquidation', value='2379.60', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='NetLiquidationByCurrency', value='2379.5966', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='NetLiquidationByCurrency', value='2500.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='NetLiquidationByCurrency', value='-144.8151', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='NetLiquidationUncertainty', value='0.00', currency='EUR', modelCode=''), 

AccountValue(account='DU3352788', tag='PhysicalCertificateValue', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='PostExpirationExcess', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='PostExpirationMargin', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='RealCurrency', value='BASE', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='RealCurrency', value='EUR', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='RealCurrency', value='USD', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='RealizedPnL', value='-8.18', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='RealizedPnL', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='RealizedPnL', value='-9.84', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='SegmentTitle-S', value='CFD', currency='', modelCode=''), 
AccountValue(account='DU3352788', tag='StockMarketValue', value='-393.26', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='StockMarketValue', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='StockMarketValue', value='-472.99', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='TBillValue', value='0.00', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='TBillValue', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='TBillValue', value='0.00', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='TBondValue', value='0.00', currency='BASE', modelCode=''), A
ccountValue(account='DU3352788', tag='TBondValue', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='TBondValue', value='0.00', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='TotalCashBalance', value='2772.8573', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='TotalCashBalance', value='2500.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='TotalCashBalance', value='328.1792', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='TotalCashValue', value='2772.86', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='TotalDebitCardPendingCharges', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='TradingType-S', value='STKNOPT', currency='', modelCode=''), 
AccountValue(account='DU3352788', tag='UnrealizedPnL', value='-1.04', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='UnrealizedPnL', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='UnrealizedPnL', value='-1.24', currency='USD', modelCode=''), 
