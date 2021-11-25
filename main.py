import tradingClass

# -------------------------------------------------------------------------------------------

trading = tradingClass.cmc(
    buyTrigger=-50,  # %
    sellTrigger=50,  # %
    isTrading=True,
    bnbAmountToBuy=0.01,
    sendNotifications=True,
    tradingType=2,
    maxThreads=5,
    delay=30
)

trading.main()