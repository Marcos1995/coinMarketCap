import tradingClass

# -------------------------------------------------------------------------------------------

trading = tradingClass.cmc(
    buyTrigger=-50,  # %
    sellTrigger=50,  # %
    isTrading=False,
    bnbAmountToBuy=0.01,
    sendNotifications=True,
    tradingType=3,
    maxThreads=5,
    delay=30
)

trading.checkExistingCryptos()