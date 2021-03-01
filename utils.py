from strategy.tests import *

def runStrategyTests():
    TestStrategyDataToShortWithAOpenPriceHigherThanLastPrice()
    print ("\n------------------------------------\n")
    TestStrategyDataToShortWithAOpenPriceLowerThanLastPrice()
    print ("\n------------------------------------\n")
    TestStrategyDataToLongWithAOpenPriceHigherThanLastPrice()
    print ("\n------------------------------------\n")
    TestStrategyDataToLongWithAOpenPriceLowerThanLastPrice()
    print ("\n------------------------------------\n")
    TestStrategyDataTooLateToRunThisStrategy()
    print ("\n------------------------------------\n")
    TestStrategyDataForLongPositionForTimeout()
    print ("\n------------------------------------\n")
    TestStrategyDataForShortPositionForTimeout()
    print ("\n------------------------------------\n")
    TestStrategyDataForShortPositionDoNothing()
    print ("\n------------------------------------\n")
    TestStrategyDataDateWindowExpiredWithoutPosition()
    print ("\n------------------------------------\n")
    TestStrategyDataWithDateWindowExpiredWithOrder()

    print ("\n")
    
if __name__ == '__main__':
    runStrategyTests()