import triggerClass as tC

# -------------------------------------------------------------------------------------------

e = tC.cmc(
    gainTrigger=1,  # %
    loseTrigger=-1,  # %
    moveHistoryCsv="moveHistory.csv",
    delay=10
)

e.al