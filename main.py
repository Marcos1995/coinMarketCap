import tradingClass

# -------------------------------------------------------------------------------------------
"""
trading = tradingClass.cmc(
    buyTrigger=-50,  # %
    sellTrigger=100,  # %
    isTrading=True,
    sendNotifications=True,
    tradingHistoryCsv="tradingHistory.csv",
    bscContractsCsv="bscContracts.csv",
    maxThreads=5,
    delay=30
)

trading.main()
"""
tradingClass.getRealTradingPrice()