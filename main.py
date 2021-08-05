import triggerClass as tC

# -------------------------------------------------------------------------------------------

e = tC.cmc(
    sellTrigger=100,  # %
    buyTrigger=-99,  # %
    sendNotifications=True,
    isSimulation=False,
    moveHistoryCsv="moveHistory.csv",
    delay=30
)

# e.core()
e.sellToken()
