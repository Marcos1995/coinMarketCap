import tradingClass

# -------------------------------------------------------------------------------------------

trading = tradingClass.cmc(
    buyTrigger=-50,  # %
    sellTrigger=30,  # %
    isTrading=True,
    bnbAmountToBuy=0.01,
    sendNotifications=True,
    tradingType=2,
    maxThreads=5,
    delay=15
)

trading.main()