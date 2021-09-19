import triggerClass

# -------------------------------------------------------------------------------------------

trading = triggerClass.cmc(
    buyTrigger=-101,  # %
    sellTrigger=1000,  # %
    isTrading=False,
    sendNotifications=True,
    tradingHistoryCsv="tradingHistory.csv",
    bscContractsCsv="bscContracts.csv",
    maxThreads=5,
    delay=30
)

trading.main()
