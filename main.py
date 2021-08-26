import triggerClass as tC

# -------------------------------------------------------------------------------------------

e = tC.cmc(
    buyTrigger=-10,  # %
    sellTrigger=100,  # %
    isTrading=False,
    sendNotifications=True,
    tradingHistoryCsv="tradingHistory.csv",
    bscContractsCsv="bscContracts.csv",
    delay=30
)

e.test_getCsvSymbolsNotSold()
