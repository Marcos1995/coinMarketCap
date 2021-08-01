import triggerClass as tC

# -------------------------------------------------------------------------------------------

e = tC.cmc(
    gainTrigger=100,  # %
    loseTrigger=-90,  # %
    isSendEmails=False,
    moveHistoryCsv="moveHistory.csv",
    delay=15
)

e.core()
