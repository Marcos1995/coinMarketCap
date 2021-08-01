import requests
import pandas as pd
import datetime as dt
import os
import time
import urllib.request, json
import bcolors
from bs4 import BeautifulSoup
from uniswap import Uniswap
from web3.auto import w3
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ------------------------------------------------------------------------------------

def formatPercentages(val):
    return round((val - 1) * 100, 4)

def printInfo(desc, color=""):
    print(dt.datetime.now(), "//", color, desc, bcolors.END)

class cmc:

    def __init__(self, gainTrigger, loseTrigger, isSendEmails, moveHistoryCsv, delay):

        self.gainTrigger = gainTrigger
        self.loseTrigger = loseTrigger
        self.isSendEmails = isSendEmails
        self.moveHistoryCsv = moveHistoryCsv
        self.delay = delay

        self.columnToExpand = "quotes"
        self.typeDesc = "type"
        self.listDesc = "List"

        self.allCoinMarketCapCoinsUrl = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing?start=1&limit=10000&convert=USD&cryptoType=all&tagType=all&audited=false"
        self.cryptoBaseUrl = "https://coinmarketcap.com/currencies/"

        self.uniswapBaseUrl = "https://app.uniswap.org/#/swap?"
        self.pancakeSwapBaseUrl = "https://exchange.pancakeswap.finance/#/swap?"

        self.tokenUrl = "/token/"

        self.idDesc = "id"
        self.nameDesc = "name"
        self.symbolDesc = "symbol"
        self.symbolNameDesc = "symbolName"
        self.slugDesc = "slug"
        self.priceDesc = "price"
        self.prevPriceDesc = "prevPrice"

        self.datetimeDesc = "datetime"
        self.prevDatetimeDesc = "prevDatetime"

        self.lastUpdatedDesc = "lastUpdated"
        self.prevLastUpdatedDesc = "prevLastUpdated"

        self.bscscanDesc = "bscscan"
        self.etherscanDesc = "etherscan"
        
        self.ethereumDesc = "Ethereum"
        self.binanceSmartChainDesc = "BinanceSmartChain"

        self.data = {}

        self.port = 465
        self.smtp_server_domain_name = "smtp.gmail.com"
        self.sender_mail = "botNotifications1995@gmail.com"
        self.password = "NByu2298"

        self.recipientEmails = [
            "marcospc1995@gmail.com",
            "fassboy61@gmail.com"
        ]

        # self.uniswapConnection()


    def uniswapConnection(self):

        from web3 import Web3

        # IPCProvider:
        w3 = Web3(Web3.IPCProvider('/home/pi/.ethereum/geth.ipc'))

        print(w3.isConnected())

        # HTTPProvider:
        w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

        print(w3.isConnected())

        # WebsocketProvider:
        w3 = Web3(Web3.WebsocketProvider('ws://127.0.0.1:8546'))

        print(w3.isConnected())

        address = None          # or None if you're not going to make transactions
        private_key = None  # or None if you're not going to make transactions
        version = 2                       # specify which version of Uniswap to use
        provider = w3    # can also be set through the environment variable `PROVIDER`
        uniswap = Uniswap(address=address, private_key=private_key, version=version, provider=provider)

        # Some token addresses we'll be using later in this guide
        eth = "0x0000000000000000000000000000000000000000"
        bat = "0x0D8775F648430679A709E98d2b0Cb6250d2887EF"
        dai = "0x6B175474E89094C44Da98b954EedeAC495271d0F"

        # Returns the amount of DAI you get for 1 ETH (10^18 wei)
        v = uniswap.get_price_input(eth, dai, 10**18)
        print(v)
        exit()


    # Get crypto coin tokens by searching in coinmarketcap websites (not ideal)
    def getTokens(self, cryptoSlug):

        # Dict to be returned
        tokens = {}

        allHrefs = []

        cryptoUrl = self.cryptoBaseUrl + cryptoSlug

        while True:
            try:
                html_page = urllib.request.urlopen(cryptoUrl)
                soup = BeautifulSoup(html_page, "html.parser")

                break
            except:
                time.sleep(self.delay)

        for link in soup.findAll('a'):
            href = str(link.get('href'))

            if self.tokenUrl in href:
                allHrefs.append(href)

        allHrefs = list(dict.fromkeys(allHrefs))

        for href in allHrefs:

            if self.etherscanDesc in href:
                platform = self.ethereumDesc
            elif self.bscscanDesc in href:
                platform = self.binanceSmartChainDesc
            else:
                continue

            contractToken = href.rsplit('/', 1)[-1]

            tokens[platform] = contractToken

        if len(tokens) > 0:
            tokens = {key: val for key, val in sorted(tokens.items(), key = lambda ele: ele[0])}

        return tokens
    

    def core(self):

        # If file exists...
        if os.path.exists(self.moveHistoryCsv):
            writeHeaders = False
        else:
            writeHeaders = True

        counter = 0

        while True:

            while True:
                try:
                    with urllib.request.urlopen(self.allCoinMarketCapCoinsUrl) as url:
                        rawData = json.loads(url.read().decode())

                    break
                except:
                    time.sleep(self.delay)

            for i, data in rawData.items():
                for desc, listOfDicts in data.items():

                    if desc.endswith(self.listDesc):
                        
                        df = pd.DataFrame(listOfDicts)
                        df = df.drop(['tags', 'cmcRank', 'marketPairCount', 'lastUpdated', 'isAudited', 'platform', 'auditInfoList'], axis = 1)
                        df = df.rename(columns = {self.nameDesc: self.symbolNameDesc})

                        df[self.columnToExpand] = df[self.columnToExpand].apply(lambda cell: cell[0])

                        df = df.drop(self.columnToExpand, axis=1).join(pd.DataFrame(df[self.columnToExpand].values.tolist()))

            for i, row in df.iterrows():

                # If "current" values are not set
                if self.data.get(row[self.idDesc], {self.priceDesc: -1})[self.priceDesc] == -1:

                    self.data.setdefault(row[self.idDesc], {})[self.priceDesc] = row[self.priceDesc]
                    self.data[row[self.idDesc]][self.lastUpdatedDesc] = row[self.lastUpdatedDesc]
                    self.data[row[self.idDesc]][self.symbolNameDesc] = row[self.symbolNameDesc]
                    self.data[row[self.idDesc]][self.symbolDesc] = row[self.symbolDesc]
                    self.data[row[self.idDesc]][self.slugDesc] = row[self.slugDesc]

                # If "current" values are not set
                else:

                    if self.data[row[self.idDesc]][self.lastUpdatedDesc] == row[self.lastUpdatedDesc]:
                        continue

                    self.data[row[self.idDesc]][self.prevPriceDesc] = self.data[row[self.idDesc]][self.priceDesc]
                    self.data[row[self.idDesc]][self.prevLastUpdatedDesc] = self.data[row[self.idDesc]][self.lastUpdatedDesc]
                    self.data[row[self.idDesc]][self.priceDesc] = row[self.priceDesc]
                    self.data[row[self.idDesc]][self.lastUpdatedDesc] = row[self.lastUpdatedDesc]

                    # Skip if current price is 0
                    if self.data[row[self.idDesc]][self.priceDesc] == 0:
                        continue
                    # Skip if prev price was 0 to prevent "division by 0" error
                    elif self.data[row[self.idDesc]][self.prevPriceDesc] == 0:
                        prevPrice = 1
                    else:
                        prevPrice = self.data[row[self.idDesc]][self.prevPriceDesc]

                    percengeDiffWoFormat = self.data[row[self.idDesc]][self.priceDesc] / prevPrice
                    percentageDiff = formatPercentages(percengeDiffWoFormat)

                    if percentageDiff >= self.gainTrigger:
                        color = bcolors.OK
                        HTMLcolor = "green"
                        tradeAction = "Vender"
                        urlAction = "inputCurrency"
                    elif percentageDiff <= self.loseTrigger:
                        color = bcolors.ERR
                        HTMLcolor = "red"
                        tradeAction = "Comprar"
                        urlAction = "outputCurrency"
                    else:
                        continue

                    tempRow = {}

                    tempRow["percentageDiff"] = percentageDiff

                    for x, y in row.items():
                        tempRow[x] = y

                    tempDf = pd.DataFrame([tempRow])

                    tempDf.to_csv(self.moveHistoryCsv, index=False, columns=list(tempDf), mode="a", header=writeHeaders)
                    writeHeaders = False

                    tokens = self.getTokens(cryptoSlug=self.data[row[self.idDesc]][self.slugDesc])

                    if len(tokens) == 0:
                        tokensDesc = ""
                    
                    else:
                        if self.isSendEmails:
                            self.sendEmails(tradeAction=tradeAction, urlAction=urlAction, cryptoData=self.data[row[self.idDesc]], percentageDiff=percentageDiff, color=HTMLcolor, tokens=tokens)

                        tokensDesc = f"// {tokens}"

                    printInfo(f"{percentageDiff} % --- {tradeAction} la moneda {self.data[row[self.idDesc]][self.symbolNameDesc]} ({self.data[row[self.idDesc]][self.symbolDesc]})"
                    + f" // Precio = {self.data[row[self.idDesc]][self.priceDesc]} $, Antes = {self.data[row[self.idDesc]][self.prevPriceDesc]} $ {tokensDesc}", color)

            counter += 1

            if counter % 100 == 0:
                printInfo(f"--- For Loop: {counter}", bcolors.WARN)

            time.sleep(self.delay)


    def sendEmails(self, tradeAction, urlAction, cryptoData, percentageDiff, color, tokens):

        while True:
            try:
                ssl_context = ssl.create_default_context()
                service = smtplib.SMTP_SSL(self.smtp_server_domain_name, self.port, context=ssl_context)
                service.login(self.sender_mail, self.password)

                break

            except:
                time.sleep(self.delay)

        # Set email subject
        subject = f"{tradeAction} moneda {cryptoData[self.symbolNameDesc]} con alias {cryptoData[self.symbolDesc]}"

        # CoinMarketCap URL to see how the coin is going
        coinMarketCapUrl = self.cryptoBaseUrl + cryptoData[self.slugDesc]

        # Start preparing the content of the email
        content = f"""<h2 style="color: {color};">Ha variado {percentageDiff} %</h2>
        <h3>Precio en dolares:</h3>
        <h3>Ahora = {cryptoData[self.priceDesc]}</h3>
        <h3>Antes = {cryptoData[self.prevPriceDesc]}</h3>
        <h3><a href="{coinMarketCapUrl}">Análisis en CoinMarketCap</a></h3>
        """

        for platform, token in tokens.items():

            if platform == self.binanceSmartChainDesc:
                baseUrl = self.pancakeSwapBaseUrl
            elif platform == self.ethereumDesc:
                baseUrl = self.uniswapBaseUrl
            else:
                continue

            # Set URL to buy or sell coins
            tradeUrl = baseUrl + urlAction + "=" + token

            # Add trading links to buy or sell
            content += f"""<h3><a href="{tradeUrl}">Comprar en {platform} con token {token}</a></h3>
            """
            
        content = MIMEText(content, "html")
        
        for email in self.recipientEmails:

            while True:
                try:
                    result = service.sendmail(self.sender_mail, email, f"Subject: {subject}\n{content}")
                    break

                except:
                    time.sleep(self.delay)

        service.quit()
        