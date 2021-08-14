import triggerClass as tC
import pandas as pd

# -------------------------------------------------------------------------------------------

e = tC.cmc(
    buyTrigger=-99,  # %
    sellTrigger=100,  # %
    sendNotifications=False,
    isSimulation=False,
    moveHistoryCsv="moveHistory.csv",
    delay=30
)

e.core()

exit()

from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()
aa = pd.DataFrame(cg.get_coins_list())
#print(aa)
data = pd.DataFrame(cg.get_coins_markets(vs_currency='usd'))

#print(data)

c = aa['id'].tolist()

print(cg.get_coin_by_id(id='litecoin'))
exit()

print(cg.get_price(ids=c, vs_currencies='usd'))
print(cg.get_price(ids=c, vs_currencies='usd', include_market_cap='true', include_24hr_vol='true', include_24hr_change='true', include_last_updated_at='true'))
