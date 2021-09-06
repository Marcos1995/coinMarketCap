import triggerClass as tC

# -------------------------------------------------------------------------------------------

e = tC.cmc(
    buyTrigger=-50,  # %
    sellTrigger=50,  # %
    isTrading=False,
    sendNotifications=True,
    tradingHistoryCsv="tradingHistory.csv",
    bscContractsCsv="bscContracts.csv",
    maxThreads=5,
    delay=20
)

e.main()
