

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


## ACCOUNT SUMMARY ##

[AccountValue(account='DU3352788', tag='AccountType', value='INDIVIDUAL', currency='', modelCode=''), 
AccountValue(account='DU3352788', tag='Cushion', value='0.997928', currency='', modelCode=''), 
AccountValue(account='DU3352788', tag='LookAheadNextChange', value='0', currency='', modelCode=''), 
AccountValue(account='DU3352788', tag='AccruedCash', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='AvailableFunds', value='2326.14', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='BuyingPower', value='15507.59', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='EquityWithLoanValue', value='2330.97', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='ExcessLiquidity', value='2326.14', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='FullAvailableFunds', value='2326.14', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='FullExcessLiquidity', value='2326.14', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='FullInitMarginReq', value='4.83', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='FullMaintMarginReq', value='4.83', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='GrossPositionValue', value='0.00', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='InitMarginReq', value='4.83', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='LookAheadAvailableFunds', value='2326.14', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='LookAheadExcessLiquidity', value='2326.14', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='LookAheadInitMarginReq', value='4.83', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='LookAheadMaintMarginReq', value='4.83', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='MaintMarginReq', value='4.83', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='NetLiquidation', value='2330.97', currency='EUR', modelCode=''), 
AccountValue(account='DU3352788', tag='TotalCashValue', value='2330.97', currency='EUR', modelCode='')]
