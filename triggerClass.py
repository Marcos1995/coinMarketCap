import requests
import pandas as pd
import datetime as dt
import os
import time
import urllib.request, json
import bcolors
from bs4 import BeautifulSoup
from uniswap import Uniswap
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tempfile import NamedTemporaryFile
import shutil
import csv
from twilio.rest import Client
import re
from web3 import Web3
import time

# ------------------------------------------------------------------------------------

def formatPercentages(val):
    return round((val - 1) * 100, 4)

def printInfo(desc, color=""):
    print(dt.datetime.now(), "//", color, desc, bcolors.END)

def getPrivateKey():
    with open("/home/pi/Documents/config.txt") as mytxt:
        for line in mytxt:
            return line


class cmc:

    def __init__(self, sellTrigger, buyTrigger, sendNotifications, isSimulation, moveHistoryCsv, delay):

        self.sellTrigger = sellTrigger
        self.buyTrigger = buyTrigger
        self.sendNotifications = sendNotifications
        self.isSimulation = isSimulation
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

        # Trading variables
        self.bsc = "https://bsc-dataseed.binance.org/"

        #pancakeswap router
        self.panRouterContractAddress = '0x10ED43C718714eb63d5aA57B78B54704E256024E'

        #pancakeswap router abi 
        self.panabi = '[{"inputs":[{"internalType":"address","name":"_factory","type":"address"},{"internalType":"address","name":"_WETH","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"amountADesired","type":"uint256"},{"internalType":"uint256","name":"amountBDesired","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountTokenDesired","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountIn","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountOut","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsIn","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"reserveA","type":"uint256"},{"internalType":"uint256","name":"reserveB","type":"uint256"}],"name":"quote","outputs":[{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETHSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermit","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermitSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityWithPermit","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapETHForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETHSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]'

        # Abi for Token to sell - all we need from here is the balanceOf & approve function can replace with shortABI
        self.sellAbi = '[{"inputs":[{"internalType":"string","name":"_NAME","type":"string"},{"internalType":"string","name":"_SYMBOL","type":"string"},{"internalType":"uint256","name":"_DECIMALS","type":"uint256"},{"internalType":"uint256","name":"_supply","type":"uint256"},{"internalType":"uint256","name":"_txFee","type":"uint256"},{"internalType":"uint256","name":"_lpFee","type":"uint256"},{"internalType":"uint256","name":"_MAXAMOUNT","type":"uint256"},{"internalType":"uint256","name":"SELLMAXAMOUNT","type":"uint256"},{"internalType":"address","name":"routerAddress","type":"address"},{"internalType":"address","name":"tokenOwner","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"minTokensBeforeSwap","type":"uint256"}],"name":"MinTokensBeforeSwapUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"tokensSwapped","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"ethReceived","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"tokensIntoLiqudity","type":"uint256"}],"name":"SwapAndLiquify","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"bool","name":"enabled","type":"bool"}],"name":"SwapAndLiquifyEnabledUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[],"name":"_liquidityFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_maxTxAmount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_taxFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"claimTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"tAmount","type":"uint256"}],"name":"deliver","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"excludeFromFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"excludeFromReward","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"geUnlockTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"includeInFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"includeInReward","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"isExcludedFromFee","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"isExcludedFromReward","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"time","type":"uint256"}],"name":"lock","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"numTokensSellToAddToLiquidity","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tAmount","type":"uint256"},{"internalType":"bool","name":"deductTransferFee","type":"bool"}],"name":"reflectionFromToken","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"liquidityFee","type":"uint256"}],"name":"setLiquidityFeePercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"maxTxPercent","type":"uint256"}],"name":"setMaxTxPercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"swapNumber","type":"uint256"}],"name":"setNumTokensSellToAddToLiquidity","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bool","name":"_enabled","type":"bool"}],"name":"setSwapAndLiquifyEnabled","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"taxFee","type":"uint256"}],"name":"setTaxFeePercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"swapAndLiquifyEnabled","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"rAmount","type":"uint256"}],"name":"tokenFromReflection","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalFees","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"uniswapV2Pair","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"uniswapV2Router","outputs":[{"internalType":"contract IUniswapV2Router02","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"unlock","outputs":[],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]'

        self.bnbAmountToBuy = 0.01
        self.wbnbContract = "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c"

        self.senderAddress = "0xa9eC6E2129267f01a2E772E208F8b0Ed802748D0"
        self.privateKey = getPrivateKey()

        print(self.privateKey)

        # self.uniswapConnection()


    def uniswapConnection(self):

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

                    if self.data[row[self.idDesc]][self.lastUpdatedDesc] == row[self.lastUpdatedDesc]:
                        continue

                    self.data[row[self.idDesc]][self.prevPriceDesc] = self.data[row[self.idDesc]][self.priceDesc]
                    self.data[row[self.idDesc]][self.prevLastUpdatedDesc] = self.data[row[self.idDesc]][self.lastUpdatedDesc]
                    self.data[row[self.idDesc]][self.priceDesc] = row[self.priceDesc]
                    self.data[row[self.idDesc]][self.lastUpdatedDesc] = row[self.lastUpdatedDesc]
                    self.data[row[self.idDesc]][self.percentChange1hDesc] = row[self.percentChange1hDesc]

                    if self.data[row[self.idDesc]][self.priceDesc] == 0 or self.data[row[self.idDesc]][self.prevPriceDesc] == 0:
                        continue

                    # Calculate diff percentage
                    percengeDiffWoFormat = self.data[row[self.idDesc]][self.priceDesc] / self.data[row[self.idDesc]][self.prevPriceDesc]
                    percentageDiff = formatPercentages(percengeDiffWoFormat)

                    # If we should buy or sell a crypto
                    if percentageDiff >= self.sellTrigger and row[self.idDesc] in csvSymbolsNotSold: # sell

                        color = bcolors.OK
                        HTMLcolor = "green"
                        tradeAction = "Vender"
                        urlAction = "inputCurrency"
                        isToBuy = False

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


                    elif percentageDiff <= self.buyTrigger and percentageDiff <= self.data[row[self.idDesc]][self.percentChange1hDesc] and row[self.idDesc] not in csvSymbolsNotSold: # buy
                        
                        color = bcolors.ERR
                        HTMLcolor = "red"
                        tradeAction = "Comprar"
                        urlAction = "outputCurrency"
                        isToBuy = True

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

                        if not self.isSimulation:
                            token = tokens[self.binanceSmartChainDesc]

                            print(token)

                            if isToBuy:
                                self.buyToken(token=token)
                            else:
                                self.sellToken(token=token)

                        
                        if self.sendNotifications:
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
            
        emailContent = MIMEText(emailContent, "html")
        whatsappContent = re.sub('<[^<]+?>', '', whatsappContent)
        whatsappContent = re.sub('  +', '', whatsappContent)

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

            if self.bscscanDesc in href:
                platform = self.binanceSmartChainDesc
            else:
                continue

            """
            if self.etherscanDesc in href:
                platform = self.ethereumDesc
            """

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
        
            # print(message.sid)


    def buyToken(self, token):

        while True:

            try:

                web3 = Web3(Web3.HTTPProvider(self.bsc))

                print(web3.isConnected())
                
                balance = web3.eth.get_balance(self.senderAddress)
                humanReadable = web3.fromWei(balance,'ether')

                printInfo(f"BNB amount: {humanReadable}", bcolors.WARN)
                
                #Contract Address of Token we want to buy
                tokenToBuy = web3.toChecksumAddress(token)        # web3.toChecksumAddress("0x6615a63c260be84974166a5eddff223ce292cf3d")
                spend = web3.toChecksumAddress(self.wbnbContract) # wbnb contract
                
                #Setup the PancakeSwap contract
                contract = web3.eth.contract(address=self.panRouterContractAddress, abi=self.panabi)

                nonce = web3.eth.get_transaction_count(self.senderAddress)
                
                start = time.time()

                """
                print(tokenToBuy)
                print(spend)
                print(contract)
                print(nonce)
                print(start)
                """

                pancakeswap2_txn = contract.functions.swapExactETHForTokensSupportingFeeOnTransferTokens( # swapExactETHForTokens
                0, # set to 0, or specify minimum amount of tokeny you want to receive - consider decimals!!!
                [spend,tokenToBuy],
                self.senderAddress,
                (int(time.time()) + 1000000)
                ).buildTransaction({
                'from': self.senderAddress,
                'value': web3.toWei(self.bnbAmountToBuy,'ether'), # This is the Token(BNB) amount you want to Swap from
                'gas': 250000,
                'gasPrice': web3.toWei('5','gwei'),
                'nonce': nonce,
                })
                    
                signed_txn = web3.eth.account.sign_transaction(pancakeswap2_txn, private_key=self.privateKey)
                tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

                print(web3.toHex(tx_token))

                balance = web3.eth.get_balance(self.senderAddress)
                humanReadable = web3.fromWei(balance,'ether')

                break

            except:
                printInfo("Error en buyToken()", bcolors.ERRMSG)
                time.sleep(self.delay)


    def sellToken(self, token):

        while True:

            try:

                web3 = Web3(Web3.HTTPProvider(self.bsc))

                print(web3.isConnected())

                sender_address = self.senderAddress #TokenAddress of holder
                spend = web3.toChecksumAddress(self.wbnbContract)  #WBNB Address


                #Get BNB Balance
                balance = web3.eth.get_balance(sender_address)
                humanReadable = web3.fromWei(balance,'ether')

                printInfo(f"BNB amount: {humanReadable}", bcolors.WARN)
                
                #Contract id is the new token we are swaping to
                #contract_id = web3.toChecksumAddress("0xc9849e6fdb743d08faee3e34dd2d1bc69ea11a51")
                contract_id = web3.toChecksumAddress(token)
                
                #Setup the PancakeSwap contract
                contract = web3.eth.contract(address=self.panRouterContractAddress, abi=self.panabi)

                #Create token Instance for Token
                sellTokenContract = web3.eth.contract(contract_id, abi=self.sellAbi)

                #Get Token Balance
                balance = sellTokenContract.functions.balanceOf(sender_address).call()
                symbol = sellTokenContract.functions.symbol().call()
                readable = web3.fromWei(balance,'ether')
                print("Balance: " + str(readable) + " " + symbol)

                #Enter amount of token to sell
                tokenValue = web3.toWei(readable, 'ether')

                #Approve Token before Selling
                tokenValue2 = web3.fromWei(tokenValue, 'ether')
                start = time.time()
                approve = sellTokenContract.functions.approve(self.panRouterContractAddress, balance).buildTransaction({
                            'from': sender_address,
                            'gasPrice': web3.toWei('5','gwei'),
                            'nonce': web3.eth.get_transaction_count(sender_address),
                            })

                signed_txn = web3.eth.account.sign_transaction(approve, private_key=self.privateKey)
                tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
                print("Approved: " + web3.toHex(tx_token))

                # Wait after approve 10 seconds before sending transaction
                time.sleep(10)

                print(f"Swapping {tokenValue2} {symbol} for BNB")
                # Swaping exact Token for ETH 

                pancakeswap2_txn = contract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens( # swapExactTokensForETH
                            tokenValue ,0, 
                            [contract_id, spend],
                            sender_address,
                            (int(time.time()) + 1000000)

                            ).buildTransaction({
                            'from': sender_address,
                            'gasPrice': web3.toWei('5','gwei'),
                            'nonce': web3.eth.get_transaction_count(sender_address),
                            })
                    
                signed_txn = web3.eth.account.sign_transaction(pancakeswap2_txn, private_key=self.privateKey)
                tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
                print(f"Sold {symbol}: " + web3.toHex(tx_token))

                break

            except:
                printInfo("Error en sellToken()", bcolors.ERRMSG)
                time.sleep(self.delay)
