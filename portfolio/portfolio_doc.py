# ib.reqPositions()
# ib.reqPositionsAsync
# cancelPositions

### ib.reqPositions ###
[Position(account='DU3352788', contract=Stock(conId=75197507, symbol='EXPR', exchange='NYSE', currency='USD', localSymbol='EXPR', tradingClass='EXPR'), position=5.0, avgCost=2.8), Position(account='DU3352788', contract=Stock(conId=47527197, symbol='EVK', exchange='NASDAQ', currency='USD', localSymbol='EVK', tradingClass='NMS'), position=0.0, avgCost=0.0), Position(account='DU3352788', contract=Stock(conId=47527197, symbol='EVK', exchange='NASDAQ', currency='USD', localSymbol='EVK', tradingClass='NMS'), position=0.0, avgCost=0.0), Position(account='DU3352788', contract=Stock(conId=47527197, symbol='EVK', exchange='NASDAQ', currency='USD', localSymbol='EVK', tradingClass='NMS'), position=-5.0, avgCost=3.29), Position(account='DU3352788', contract=Stock(conId=75197507, symbol='EXPR', exchange='NYSE', currency='USD', localSymbol='EXPR', tradingClass='EXPR'), position=5.0, avgCost=2.828), Position(account='DU3352788', contract=Stock(conId=47527197, symbol='EVK', exchange='NASDAQ', currency='USD', localSymbol='EVK', tradingClass='NMS'), position=-5.0, avgCost=3.2541642)]

### ib.positions() ###
[Position(account='DU3352788', contract=Stock(conId=75197507, symbol='EXPR', exchange='NYSE', currency='USD', localSymbol='EXPR', tradingClass='EXPR'), position=5.0, avgCost=2.828), Position(account='DU3352788', contract=Stock(conId=47527197, symbol='EVK', exchange='NASDAQ', currency='USD', localSymbol='EVK', tradingClass='NMS'), position=-5.0, avgCost=3.2541642)]



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
        AccountValue(account='DU3352788', tag='AvailableFunds', value='2394.87', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='Billable', value='0.00', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='BuyingPower', value='15965.80', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='CashBalance', value='2397.9323', currency='BASE', modelCode=''), 
        AccountValue(account='DU3352788', tag='CashBalance', value='2500.00', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='CashBalance', value='-122.9487', currency='USD', modelCode=''), 
        AccountValue(account='DU3352788', tag='CorporateBondValue', value='0.00', currency='BASE', modelCode=''), 
        AccountValue(account='DU3352788', tag='CorporateBondValue', value='0.00', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='CorporateBondValue', value='0.00', currency='USD', modelCode=''), 
        AccountValue(account='DU3352788', tag='Currency', value='BASE', currency='BASE', modelCode=''), 
        AccountValue(account='DU3352788', tag='Currency', value='EUR', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='Currency', value='USD', currency='USD', modelCode=''), 
        AccountValue(account='DU3352788', tag='Cushion', value='0.998723', currency='', modelCode=''), 
        AccountValue(account='DU3352788', tag='EquityWithLoanValue', value='2397.93', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='ExcessLiquidity', value='2394.87', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='ExchangeRate', value='1.00', currency='BASE', modelCode=''), 
        AccountValue(account='DU3352788', tag='ExchangeRate', value='1.00', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='ExchangeRate', value='0.8303924', currency='USD', modelCode=''), 
        AccountValue(account='DU3352788', tag='FullAvailableFunds', value='2394.87', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='FullExcessLiquidity', value='2394.87', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='FullInitMarginReq', value='3.06', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='FullMaintMarginReq', value='3.06', currency='EUR', modelCode=''), 
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
        AccountValue(account='DU3352788', tag='InitMarginReq', value='3.06', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='IssuerOptionValue', value='0.00', currency='BASE', modelCode=''), 
        AccountValue(account='DU3352788', tag='IssuerOptionValue', value='0.00', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='IssuerOptionValue', value='0.00', currency='USD', modelCode=''), 
        AccountValue(account='DU3352788', tag='Leverage-S', value='0.00', currency='', modelCode=''), 
        AccountValue(account='DU3352788', tag='LookAheadAvailableFunds', value='2394.87', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='LookAheadExcessLiquidity', value='2394.87', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='LookAheadInitMarginReq', value='3.06', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='LookAheadMaintMarginReq', value='3.06', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='LookAheadNextChange', value='0', currency='', modelCode=''), 
        AccountValue(account='DU3352788', tag='MaintMarginReq', value='3.06', currency='EUR', modelCode=''), 
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
        AccountValue(account='DU3352788', tag='NetLiquidation', value='2397.93', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='NetLiquidationByCurrency', value='2397.9323', currency='BASE', modelCode=''), 
        AccountValue(account='DU3352788', tag='NetLiquidationByCurrency', value='2500.00', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='NetLiquidationByCurrency', value='-122.9487', currency='USD', modelCode=''), 
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
        AccountValue(account='DU3352788', tag='RealizedPnL', value='-1.60', currency='BASE', modelCode=''), 
        AccountValue(account='DU3352788', tag='RealizedPnL', value='0.00', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='RealizedPnL', value='-1.93', currency='USD', modelCode=''), 
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
        AccountValue(account='DU3352788', tag='TotalCashBalance', value='2397.9323', currency='BASE', modelCode=''), 
        AccountValue(account='DU3352788', tag='TotalCashBalance', value='2500.00', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='TotalCashBalance', value='-122.9487', currency='USD', modelCode=''), 
        AccountValue(account='DU3352788', tag='TotalCashValue', value='2397.93', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='TotalDebitCardPendingCharges', value='0.00', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='TradingType-S', value='STKNOPT', currency='', modelCode=''), 
        AccountValue(account='DU3352788', tag='UnrealizedPnL', value='0.00', currency='BASE', modelCode=''), 
        AccountValue(account='DU3352788', tag='UnrealizedPnL', value='0.00', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='UnrealizedPnL', value='0.00', currency='USD', modelCode=''), 
        AccountValue(account='DU3352788', tag='WarrantValue', value='0.00', currency='BASE', modelCode=''), 
        AccountValue(account='DU3352788', tag='WarrantValue', value='0.00', currency='EUR', modelCode=''), 
        AccountValue(account='DU3352788', tag='WarrantValue', value='0.00', currency='USD', modelCode='')]