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

def printInfo(val, color=""):
    print(dt.datetime.now(), "//", color, val, bcolors.END)

class cmc:

    def __init__(self, gainTrigger, loseTrigger, moveHistoryCsv, delay):

        self.gainTrigger = gainTrigger
        self.loseTrigger = loseTrigger
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

        self.lastUpdatesDesc = "lastUpdated"

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


    def sendEmail(self, subject, content):
        ssl_context = ssl.create_default_context()
        service = smtplib.SMTP_SSL(self.smtp_server_domain_name, self.port, context=ssl_context)
        service.login(self.sender_mail, self.password)

        for email in self.recipientEmails:
            result = service.sendmail(self.sender_mail, email, f"Subject: {subject}\n{content}")

        service.quit()

    # Get crypto coin tokens by searching in coinmarketcap websites (not ideal)
    def getTokens(self, cryptoSlug="dashsports"):

        # Dict to be returned
        tokens = {}

        allHrefs = []

        cryptoUrl = self.cryptoBaseUrl + cryptoSlug

        html_page = urllib.request.urlopen(cryptoUrl)
        soup = BeautifulSoup(html_page, "html.parser")

        for link in soup.findAll('a'):
            href = str(link.get('href'))

            if self.tokenUrl in href:
                allHrefs.append(href)

        allHrefs = list(dict.fromkeys(allHrefs))

        print(allHrefs)

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
            
            print(tokens)

        return tokens
    