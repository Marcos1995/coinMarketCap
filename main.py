import tradingClass

# -------------------------------------------------------------------------------------------

trading = tradingClass.cmc(
    buyTrigger=-0.0001,  # %
    sellTrigger=1000,  # %
    isTrading=False,
    sendNotifications=True,
    tradingHistoryCsv="tradingHistory.csv",
    bscContractsCsv="bscContracts.csv",
    maxThreads=5,
    delay=30
)

trading.main()
