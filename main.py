import tradingClass

# -------------------------------------------------------------------------------------------

trading = tradingClass.cmc(
    buyTrigger=-50,  # %
    sellTrigger=100,  # %
    isTrading=False,
    sendNotifications=False,
    tradingHistoryCsv="tradingHistory.csv",
    bscContractsCsv="bscContracts.csv",
    maxThreads=5,
    delay=30
)

trading.telegramMainTest()