import tradingClass

# -------------------------------------------------------------------------------------------

trading = tradingClass.cmc(
    buyTrigger=-50,  # %
    sellTrigger=100,  # %
    isTrading=False,
    sendNotifications=False,
    tradingType=2,
    maxThreads=5,
    delay=30
)

trading.main()