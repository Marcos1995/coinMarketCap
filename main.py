import triggerClass as tC

# -------------------------------------------------------------------------------------------

e = tC.cmc(
    buyTrigger=-5,  # %
    sellTrigger=1,  # %
    sendNotifications=False,
    isSimulation=True,
    moveHistoryCsv="moveHistory.csv",
    delay=30
)

e.core()
