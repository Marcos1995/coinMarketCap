import triggerClass as tC
import pandas as pd

# -------------------------------------------------------------------------------------------

e = tC.cmc(
    buyTrigger=-90,  # %
    sellTrigger=100,  # %
    sendNotifications=False,
    isSimulation=False,
    moveHistoryCsv="moveHistory.csv",
    bscContractsCsv = "bscContracts.csv",
    delay=30
)

e.core()
