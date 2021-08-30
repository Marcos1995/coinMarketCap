import triggerClass as tC

# -------------------------------------------------------------------------------------------

e = tC.cmc(
    buyTrigger=-90,  # %
    sellTrigger=10,  # %
    isTrading=False,
    sendNotifications=False,
    tradingHistoryCsv="tradingHistory.csv",
    bscContractsCsv="bscContracts.csv",
    delay=60
)

e.main()
