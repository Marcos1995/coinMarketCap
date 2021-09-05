import triggerClass as tC

# -------------------------------------------------------------------------------------------

e = tC.cmc(
    buyTrigger=-50,  # %
    sellTrigger=50,  # %
    isTrading=False,
    sendNotifications=False,
    tradingHistoryCsv="tradingHistory.csv",
    bscContractsCsv="bscContracts.csv",
    delay=15
)

e.main()
