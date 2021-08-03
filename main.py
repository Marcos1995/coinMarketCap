import triggerClass as tC

# -------------------------------------------------------------------------------------------

e = tC.cmc(
    gainTrigger=100,  # %
    loseTrigger=-90,  # %
    isSendEmails=True,
    moveHistoryCsv="moveHistory.csv",
    delay=30
)

e.core()
