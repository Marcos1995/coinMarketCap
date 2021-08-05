import triggerClass as tC

# -------------------------------------------------------------------------------------------

e = tC.cmc(
    gainTrigger=100,  # %
    loseTrigger=-99,  # %
    sendNotifications=True,
    moveHistoryCsv="moveHistory.csv",
    delay=30
)

# e.core()
e.buyToken()
