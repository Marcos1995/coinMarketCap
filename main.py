import triggerClass as tC

# -------------------------------------------------------------------------------------------

e = tC.cmc(
    buyTrigger=-70,  # %
    sellTrigger=1000,  # %
    isTrading=True,
    sendNotifications=True,
    tradingHistoryCsv="tradingHistory.csv",
    bscContractsCsv="bscContracts_old.csv",
    maxThreads=5,
    delay=20
)

e.main()
