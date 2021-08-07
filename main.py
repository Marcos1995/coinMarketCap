import triggerClass as tC

# -------------------------------------------------------------------------------------------

e = tC.cmc(
    sellTrigger=100,  # %
    buyTrigger=-95,  # %
    sendNotifications=False,
    isSimulation=False,
    moveHistoryCsv="moveHistory.csv",
    delay=30
)

e.core()
