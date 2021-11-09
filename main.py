import tradingClass

# -------------------------------------------------------------------------------------------

trading = tradingClass.cmc(
    buyTrigger=-50,  # %
    sellTrigger=50,  # %
    isTrading=False,
    sendNotifications=False,
    tradingType=2,
    maxThreads=5,
    delay=15
)

trading.main()