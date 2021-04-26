

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
       fills=[
Fill(contract=Stock(conId=27021698, symbol='OGZD', right='?', exchange='SMART', currency='USD', localSymbol='OGZD', tradingClass='OGZD'), 
                     execution=



Execution(execId='0000e859.603f1a4b.01.01', time=datetime.datetime(2021, 3, 3, 8, 49, 29, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', 
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


[AccountValue(account='DU3352788', tag='AccountCode', value='DU3352788', currency='', modelCode=''), 
AccountValue(account='DU3352788', tag='AccountOrGroup', value='DU3352788', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='AccountOrGroup', value='DU3352788', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='AccountOrGroup', value='DU3352788', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='AccountReady', value='true', currency='', modelCode=''), 
AccountValue(account='DU3352788', tag='AccountType', value='INDIVIDUAL', currency='', modelCode=''), 
AccountValue(account='DU3352788', tag='AccruedCash', value='0.00', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='AccruedCash', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='AccruedCash', value='0.00', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='AccruedDividend', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='AvailableFunds', value='2500.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='AvailableFunds-S', value='2500.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='Billable', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='BuyingPower', value='16666.65', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='CashBalance', value='2499.998', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='CashBalance', value='2499.998', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='CashBalance', value='0.00', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='CorporateBondValue', value='0.00', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='CorporateBondValue', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='CorporateBondValue', value='0.00', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='Currency', value='BASE', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='Currency', value='EUR', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='Currency', value='USD', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='Cushion', value='1', currency='', modelCode=''), 
AccountValue(account='DU3352788', tag='EquityWithLoanValue', value='2500.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='ExcessLiquidity', value='2500.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='ExcessLiquidity-S', value='2500.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='ExchangeRate', value='1.00', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='ExchangeRate', value='1.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='ExchangeRate', value='0.8411137', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='FullAvailableFunds', value='2500.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='FullExcessLiquidity', value='2500.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='FullInitMarginReq', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='FullMaintMarginReq', value='0.00', currency='EUR', modelCode=''), 
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
AccountValue(account='DU3352788', tag='GrossPositionValue', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='Guarantee', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='IndianStockHaircut', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='InitMarginReq', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='IssuerOptionValue', value='0.00', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='IssuerOptionValue', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='IssuerOptionValue', value='0.00', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='Leverage-S', value='0.00', currency='', modelCode=''), 
AccountValue(account='DU3352788', tag='LookAheadAvailableFunds', value='2500.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='LookAheadExcessLiquidity', value='2500.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='LookAheadInitMarginReq', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='LookAheadMaintMarginReq', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='LookAheadNextChange', value='0', currency='', modelCode=''), 
AccountValue(account='DU3352788', tag='MaintMarginReq', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='MoneyMarketFundValue', value='0.00', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='MoneyMarketFundValue', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='MoneyMarketFundValue', value='0.00', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='MutualFundValue', value='0.00', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='MutualFundValue', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='MutualFundValue', value='0.00', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='NLVAndMarginInReview', value='false', currency='', modelCode=''), 
AccountValue(account='DU3352788', tag='NetDividend', value='0.00', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='NetDividend', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='NetDividend', value='0.00', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='NetLiquidation', value='2500.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='NetLiquidationByCurrency', value='2499.998', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='NetLiquidationByCurrency', value='2499.998', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='NetLiquidationByCurrency', value='0.00', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='NetLiquidationUncertainty', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='OptionMarketValue', value='0.00', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='OptionMarketValue', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='OptionMarketValue', value='0.00', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='PASharesValue', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='PhysicalCertificateValue', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='PostExpirationExcess', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='PostExpirationMargin', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='RealCurrency', value='EUR', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='RealCurrency', value='EUR', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='RealCurrency', value='USD', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='RealizedPnL', value='-8.01', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='RealizedPnL', value='-8.01', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='RealizedPnL', value='0.00', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='SegmentTitle-S', value='CFD', currency='', modelCode=''), 
AccountValue(account='DU3352788', tag='StockMarketValue', value='0.00', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='StockMarketValue', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='StockMarketValue', value='0.00', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='TBillValue', value='0.00', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='TBillValue', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='TBillValue', value='0.00', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='TBondValue', value='0.00', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='TBondValue', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='TBondValue', value='0.00', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='TotalCashBalance', value='2499.998', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='TotalCashBalance', value='2499.998', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='TotalCashBalance', value='0.00', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='TotalCashValue', value='2500.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='TotalDebitCardPendingCharges', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='TradingType-S', value='STKNOPT', currency='', modelCode=''), 
AccountValue(account='DU3352788', tag='UnrealizedPnL', value='0.00', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='UnrealizedPnL', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='UnrealizedPnL', value='0.00', currency='USD', modelCode=''), 
AccountValue(account='DU3352788', tag='WarrantValue', value='0.00', currency='BASE', modelCode=''), 
AccountValue(account='DU3352788', tag='WarrantValue', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='WarrantValue', value='0.00', currency='USD', modelCode='')]










[AccountValue(account='DU3352788', tag='AccountCode', value='DU3352788', currency='', modelCode=''),
AccountValue(account='DU3352788', tag='AccountOrGroup', value='DU3352788', currency='BASE', modelCode=''),
AccountValue(account='DU3352788', tag='AccountOrGroup', value='DU3352788', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='AccountOrGroup', value='DU3352788', currency='USD', modelCode=''),
AccountValue(account='DU3352788', tag='AccountReady', value='true', currency='', modelCode=''),
AccountValue(account='DU3352788', tag='AccountType', value='INDIVIDUAL', currency='', modelCode=''),
AccountValue(account='DU3352788', tag='AccruedCash', value='0.00', currency='BASE', modelCode=''),
AccountValue(account='DU3352788', tag='AccruedCash', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='AccruedCash', value='0.00', currency='USD', modelCode=''),
AccountValue(account='DU3352788', tag='AccruedDividend', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='AvailableFunds', value='451.99', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='Billable', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='BuyingPower', value='3013.26', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='CashBalance', value='2527.8905', currency='BASE', modelCode=''),
AccountValue(account='DU3352788', tag='CashBalance', value='2500.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='CashBalance', value='33.1786', currency='USD', modelCode=''),
AccountValue(account='DU3352788', tag='CorporateBondValue', value='0.00', currency='BASE', modelCode=''),
AccountValue(account='DU3352788', tag='CorporateBondValue', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='CorporateBondValue', value='0.00', currency='USD', modelCode=''),
AccountValue(account='DU3352788', tag='Currency', value='BASE', currency='BASE', modelCode=''),
AccountValue(account='DU3352788', tag='Currency', value='EUR', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='Currency', value='USD', currency='USD', modelCode=''),
AccountValue(account='DU3352788', tag='Cushion', value='0.968458', currency='', modelCode=''),
AccountValue(account='DU3352788', tag='EquityWithLoanValue', value='2451.99', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='ExcessLiquidity', value='2374.65', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='ExchangeRate', value='1.00', currency='BASE', modelCode=''),
AccountValue(account='DU3352788', tag='ExchangeRate', value='1.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='ExchangeRate', value='0.8406187', currency='USD', modelCode=''),
AccountValue(account='DU3352788', tag='FullAvailableFunds', value='451.99', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='FullExcessLiquidity', value='2374.65', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='FullInitMarginReq', value='2000.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='FullMaintMarginReq', value='77.34', currency='EUR', modelCode=''),
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
AccountValue(account='DU3352788', tag='GrossPositionValue', value='75.90', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='Guarantee', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='IndianStockHaircut', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='InitMarginReq', value='2000.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='IssuerOptionValue', value='0.00', currency='BASE', modelCode=''),
AccountValue(account='DU3352788', tag='IssuerOptionValue', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='IssuerOptionValue', value='0.00', currency='USD', modelCode=''),
AccountValue(account='DU3352788', tag='Leverage-S', value='0.03', currency='', modelCode=''),
AccountValue(account='DU3352788', tag='LookAheadAvailableFunds', value='451.99', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='LookAheadExcessLiquidity', value='2374.65', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='LookAheadInitMarginReq', value='2000.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='LookAheadMaintMarginReq', value='77.34', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='LookAheadNextChange', value='1615410000', currency='', modelCode=''),
AccountValue(account='DU3352788', tag='MaintMarginReq', value='77.34', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='MoneyMarketFundValue', value='0.00', currency='BASE', modelCode=''),
AccountValue(account='DU3352788', tag='MoneyMarketFundValue', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='MoneyMarketFundValue', value='0.00', currency='USD', modelCode=''),
AccountValue(account='DU3352788', tag='MutualFundValue', value='0.00', currency='BASE', modelCode=''),
AccountValue(account='DU3352788', tag='MutualFundValue', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='MutualFundValue', value='0.00', currency='USD', modelCode=''),
AccountValue(account='DU3352788', tag='NLVAndMarginInReview', value='false', currency='', modelCode=''),
AccountValue(account='DU3352788', tag='NetDividend', value='0.00', currency='BASE', modelCode=''),
AccountValue(account='DU3352788', tag='NetDividend', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='NetDividend', value='0.00', currency='USD', modelCode=''),
AccountValue(account='DU3352788', tag='NetLiquidation', value='2451.99', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='NetLiquidationByCurrency', value='2451.9897', currency='BASE', modelCode=''),
AccountValue(account='DU3352788', tag='NetLiquidationByCurrency', value='2500.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='NetLiquidationByCurrency', value='-57.1131', currency='USD', modelCode=''),
AccountValue(account='DU3352788', tag='NetLiquidationUncertainty', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='OptionMarketValue', value='0.00', currency='BASE', modelCode=''),
AccountValue(account='DU3352788', tag='OptionMarketValue', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='OptionMarketValue', value='0.00', currency='USD', modelCode=''),
AccountValue(account='DU3352788', tag='PASharesValue', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='PhysicalCertificateValue', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='PostExpirationExcess', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='PostExpirationMargin', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='RealCurrency', value='BASE', currency='BASE', modelCode=''),
AccountValue(account='DU3352788', tag='RealCurrency', value='EUR', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='RealCurrency', value='USD', currency='USD', modelCode=''),
AccountValue(account='DU3352788', tag='RealizedPnL', value='-22.35', currency='BASE', modelCode=''),
AccountValue(account='DU3352788', tag='RealizedPnL', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='RealizedPnL', value='-26.58', currency='USD', modelCode=''),
AccountValue(account='DU3352788', tag='SegmentTitle-S', value='CFD', currency='', modelCode=''),
AccountValue(account='DU3352788', tag='StockMarketValue', value='-75.90', currency='BASE', modelCode=''),
AccountValue(account='DU3352788', tag='StockMarketValue', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='StockMarketValue', value='-90.29', currency='USD', modelCode=''),
AccountValue(account='DU3352788', tag='TBillValue', value='0.00', currency='BASE', modelCode=''),
AccountValue(account='DU3352788', tag='TBillValue', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='TBillValue', value='0.00', currency='USD', modelCode=''),
AccountValue(account='DU3352788', tag='TBondValue', value='0.00', currency='BASE', modelCode=''),
AccountValue(account='DU3352788', tag='TBondValue', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='TBondValue', value='0.00', currency='USD', modelCode=''),
AccountValue(account='DU3352788', tag='TotalCashBalance', value='2527.8905', currency='BASE', modelCode=''),
AccountValue(account='DU3352788', tag='TotalCashBalance', value='2500.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='TotalCashBalance', value='33.1786', currency='USD', modelCode=''),
AccountValue(account='DU3352788', tag='TotalCashValue', value='2527.90', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='TotalDebitCardPendingCharges', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='TradingType-S', value='STKNOPT', currency='', modelCode=''),
AccountValue(account='DU3352788', tag='UnrealizedPnL', value='-0.65', currency='BASE', modelCode=''),
AccountValue(account='DU3352788', tag='UnrealizedPnL', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='UnrealizedPnL', value='-0.78', currency='USD', modelCode=''),
AccountValue(account='DU3352788', tag='WarrantValue', value='0.00', currency='BASE', modelCode=''),
AccountValue(account='DU3352788', tag='WarrantValue', value='0.00', currency='EUR', modelCode=''),
AccountValue(account='DU3352788', tag='WarrantValue', value='0.00', currency='USD', modelCode='')]

[
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), 
execution=

Execution(execId='0000e859.60864172.01.01', time=datetime.datetime(2021, 4, 26, 12, 58, 4, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.528, permId=1262916859, clientId=2, orderId=3, liquidation=0, cumQty=10.0, avgPrice=2.528, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.60864172.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 12, 58, 4, tzinfo=datetime.timezone.utc)), 

Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=

Execution(execId='0000e859.60864173.01.01', time=datetime.datetime(2021, 4, 26, 12, 58, 31, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='SLD', shares=10.0, price=2.526, permId=1262916862, clientId=0, orderId=0, liquidation=0, cumQty=10.0, avgPrice=2.526, orderRef='MktDepth', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.60864173.01.01', commission=4.0, currency='EUR', realizedPNL=-8.02, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 12, 58, 31, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=

Execution(execId='0000e859.6086419f.01.01', time=datetime.datetime(2021, 4, 26, 13, 5, 52, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.524, permId=1262916866, clientId=2, orderId=8, liquidation=0, cumQty=10.0, avgPrice=2.524, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.6086419f.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 5, 52, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=

Execution(execId='0000e859.608641c1.01.01', time=datetime.datetime(2021, 4, 26, 13, 9, 12, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.53, permId=1262916873, clientId=2, orderId=13, liquidation=0, cumQty=10.0, avgPrice=2.53, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641c1.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 9, 12, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=

Execution(execId='0000e859.608641c9.01.01', time=datetime.datetime(2021, 4, 26, 13, 9, 50, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='SLD', shares=20.0, price=2.528, permId=1262916882, clientId=0, orderId=0, liquidation=0, cumQty=20.0, avgPrice=2.528, orderRef='MktDepth', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641c9.01.01', commission=4.0, currency='EUR', realizedPNL=-11.98, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 9, 50, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=

Execution(execId='0000e859.608641cd.01.01', time=datetime.datetime(2021, 4, 26, 13, 10, 15, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.53, permId=1262916884, clientId=2, orderId=16, liquidation=0, cumQty=10.0, avgPrice=2.53, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641cd.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 10, 15, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=

Execution(execId='0000e859.608641da.01.01', time=datetime.datetime(2021, 4, 26, 13, 12, 20, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.53, permId=1262916893, clientId=2, orderId=21, liquidation=0, cumQty=10.0, avgPrice=2.53, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641da.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 12, 20, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=

Execution(execId='0000e859.608641df.01.01', time=datetime.datetime(2021, 4, 26, 13, 12, 42, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='SLD', shares=20.0, price=2.529, permId=1262916896, clientId=0, orderId=0, liquidation=0, cumQty=20.0, avgPrice=2.529, orderRef='MktDepth', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641df.01.01', commission=4.0, currency='EUR', realizedPNL=-12.02, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 12, 42, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=

Execution(execId='0000e859.608641e2.01.01', time=datetime.datetime(2021, 4, 26, 13, 12, 58, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.53, permId=1262916898, clientId=2, orderId=24, liquidation=0, cumQty=10.0, avgPrice=2.53, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641e2.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 12, 58, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=

Execution(execId='0000e859.608641e3.01.01', time=datetime.datetime(2021, 4, 26, 13, 13, 13, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='SLD', shares=10.0, price=2.529, permId=1262916901, clientId=0, orderId=0, liquidation=0, cumQty=10.0, avgPrice=2.529, orderRef='MktDepth', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641e3.01.01', commission=4.0, currency='EUR', realizedPNL=-8.01, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 13, 13, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=

Execution(execId='0000e859.608641eb.01.01', time=datetime.datetime(2021, 4, 26, 13, 14, 18, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.529, permId=1262916903, clientId=2, orderId=27, liquidation=0, cumQty=10.0, avgPrice=2.529, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641eb.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 14, 18, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=

Execution(execId='0000e859.608641f5.01.01', time=datetime.datetime(2021, 4, 26, 13, 16, 45, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='SLD', shares=10.0, price=2.526, permId=1262916904, clientId=0, orderId=0, liquidation=0, cumQty=10.0, avgPrice=2.526, orderRef='MktDepth', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641f5.01.01', commission=4.0, currency='EUR', realizedPNL=-8.03, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 16, 45, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=

Execution(execId='0000e859.608641f9.01.01', time=datetime.datetime(2021, 4, 26, 13, 17, 22, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.527, permId=1262916906, clientId=2, orderId=28, liquidation=0, cumQty=10.0, avgPrice=2.527, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641f9.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 17, 22, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=

Execution(execId='0000e859.608641fb.01.01', time=datetime.datetime(2021, 4, 26, 13, 18, 58, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='SLD', shares=10.0, price=2.533, permId=1262916908, clientId=0, orderId=0, liquidation=0, cumQty=10.0, avgPrice=2.533, orderRef='MktDepth', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641fb.01.01', commission=4.0, currency='EUR', realizedPNL=-7.94, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 18, 58, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=

Execution(execId='0000e859.608641fd.01.01', time=datetime.datetime(2021, 4, 26, 13, 19, 6, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.536, permId=1262916923, clientId=2, orderId=32, liquidation=0, cumQty=10.0, avgPrice=2.536, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641fd.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 19, 6, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK', tradingClass='CABK'), execution=

Execution(execId='0000e859.60864244.01.01', time=datetime.datetime(2021, 4, 26, 13, 37, 40, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.547, permId=187089424, clientId=3, orderId=3, liquidation=0, cumQty=10.0, avgPrice=2.547, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.60864244.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 37, 40, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK', tradingClass='CABK'), 
execution=
Execution(execId='0000e859.60864245.01.01', time=datetime.datetime(2021, 4, 26, 13, 38, 7, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='SLD', shares=20.0, price=2.543, permId=187089427, clientId=0, orderId=0, liquidation=0, cumQty=20.0, avgPrice=2.543, orderRef='MktDepth', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.60864245.01.01', commission=4.0, currency='EUR', realizedPNL=-11.97, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 38, 7, tzinfo=datetime.timezone.utc)), 

Fill(contract=Stock(conId=30314144, symbol='SAN1', exchange='DXEES', currency='EUR', localSymbol='SAN1', tradingClass='SAN1'), 
       execution=
Execution(execId='0000e859.6086424b.01.01', time=datetime.datetime(2021, 4, 26, 13, 41, 22, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.9145, permId=187089446, clientId=3, orderId=40, liquidation=0, cumQty=10.0, avgPrice=2.9145, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.6086424b.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 50, 12, 827895, tzinfo=datetime.timezone.utc))]


Trade(contract=Stock(symbol='SAN1', exchange='SMART', currency='EUR'), 
       order=MarketOrder(orderId=40, clientId=3, action='BUY', totalQuantity=10), 
       orderStatus=OrderStatus(orderId=40, status='PendingSubmit', filled=0, remaining=0, avgFillPrice=0.0, permId=0, parentId=0, lastFillPrice=0.0, clientId=0, whyHeld='', mktCapPrice=0.0), fills=[], log=[TradeLogEntry(time=datetime.datetime(2021, 4, 26, 13, 41, 21, 653891, tzinfo=datetime.timezone.utc), status='PendingSubmit', message='')]), 
Trade(contract=Stock(symbol='SAN1', exchange='SMART', currency='EUR'), 
       order=LimitOrder(orderId=41, clientId=3, action='SELL', totalQuantity=10, lmtPrice=10), 
       orderStatus=OrderStatus(orderId=41, status='PendingSubmit', filled=0, remaining=0, avgFillPrice=0.0, permId=0, parentId=0, lastFillPrice=0.0, clientId=0, whyHeld='', mktCapPrice=0.0), fills=[], log=[TradeLogEntry(time=datetime.datetime(2021, 4, 26, 13, 41, 21, 654298, tzinfo=datetime.timezone.utc), status='PendingSubmit', message='')]), 
Trade(contract=Stock(symbol='SAN1', exchange='SMART', currency='EUR'), 
       order=StopOrder(orderId=42, clientId=3, action='SELL', totalQuantity=10, auxPrice=1), 
       orderStatus=OrderStatus(orderId=42, status='PendingSubmit', filled=0, remaining=0, avgFillPrice=0.0, permId=0, parentId=0, lastFillPrice=0.0, clientId=0, whyHeld='', mktCapPrice=0.0), fills=[], log=[TradeLogEntry(time=datetime.datetime(2021, 4, 26, 13, 41, 21, 654689, tzinfo=datetime.timezone.utc), status='PendingSubmit', message='')




       [
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=
Execution(execId='0000e859.60864172.01.01', time=datetime.datetime(2021, 4, 26, 12, 58, 4, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.528, permId=1262916859, clientId=2, orderId=3, liquidation=0, cumQty=10.0, avgPrice=2.528, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.60864172.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 12, 58, 4, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=
Execution(execId='0000e859.60864173.01.01', time=datetime.datetime(2021, 4, 26, 12, 58, 31, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='SLD', shares=10.0, price=2.526, permId=1262916862, clientId=0, orderId=0, liquidation=0, cumQty=10.0, avgPrice=2.526, orderRef='MktDepth', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.60864173.01.01', commission=4.0, currency='EUR', realizedPNL=-8.02, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 12, 58, 31, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=
Execution(execId='0000e859.6086419f.01.01', time=datetime.datetime(2021, 4, 26, 13, 5, 52, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.524, permId=1262916866, clientId=2, orderId=8, liquidation=0, cumQty=10.0, avgPrice=2.524, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.6086419f.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 5, 52, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=
Execution(execId='0000e859.608641c1.01.01', time=datetime.datetime(2021, 4, 26, 13, 9, 12, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.53, permId=1262916873, clientId=2, orderId=13, liquidation=0, cumQty=10.0, avgPrice=2.53, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641c1.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 9, 12, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=
Execution(execId='0000e859.608641c9.01.01', time=datetime.datetime(2021, 4, 26, 13, 9, 50, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='SLD', shares=20.0, price=2.528, permId=1262916882, clientId=0, orderId=0, liquidation=0, cumQty=20.0, avgPrice=2.528, orderRef='MktDepth', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641c9.01.01', commission=4.0, currency='EUR', realizedPNL=-11.98, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 9, 50, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=
Execution(execId='0000e859.608641cd.01.01', time=datetime.datetime(2021, 4, 26, 13, 10, 15, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.53, permId=1262916884, clientId=2, orderId=16, liquidation=0, cumQty=10.0, avgPrice=2.53, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641cd.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 10, 15, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=
Execution(execId='0000e859.608641da.01.01', time=datetime.datetime(2021, 4, 26, 13, 12, 20, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.53, permId=1262916893, clientId=2, orderId=21, liquidation=0, cumQty=10.0, avgPrice=2.53, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641da.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 12, 20, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=
Execution(execId='0000e859.608641df.01.01', time=datetime.datetime(2021, 4, 26, 13, 12, 42, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='SLD', shares=20.0, price=2.529, permId=1262916896, clientId=0, orderId=0, liquidation=0, cumQty=20.0, avgPrice=2.529, orderRef='MktDepth', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641df.01.01', commission=4.0, currency='EUR', realizedPNL=-12.02, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 12, 42, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=
Execution(execId='0000e859.608641e2.01.01', time=datetime.datetime(2021, 4, 26, 13, 12, 58, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.53, permId=1262916898, clientId=2, orderId=24, liquidation=0, cumQty=10.0, avgPrice=2.53, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641e2.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 12, 58, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=
Execution(execId='0000e859.608641e3.01.01', time=datetime.datetime(2021, 4, 26, 13, 13, 13, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='SLD', shares=10.0, price=2.529, permId=1262916901, clientId=0, orderId=0, liquidation=0, cumQty=10.0, avgPrice=2.529, orderRef='MktDepth', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641e3.01.01', commission=4.0, currency='EUR', realizedPNL=-8.01, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 13, 13, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=
Execution(execId='0000e859.608641eb.01.01', time=datetime.datetime(2021, 4, 26, 13, 14, 18, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.529, permId=1262916903, clientId=2, orderId=27, liquidation=0, cumQty=10.0, avgPrice=2.529, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641eb.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 14, 18, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=
Execution(execId='0000e859.608641f5.01.01', time=datetime.datetime(2021, 4, 26, 13, 16, 45, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='SLD', shares=10.0, price=2.526, permId=1262916904, clientId=0, orderId=0, liquidation=0, cumQty=10.0, avgPrice=2.526, orderRef='MktDepth', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641f5.01.01', commission=4.0, currency='EUR', realizedPNL=-8.03, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 16, 45, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=
Execution(execId='0000e859.608641f9.01.01', time=datetime.datetime(2021, 4, 26, 13, 17, 22, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.527, permId=1262916906, clientId=2, orderId=28, liquidation=0, cumQty=10.0, avgPrice=2.527, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641f9.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 17, 22, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=
Execution(execId='0000e859.608641fb.01.01', time=datetime.datetime(2021, 4, 26, 13, 18, 58, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='SLD', shares=10.0, price=2.533, permId=1262916908, clientId=0, orderId=0, liquidation=0, cumQty=10.0, avgPrice=2.533, orderRef='MktDepth', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641fb.01.01', commission=4.0, currency='EUR', realizedPNL=-7.94, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 18, 58, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK'), execution=
Execution(execId='0000e859.608641fd.01.01', time=datetime.datetime(2021, 4, 26, 13, 19, 6, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.536, permId=1262916923, clientId=2, orderId=32, liquidation=0, cumQty=10.0, avgPrice=2.536, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608641fd.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 19, 6, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK', tradingClass='CABK'), execution=
Execution(execId='0000e859.60864244.01.01', time=datetime.datetime(2021, 4, 26, 13, 37, 40, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.547, permId=187089424, clientId=3, orderId=3, liquidation=0, cumQty=10.0, avgPrice=2.547, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.60864244.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 37, 40, tzinfo=datetime.timezone.utc)), 
Fill(contract=Stock(conId=48832907, symbol='CABK', exchange='DXEES', currency='EUR', localSymbol='CABK', tradingClass='CABK'), execution=
Execution(execId='0000e859.60864245.01.01', time=datetime.datetime(2021, 4, 26, 13, 38, 7, tzinfo=datetime.timezone.utc), acctNumber='DU3352788', exchange='DXEES', side='SLD', shares=20.0, price=2.543, permId=187089427, clientId=0, orderId=0, liquidation=0, cumQty=20.0, avgPrice=2.543, orderRef='MktDepth', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.60864245.01.01', commission=4.0, currency='EUR', realizedPNL=-11.97, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 38, 7, tzinfo=datetime.timezone.utc)), 




Fill(contract=Stock(conId=30314144, symbol='SAN1', exchange='DXEES', currency='EUR', localSymbol='SAN1', tradingClass='SAN1'), execution=
Execution(execId='0000e859.6086424b.01.01', time=datetime.datetime(2021, 4, 26, 13, 41, 22, tzinfo=datetime.timezone.utc), 
       acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.9145, permId=187089446, clientId=3, orderId=40, liquidation=0, cumQty=10.0, avgPrice=2.9145, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.6086424b.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 13, 41, 22, tzinfo=datetime.timezone.utc)), 

Fill(contract=Stock(conId=30314144, symbol='SAN1', exchange='DXEES', currency='EUR', localSymbol='SAN1', tradingClass='SAN1'), execution=
Execution(execId='0000e859.608642e5.01.01', time=datetime.datetime(2021, 4, 26, 14, 12, 38, tzinfo=datetime.timezone.utc), 
acctNumber='DU3352788', exchange='DXEES', side='SLD', shares=10.0, price=2.917, permId=187089449, clientId=0, orderId=0, liquidation=0, cumQty=10.0, avgPrice=2.917, orderRef='MktDepth', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608642e5.01.01', commission=4.0, currency='EUR', realizedPNL=-7.975, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 14, 12, 38, tzinfo=datetime.timezone.utc)), 

Fill(contract=Stock(conId=30314144, symbol='SAN1', exchange='DXEES', currency='EUR', localSymbol='SAN1', tradingClass='SAN1'), execution=
Execution(execId='0000e859.608642f2.01.01', time=datetime.datetime(2021, 4, 26, 14, 16, 19, tzinfo=datetime.timezone.utc), 
acctNumber='DU3352788', exchange='DXEES', side='SLD', shares=10.0, price=2.916, permId=187089470, clientId=3, orderId=45, liquidation=0, cumQty=10.0, avgPrice=2.916, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608642f2.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 14, 17, 13, 203253, tzinfo=datetime.timezone.utc)), 

Fill(contract=Stock(conId=30314144, symbol='SAN1', exchange='DXEES', currency='EUR', localSymbol='SAN1', tradingClass='SAN1'), execution=
Execution(execId='0000e859.608642f3.01.01', time=datetime.datetime(2021, 4, 26, 14, 16, 19, tzinfo=datetime.timezone.utc), 
acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.918, permId=187089471, clientId=3, orderId=46, liquidation=0, cumQty=10.0, avgPrice=2.918, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608642f3.01.01', commission=4.0, currency='EUR', realizedPNL=-8.02, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 14, 17, 13, 203253, tzinfo=datetime.timezone.utc)), 

Fill(contract=Stock(conId=30314144, symbol='SAN1', exchange='DXEES', currency='EUR', localSymbol='SAN1', tradingClass='SAN1'), execution=
Execution(execId='0000e859.608642f9.01.01', time=datetime.datetime(2021, 4, 26, 14, 16, 25, tzinfo=datetime.timezone.utc), 
acctNumber='DU3352788', exchange='DXEES', side='BOT', shares=10.0, price=2.917, permId=187089472, clientId=3, orderId=47, liquidation=0, cumQty=10.0, avgPrice=2.917, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608642f9.01.01', commission=4.0, currency='EUR', realizedPNL=0.0, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 14, 17, 13, 203253, tzinfo=datetime.timezone.utc)), 

Fill(contract=Stock(conId=30314144, symbol='SAN1', exchange='DXEES', currency='EUR', localSymbol='SAN1', tradingClass='SAN1'), execution=
Execution(execId='0000e859.608642ff.01.01', time=datetime.datetime(2021, 4, 26, 14, 16, 56, tzinfo=datetime.timezone.utc), 
acctNumber='DU3352788', exchange='DXEES', side='SLD', shares=10.0, price=2.9175, permId=187089473, clientId=3, orderId=48, liquidation=0, cumQty=10.0, avgPrice=2.9175, orderRef='', evRule='', evMultiplier=0.0, modelCode='', lastLiquidity=2), commissionReport=CommissionReport(execId='0000e859.608642ff.01.01', commission=4.0, currency='EUR', realizedPNL=-7.995, yield_=0.0, yieldRedemptionDate=0), time=datetime.datetime(2021, 4, 26, 14, 17, 13, 203253, tzinfo=datetime.timezone.utc))]