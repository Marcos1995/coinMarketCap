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
from tempfile import NamedTemporaryFile
import shutil
import csv
from twilio.rest import Client
import re

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
        self.circulatingSupplyDesc = "circulatingSupply"
        self.totalSupplyDesc = "totalSupply"
        self.maxSupplyDesc = "maxSupply"
        self.isActiveDesc = "isActive"
        self.dateAddedDesc = "dateAdded"
        self.columnToExpand = "quotes"

        self.selectDataColumns = [
            self.idDesc, self.nameDesc, self.symbolDesc, self.slugDesc, self.circulatingSupplyDesc,
            self.totalSupplyDesc, self.maxSupplyDesc, self.isActiveDesc, self.dateAddedDesc, self.columnToExpand
        ]

        self.priceDesc = "price"
        self.prevPriceDesc = "prevPrice"

        self.percentChange1hDesc = "percentChange1h"

        self.datetimeDesc = "datetime"
        self.prevDatetimeDesc = "prevDatetime"

        self.lastUpdatedDesc = "lastUpdated"
        self.prevLastUpdatedDesc = "prevLastUpdated"

        self.percentageDiffDesc = "percentageDiff"
        self.sellPercentageDiffDesc = "sellPercentageDiff"
        self.isSoldDesc = "isSold"

        self.separator = ","

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

        # Twilio
        self.account_sid = 'AC5acbac010999dc20b065ce163ddd0c2b' 
        self.auth_token = '41342f1e7a6b6359c22607b8f28bdf13' 

        self.mobileNumbers = [
            "+34634553557",
            "+34635453357"
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


    def core(self):

        # Instantiate list
        csvSymbolsNotSold = []

        counter = 0

        while True:

            # Get .csv symbols not sold
            if os.path.exists(self.moveHistoryCsv):
                csvSymbolsNotSold = self.getCsvSymbolsNotSold()
                # print(csvSymbolsNotSold)
                writeHeaders = False
            else:
                writeHeaders = True
                # printInfo(f"No existe el fichero {self.moveHistoryCsv}", bcolors.WARN)

            # Get API data
            df = self.getData()

            # For each dataframe row
            for i, row in df.iterrows():

                # If "current" values are not set
                if self.data.get(row[self.idDesc], {self.priceDesc: -1})[self.priceDesc] == -1:

                    self.data.setdefault(row[self.idDesc], {})[self.symbolNameDesc] = row[self.symbolNameDesc]
                    self.data[row[self.idDesc]][self.symbolDesc] = row[self.symbolDesc]
                    self.data[row[self.idDesc]][self.slugDesc] = row[self.slugDesc]
                    self.data[row[self.idDesc]][self.priceDesc] = row[self.priceDesc]
                    self.data[row[self.idDesc]][self.lastUpdatedDesc] = row[self.lastUpdatedDesc]
                    self.data[row[self.idDesc]][self.percentChange1hDesc] = row[self.percentChange1hDesc]

                # If "previous" values are set
                else:

                    if self.data[row[self.idDesc]][self.lastUpdatedDesc] == row[self.lastUpdatedDesc] or (self.data[row[self.idDesc]][self.priceDesc] == 0 and row[self.priceDesc] == 0):
                        continue

                    self.data[row[self.idDesc]][self.prevPriceDesc] = self.data[row[self.idDesc]][self.priceDesc]
                    self.data[row[self.idDesc]][self.prevLastUpdatedDesc] = self.data[row[self.idDesc]][self.lastUpdatedDesc]
                    self.data[row[self.idDesc]][self.priceDesc] = row[self.priceDesc]
                    self.data[row[self.idDesc]][self.lastUpdatedDesc] = row[self.lastUpdatedDesc]
                    self.data[row[self.idDesc]][self.percentChange1hDesc] = row[self.percentChange1hDesc]

                    if self.data[row[self.idDesc]][self.prevPriceDesc] == 0:
                        prevPrice = 1 / self.gainTrigger
                    else:
                        prevPrice = self.data[row[self.idDesc]][self.prevPriceDesc]

                    # Calculate diff percentage
                    percengeDiffWoFormat = self.data[row[self.idDesc]][self.priceDesc] / prevPrice
                    percentageDiff = formatPercentages(percengeDiffWoFormat)

                    # If we should buy or sell a crypto
                    if percentageDiff >= self.gainTrigger and row[self.idDesc] in csvSymbolsNotSold: # sell

                        color = bcolors.OK
                        HTMLcolor = "green"
                        tradeAction = "Vender"
                        urlAction = "inputCurrency"

                        # ------------------------------------------------------------------

                        # Update .csv setting the new cells value
                        tempfile = NamedTemporaryFile(mode='w', delete=False)

                        df = pd.read_csv(self.moveHistoryCsv, sep=self.separator)

                        with open(self.moveHistoryCsv, 'r', newline='') as csvfile, tempfile:
                            reader = csv.DictReader(csvfile, fieldnames=list(df), delimiter=self.separator)
                            writer = csv.DictWriter(tempfile, fieldnames=list(df), delimiter=self.separator, lineterminator='\n')
                            for r in reader:

                                if r[self.symbolDesc] == self.symbolDesc:
                                    writer.writerow(r)
                                    continue

                                if int(r[self.idDesc]) == int(row[self.idDesc]) and int(r[self.isSoldDesc]) == 0:
                                    r[self.isSoldDesc], r[self.sellPercentageDiffDesc] = 1, percentageDiff

                                writer.writerow(r)

                        shutil.move(tempfile.name, self.moveHistoryCsv)


                    elif percentageDiff <= self.loseTrigger and percentageDiff <= self.data[row[self.idDesc]][self.percentChange1hDesc] and row[self.idDesc] not in csvSymbolsNotSold: # buy

                        color = bcolors.ERR
                        HTMLcolor = "red"
                        tradeAction = "Comprar"
                        urlAction = "outputCurrency"

                        # -------------------------------------------------------------------

                        # Prepare data to insert in .csv file
                        tempRow = {}
                        tempRow[self.percentageDiffDesc] = percentageDiff
                        tempRow[self.sellPercentageDiffDesc] = None
                        tempRow[self.isSoldDesc] = 0

                        for x, y in row.items():
                            tempRow[x] = y

                        tempDf = pd.DataFrame([tempRow])

                        tempDf.to_csv(self.moveHistoryCsv, index=False, columns=list(tempDf), mode="a", header=writeHeaders)
                        writeHeaders = False

                    else: # Nothing to do, so let's continue with the other coin
                        continue

                    tokens = self.getTokens(cryptoSlug=self.data[row[self.idDesc]][self.slugDesc])

                    if len(tokens) == 0:
                        tokensDesc = ""
                    
                    else:
                        if self.isSendEmails:
                            self.sendEmails(tradeAction=tradeAction, urlAction=urlAction, cryptoData=self.data[row[self.idDesc]], percentageDiff=percentageDiff, color=HTMLcolor, tokens=tokens)

                        tokensDesc = f"// {tokens}"

                    printInfo(f"{percentageDiff} % --- {tradeAction} la moneda {self.data[row[self.idDesc]][self.symbolNameDesc]} ({self.data[row[self.idDesc]][self.symbolDesc]}"
                    + f" - {row[self.idDesc]}) // Precio = {self.data[row[self.idDesc]][self.priceDesc]} $, Antes = {self.data[row[self.idDesc]][self.prevPriceDesc]} $ {tokensDesc}", color)

            counter += 1

            if counter % 100 == 0:
                printInfo(f"--- For Loop: {counter}", bcolors.WARN)

            time.sleep(self.delay)


    def getCsvSymbolsNotSold(self):

        csvSymbolsNotSold = []

        with open(self.moveHistoryCsv) as f:

            lis = [line.split(sep=self.separator) for line in f]  # create a list of lists

            for i, row in enumerate(lis):
                if i == 0:
                    idColumnIndex = row.index(self.idDesc)
                    isSoldColumnIndex = row.index(self.isSoldDesc)
                else:
                    if int(row[isSoldColumnIndex]) == 0:
                        csvSymbolsNotSold.append(int(row[idColumnIndex]))

        csvSymbolsNotSold = list(dict.fromkeys(csvSymbolsNotSold))

        # if len(csvSymbolsNotSold) > 0:
        #     print(csvSymbolsNotSold)

        return csvSymbolsNotSold


    def getData(self):

        while True:
            try:
                with urllib.request.urlopen(self.allCoinMarketCapCoinsUrl) as url:
                    rawData = json.loads(url.read().decode())

                break
            except:
                printInfo("Error obteniendo datos en getData()", bcolors.ERRMSG)
                time.sleep(self.delay)

        for i, data in rawData.items():
            for desc, listOfDicts in data.items():

                if desc.endswith(self.listDesc):
                    
                    df = pd.DataFrame(listOfDicts)
                    
                    # Select few columns only
                    df = df[self.selectDataColumns]
                    
                    # df = df.drop(['tags', 'cmcRank', 'marketPairCount', 'lastUpdated', 'isAudited', 'platform', 'auditInfoList'], axis = 1)

                    df = df.rename(columns = {self.nameDesc: self.symbolNameDesc})

                    # Prepare column to expand
                    df[self.columnToExpand] = df[self.columnToExpand].apply(lambda cell: cell[0])

                    # Expand column in df
                    df = df.drop(self.columnToExpand, axis=1).join(pd.DataFrame(df[self.columnToExpand].values.tolist()))

        return df


    def sendEmails(self, tradeAction, urlAction, cryptoData, percentageDiff, color, tokens):

        while True:
            try:
                ssl_context = ssl.create_default_context()
                service = smtplib.SMTP_SSL(self.smtp_server_domain_name, self.port, context=ssl_context)
                service.login(self.sender_mail, self.password)

                break

            except:
                printInfo("Error obteniendo datos en sendEmails()", bcolors.ERRMSG)
                time.sleep(self.delay)

        # Set email subject
        subject = f"{tradeAction} moneda {cryptoData[self.symbolNameDesc]} con alias {cryptoData[self.symbolDesc]}"

        # CoinMarketCap URL to see how the coin is going
        coinMarketCapUrl = self.cryptoBaseUrl + cryptoData[self.slugDesc]

        coinMarketCapDesc = "Análisis en CoinMarketCap"

        # Start preparing the content of the email
        content = f"""
        <h2 style="color: {color};">Ha variado {percentageDiff} %</h2>
        <h3>Precio en dolares:</h3>
        <h3>Ahora = {cryptoData[self.priceDesc]}</h3>
        <h3>Antes = {cryptoData[self.prevPriceDesc]}</h3>
        """

        emailContent = content + f"""<h3><a href="{coinMarketCapUrl}">{coinMarketCapDesc}</a></h3>
        """
        whatsappContent = subject + content + f"""
        {coinMarketCapDesc}
        {coinMarketCapUrl}
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

            desc = f"{tradeAction} en {platform} con token {token}"

            # Add trading links to buy or sell
            emailContent += f"""<h3><a href="{tradeUrl}">{desc}</a></h3>
            """

            whatsappContent += f"""
            {desc}
            {tradeUrl}
            """

        print(emailContent)
            
        emailContent = MIMEText(emailContent, "html")
        whatsappContent = re.sub('<[^<]+?>', '', whatsappContent)
        whatsappContent = re.sub('  +', '', whatsappContent)

        print(whatsappContent)

        # Send whatsapp message
        self.sendWhatsapp(message=whatsappContent)
        
        for email in self.recipientEmails:

            while True:
                try:
                    result = service.sendmail(self.sender_mail, email, f"Subject: {subject}\n{emailContent}")
                    break

                except:
                    printInfo("Error enviando email en sendEmails()", bcolors.ERRMSG)
                    time.sleep(self.delay)

        service.quit()

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
                printInfo("Error obteniendo datos en getTokens()", bcolors.ERRMSG)
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

        # Sort dict
        if len(tokens) > 0:
            tokens = {key: val for key, val in sorted(tokens.items(), key = lambda ele: ele[0])}

        return tokens
    

    def sendWhatsapp(self, message):

        client = Client(self.account_sid, self.auth_token)

        for number in self.mobileNumbers:
        
            message = client.messages.create( 
                                        from_='whatsapp:+14155238886',  
                                        body=message,      
                                        to='whatsapp:' + number 
                                    ) 
        
            print(message.sid)