import triggerClass as tC

# -------------------------------------------------------------------------------------------

e = tC.cmc(
    gainTrigger=300,  # %
    loseTrigger=-80,  # %
    moveHistoryCsv="moveHistory.csv",
    delay=15
)

e.core()