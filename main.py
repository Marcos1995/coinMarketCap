import triggerClass as tC

# -------------------------------------------------------------------------------------------

e = tC.cmc(
    buyTrigger=-90,  # %
    sellTrigger=100,  # %
    isTrading=True,
    sendNotifications=False,
    tradingHistoryCsv="tradingHistory.csv",
    bscContractsCsv="bscContracts.csv",
    delay=30
)

e.core()
