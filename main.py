import tradingClass

# -------------------------------------------------------------------------------------------

trading = tradingClass.cmc(
    buyTrigger=-90,  # %
    sellTrigger=1000,  # %
    isTrading=False,
    sendNotifications=True,
    tradingHistoryCsv="tradingHistory.csv",
    bscContractsCsv="bscContracts.csv",
    maxThreads=5,
    delay=30
)

trading.main()
