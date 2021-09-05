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
from concurrent.futures import ThreadPoolExecutor

# ------------------------------------------------------------------------------------

def formatPercentages(val):
    return round((val - 1) * 100, 4)

def boolToInt(val):
    if val == "True" or val == True:
        res = 1
    elif val == "False" or val == False:
        res = 0
    else:
        res = -1

    return res

def printInfo(desc, color=""):
    print(dt.datetime.now(), "//", color, desc, bcolors.END)

def getPrivateKey():
    with open("/home/pi/Documents/config.txt") as mytxt:
        for line in mytxt:
            return line


class cmc:

    def __init__(self, buyTrigger, sellTrigger, isTrading: bool, sendNotifications: bool, tradingHistoryCsv, bscContractsCsv, delay):

        # Check parameters
        if not isinstance(buyTrigger, (int, float)):
            printInfo(f"El parametro buyTrigger ha de ser de tipo int o float", bcolors.ERRMSG)
            exit()

        elif not isinstance(sellTrigger, (int, float)):
            printInfo(f"El parametro sellTrigger ha de ser de tipo int o float", bcolors.ERRMSG)
            exit()

        elif not isinstance(isTrading, bool):
            printInfo(f"El parametro isTrading ha de ser de tipo bool", bcolors.ERRMSG)
            exit()

        elif not isinstance(sendNotifications, bool):
            printInfo(f"El parametro sendNotification ha de ser de tipo bool", bcolors.ERRMSG)
            exit()

        elif not isinstance(tradingHistoryCsv, str) or not tradingHistoryCsv.endswith(".csv"):
            printInfo(f"El parametro tradingHistoryCsv ha de ser de tipo str acabado en .csv", bcolors.ERRMSG)
            exit()

        elif not isinstance(bscContractsCsv, str) or not bscContractsCsv.endswith(".csv"):
            printInfo(f"El parametro bscContractsCsv ha de ser de tipo str acabado en .csv", bcolors.ERRMSG)
            exit()

        elif not isinstance(delay, (int, float)):
            printInfo(f"El parametro delay ha de ser de tipo int o float", bcolors.ERRMSG)
            exit()

        # Assign parameters to self values
        self.buyTrigger = buyTrigger
        self.sellTrigger = sellTrigger
        self.sendNotifications = sendNotifications
        self.isTrading = isTrading
        self.tradingHistoryCsv = tradingHistoryCsv
        self.bscContractsCsv = bscContractsCsv
        self.delay = delay

        self.bscContractsDf = pd.DataFrame()
        self.dfCsvSymbolsNotSold = pd.DataFrame()
        self.writeTradingHistoryHeaders = True

        self.csvBscContractTokens = []
        self.csvSymbolsNotSold = []

        self.cryptoCurrencyListDesc = "cryptoCurrencyList"
        self.statusDesc = "status"
        self.timestampDesc = "timestamp"

        self.timestamp = None
        self.prevTimestamp = None

        self.allCoinMarketCapCoinsUrl = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing?start=1&limit=10000&convert=USD&cryptoType=all&tagType=all&audited=false&tagSlugs=binance-smart-chain"
        self.checkCoinMarketCapTimestampUrl = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing?limit=0"
        self.cryptoBaseUrl = "https://coinmarketcap.com/currencies/"

        self.uniswapBaseUrl = "https://app.uniswap.org/#/swap?"
        self.pancakeSwapBaseUrl = "https://exchange.pancakeswap.finance/#/swap?"

        self.bscscanTransactionBaseUrl = "https://www.bscscan.com/tx/"

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
        self.sellPriceDesc = "sellPrice"

        self.marketCapDesc = "marketCap"
        self.fullyDilluttedMarketCapDesc = "fullyDilluttedMarketCap"

        self.percentChange1hDesc = "percentChange1h"

        self.datetimeDesc = "datetime"
        self.sellDatetimeDesc = "sellDatetime"

        self.percentageDiffDesc = "percentageDiff"
        self.sellPercentageDiffDesc = "sellPercentageDiff"
        self.isSoldDesc = "isSold"
        self.isTradingDesc = "isTrading"

        printInfo(f"{self.isTradingDesc} = {self.isTrading}", bcolors.WARN)

        self.separator = ","

        self.bscscanDesc = "bscscan"
        self.etherscanDesc = "etherscan"
        
        self.ethereumDesc = "Ethereum"
        self.binanceSmartChainDesc = "BinanceSmartChain"

        self.bscContractDesc = "bscContract"

        self.data = {}

        # Send emails configuration
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
        self.bsc = "https://bsc-dataseed1.binance.org" # "https://bsc-dataseed.binance.org/"

        self.web3 = Web3(Web3.HTTPProvider(self.bsc))

        #pancakeswap router
        self.panRouterContractAddress = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
        self.getPriceAddress = "0xBCfCcbde45cE874adCB698cC183deBcF17952812"

        #pancakeswap router abi 
        self.panabi = '[{"inputs":[{"internalType":"address","name":"_factory","type":"address"},{"internalType":"address","name":"_WETH","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"amountADesired","type":"uint256"},{"internalType":"uint256","name":"amountBDesired","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountTokenDesired","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountIn","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountOut","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsIn","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"reserveA","type":"uint256"},{"internalType":"uint256","name":"reserveB","type":"uint256"}],"name":"quote","outputs":[{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETHSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermit","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermitSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityWithPermit","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapETHForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETHSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]'

        # Abi for Token to sell - all we need from here is the balanceOf & approve function can replace with shortABI
        self.sellAbi = '[{"inputs":[{"internalType":"string","name":"_NAME","type":"string"},{"internalType":"string","name":"_SYMBOL","type":"string"},{"internalType":"uint256","name":"_DECIMALS","type":"uint256"},{"internalType":"uint256","name":"_supply","type":"uint256"},{"internalType":"uint256","name":"_txFee","type":"uint256"},{"internalType":"uint256","name":"_lpFee","type":"uint256"},{"internalType":"uint256","name":"_MAXAMOUNT","type":"uint256"},{"internalType":"uint256","name":"SELLMAXAMOUNT","type":"uint256"},{"internalType":"address","name":"routerAddress","type":"address"},{"internalType":"address","name":"tokenOwner","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"minTokensBeforeSwap","type":"uint256"}],"name":"MinTokensBeforeSwapUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"tokensSwapped","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"ethReceived","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"tokensIntoLiqudity","type":"uint256"}],"name":"SwapAndLiquify","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"bool","name":"enabled","type":"bool"}],"name":"SwapAndLiquifyEnabledUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[],"name":"_liquidityFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_maxTxAmount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_taxFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"claimTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"tAmount","type":"uint256"}],"name":"deliver","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"excludeFromFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"excludeFromReward","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"geUnlockTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"includeInFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"includeInReward","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"isExcludedFromFee","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"isExcludedFromReward","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"time","type":"uint256"}],"name":"lock","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"numTokensSellToAddToLiquidity","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tAmount","type":"uint256"},{"internalType":"bool","name":"deductTransferFee","type":"bool"}],"name":"reflectionFromToken","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"liquidityFee","type":"uint256"}],"name":"setLiquidityFeePercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"maxTxPercent","type":"uint256"}],"name":"setMaxTxPercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"swapNumber","type":"uint256"}],"name":"setNumTokensSellToAddToLiquidity","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bool","name":"_enabled","type":"bool"}],"name":"setSwapAndLiquifyEnabled","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"taxFee","type":"uint256"}],"name":"setTaxFeePercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"swapAndLiquifyEnabled","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"rAmount","type":"uint256"}],"name":"tokenFromReflection","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalFees","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"uniswapV2Pair","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"uniswapV2Router","outputs":[{"internalType":"contract IUniswapV2Router02","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"unlock","outputs":[],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]'

        self.getPriceABI = '[{"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"token0","type":"address"},{"indexed":true,"internalType":"address","name":"token1","type":"address"},{"indexed":false,"internalType":"address","name":"pair","type":"address"},{"indexed":false,"internalType":"uint256","name":"","type":"uint256"}],"name":"PairCreated","type":"event"},{"constant":true,"inputs":[],"name":"INIT_CODE_PAIR_HASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"allPairs","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"allPairsLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"}],"name":"createPair","outputs":[{"internalType":"address","name":"pair","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"feeTo","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"feeToSetter","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"getPair","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_feeTo","type":"address"}],"name":"setFeeTo","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"name":"setFeeToSetter","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]'

        self.getReservedABI = '[{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1","type":"uint256"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"Burn","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1","type":"uint256"}],"name":"Mint","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0In","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1In","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount0Out","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1Out","type":"uint256"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"Swap","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint112","name":"reserve0","type":"uint112"},{"indexed":false,"internalType":"uint112","name":"reserve1","type":"uint112"}],"name":"Sync","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"constant":true,"inputs":[],"name":"DOMAIN_SEPARATOR","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"MINIMUM_LIQUIDITY","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"PERMIT_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"burn","outputs":[{"internalType":"uint256","name":"amount0","type":"uint256"},{"internalType":"uint256","name":"amount1","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getReserves","outputs":[{"internalType":"uint112","name":"_reserve0","type":"uint112"},{"internalType":"uint112","name":"_reserve1","type":"uint112"},{"internalType":"uint32","name":"_blockTimestampLast","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_token0","type":"address"},{"internalType":"address","name":"_token1","type":"address"}],"name":"initialize","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"kLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"mint","outputs":[{"internalType":"uint256","name":"liquidity","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"nonces","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"permit","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"price0CumulativeLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"price1CumulativeLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"skim","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"amount0Out","type":"uint256"},{"internalType":"uint256","name":"amount1Out","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"swap","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"sync","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"token0","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"token1","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"}]'

        #self.pancakeSwapAbi =  [{"inputs":[{"internalType":"address","name":"_factory","type":"address"},{"internalType":"address","name":"_WETH","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"amountADesired","type":"uint256"},{"internalType":"uint256","name":"amountBDesired","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountTokenDesired","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountIn","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountOut","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsIn","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"reserveA","type":"uint256"},{"internalType":"uint256","name":"reserveB","type":"uint256"}],"name":"quote","outputs":[{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETHSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermit","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermitSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityWithPermit","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapETHForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETHSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}];
        self.tokenAbi = '[{"inputs":[{"internalType":"string","name":"_name","type":"string"},{"internalType":"string","name":"_symbol","type":"string"},{"internalType":"uint256","name":"_decimals","type":"uint256"},{"internalType":"uint256","name":"_supply","type":"uint256"},{"internalType":"uint256","name":"_txFee","type":"uint256"},{"internalType":"uint256","name":"_burnFee","type":"uint256"},{"internalType":"uint256","name":"_charityFee","type":"uint256"},{"internalType":"address","name":"_FeeAddress","type":"address"},{"internalType":"address","name":"tokenOwner","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[],"name":"FeeAddress","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_BURN_FEE","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_CHARITY_FEE","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_TAX_FEE","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_value","type":"uint256"}],"name":"burn","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"tAmount","type":"uint256"}],"name":"deliver","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"excludeAccount","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"includeAccount","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"isCharity","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"isExcluded","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mint","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tAmount","type":"uint256"},{"internalType":"bool","name":"deductTransferFee","type":"bool"}],"name":"reflectionFromToken","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"setAsCharityAccount","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"rAmount","type":"uint256"}],"name":"tokenFromReflection","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalBurn","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalCharity","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalFees","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_txFee","type":"uint256"},{"internalType":"uint256","name":"_burnFee","type":"uint256"},{"internalType":"uint256","name":"_charityFee","type":"uint256"}],"name":"updateFee","outputs":[],"stateMutability":"nonpayable","type":"function"}]'

        self.pancakeSwapRouter = self.web3.eth.contract(address=self.panRouterContractAddress, abi=self.panabi)

        self.tokenAmount = 10 ** 18
        self.tokenDecimalsDesc = "tokenDecimals"

        self.bnbAmountToBuy = 0.001
        printInfo(f"BNB amount to buy for each crypto = {self.bnbAmountToBuy} BNB", bcolors.WARN)
        self.wbnbContract = self.web3.toChecksumAddress("0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c")
        self.usdtContract = self.web3.toChecksumAddress("0x55d398326f99059ff775485246999027b3197955")

        self.contract = self.web3.eth.contract(address=self.getPriceAddress, abi=self.getPriceABI)

        self.senderAddress = "0xa9eC6E2129267f01a2E772E208F8b0Ed802748D0"
        self.privateKey = getPrivateKey()


    def getPancakeSwapPrice(self, token):

        token = self.web3.toChecksumAddress(token)

        if token == self.wbnbContract or token == self.usdtContract:
            return 0
        
        # tokensToSell = 10 ** tokenDecimals # self.setDecimals(1, tokenDecimals)

        try:
            tokenAmountOut = self.pancakeSwapRouter.functions.getAmountsOut(self.tokenAmount, [token, self.wbnbContract]).call()
            tokenPriceInBNB =  self.web3.fromWei(tokenAmountOut[1], "ether") # / (self.tokenAmount / tokenAmountOut[0])

            # Slow
            #BNBamountOut = self.pancakeSwapRouter.functions.getAmountsOut(self.tokenAmount, [self.wbnbContract, self.usdtContract]).call()
            bnbPriceInUSDT = 1 # self.web3.fromWei(BNBamountOut[1], "ether")

        except:
            return 0
            #printInfo(f"Error calculando el precio en getPancakeSwapPrice()")

        return float(bnbPriceInUSDT * tokenPriceInBNB)


    def getTokenDecimals(self, token):

        try:
            tokenRouter = self.web3.eth.contract(address=token, abi=self.tokenAbi)
            tokenDecimals = tokenRouter.functions.decimals().call()
        except:
            tokenDecimals = 100

        return tokenDecimals


    def setDecimals(self, number, decimals):
        number = str(number)
        numberAbs = number.split('.')[0]

        if '.' in str(number):
            numberDecimals = number.split('.')[1]
        else:
            numberDecimals = ""

        # numberDecimals = number.split('.')[1] ? number.split('.')[1] : '';

        while len(numberDecimals) < decimals:
            numberDecimals += "0"

        return int(numberAbs + numberDecimals)


    def getNewBscContracts(self):

        # Get API data
        dataDf = self.getData()

        # Get .csv symbols with pairAddresses
        if os.path.exists(self.bscContractsCsv):
            self.getCsvBscTokens(dataDf=dataDf)
            bscContractsHeader = False
        else:
            bscContractsHeader = True

        # For each dataframe row
        for i, row in dataDf.iterrows():
            if row[self.idDesc] not in self.csvBscContractTokens:
                self.insertBscContracts(row=row, headers=bscContractsHeader)


    def core(self, currentLoop):

        printInfo(f"Start Loop {currentLoop}", bcolors.OK)
        startDate = dt.datetime.now()

        # Get .csv symbols not sold
        if os.path.exists(self.tradingHistoryCsv):
            self.dfCsvSymbolsNotSold = self.getCsvSymbolsNotSold()
            self.writeTradingHistoryHeaders = False
        else:
            self.dfCsvSymbolsNotSold = pd.DataFrame()
            self.writeTradingHistoryHeaders = True

        # For each dataframe row
        for i, row in self.bscContractsDf.iterrows():

            # If "current" values are not set
            if self.data.get(row[self.idDesc], {self.priceDesc: -1})[self.priceDesc] == -1:

                self.data.setdefault(row[self.idDesc], {})[self.symbolNameDesc] = row[self.symbolNameDesc]
                self.data[row[self.idDesc]][self.symbolDesc] = row[self.symbolDesc]
                self.data[row[self.idDesc]][self.slugDesc] = row[self.slugDesc]
                self.data[row[self.idDesc]][self.bscContractDesc] = row[self.bscContractDesc]

                self.data[row[self.idDesc]][self.priceDesc] = self.getPancakeSwapPrice(token=row[self.bscContractDesc])

                #printInfo(f"{self.data[row[self.idDesc]][self.symbolNameDesc]} = {self.data[row[self.idDesc]][self.priceDesc]} BNB", bcolors.OK)
                #continue


            # If "previous" values are set
            else:

                prevPrice = self.data[row[self.idDesc]][self.priceDesc]

                if row[self.idDesc] in self.csvSymbolsNotSold:
                        prevPrice = float(self.dfCsvSymbolsNotSold[self.dfCsvSymbolsNotSold[self.idDesc] == row[self.idDesc]][self.priceDesc])
                        #printInfo(f"El symbol {self.data[row[self.idDesc]][self.symbolNameDesc]} ya tiene prevPrice que es {prevPrice} BNB", bcolors.OK)

                self.data[row[self.idDesc]][self.prevPriceDesc] = prevPrice
                self.data[row[self.idDesc]][self.priceDesc] = self.getPancakeSwapPrice(token=row[self.bscContractDesc])

                if self.data[row[self.idDesc]][self.priceDesc] == 0 or self.data[row[self.idDesc]][self.prevPriceDesc] == 0:
                    continue

                # Calculate diff percentage
                percengeDiffWoFormat = self.data[row[self.idDesc]][self.priceDesc] / self.data[row[self.idDesc]][self.prevPriceDesc]
                percentageDiff = formatPercentages(percengeDiffWoFormat)

                # Double check to prevent insert info twice
                if percentageDiff <= self.buyTrigger or percentageDiff >= self.sellTrigger:
                    self.dfCsvSymbolsNotSold = self.getCsvSymbolsNotSold()
                    printInfo(f"Current loop = {currentLoop} || Comprobamos doblemente para saber si realmente hemos de hacer trading de {self.data[row[self.idDesc]][self.symbolDesc]} - {percentageDiff}", bcolors.BLUE)
                else:
                    continue

                # If we should buy or sell a crypto
                if percentageDiff <= self.buyTrigger and row[self.idDesc] not in self.csvSymbolsNotSold: # buy
                    
                    color = bcolors.ERR
                    HTMLcolor = "red"
                    tradeAction = "Comprar"
                    urlAction = "outputCurrency"
                    isToBuy = True

                    # -------------------------------------------------------------------

                    # Prepare data to insert in .csv file
                    tempRow = {}

                    for x, y in row.items():
                        tempRow[x] = y

                    tempRow[self.isSoldDesc] = 0
                    tempRow[self.isTradingDesc] = boolToInt(val=self.isTrading)
                    tempRow[self.prevPriceDesc] = self.data[row[self.idDesc]][self.prevPriceDesc]
                    tempRow[self.priceDesc] = self.data[row[self.idDesc]][self.priceDesc]
                    tempRow[self.sellPriceDesc] = None
                    tempRow[self.percentageDiffDesc] = percentageDiff
                    tempRow[self.sellPercentageDiffDesc] = None
                    tempRow[self.datetimeDesc] = dt.datetime.now()
                    tempRow[self.sellDatetimeDesc] = None

                    # To dataFrame
                    tempDf = pd.DataFrame([tempRow])

                    tempDf.to_csv(self.tradingHistoryCsv, index=False, columns=list(tempDf), mode="a", header=self.writeTradingHistoryHeaders)
                    self.writeTradingHistoryHeaders = False

                elif percentageDiff >= self.sellTrigger and row[self.idDesc] in self.csvSymbolsNotSold: # sell

                    color = bcolors.OK
                    HTMLcolor = "green"
                    tradeAction = "Vender"
                    urlAction = "inputCurrency"
                    isToBuy = False

                    # ------------------------------------------------------------------

                    # Update .csv setting the new cells value
                    tempfile = NamedTemporaryFile(mode='w', delete=False)

                    df = pd.read_csv(self.tradingHistoryCsv, sep=self.separator)

                    with open(self.tradingHistoryCsv, 'r', newline='') as csvfile, tempfile:

                        reader = csv.DictReader(csvfile, fieldnames=list(df), delimiter=self.separator)
                        writer = csv.DictWriter(tempfile, fieldnames=list(df), delimiter=self.separator, lineterminator='\n')

                        for r in reader:

                            if r[self.symbolDesc] == self.symbolDesc:
                                writer.writerow(r)
                                continue

                            if int(r[self.idDesc]) == int(row[self.idDesc]) and int(r[self.isTradingDesc]) == boolToInt(val=self.isTrading) and int(r[self.isSoldDesc]) == 0:
                                r[self.isSoldDesc] = 1
                                r[self.sellPriceDesc] = self.data[row[self.idDesc]][self.priceDesc]
                                r[self.sellPercentageDiffDesc] = percentageDiff
                                r[self.sellDatetimeDesc] = dt.datetime.now()

                            writer.writerow(r)

                    shutil.move(tempfile.name, self.tradingHistoryCsv)

                else: # Nothing to do, so let's continue with the other coin
                    continue

                #tokens = self.getTokens(cryptoSlug=self.data[row[self.idDesc]][self.slugDesc])

                printInfo(f"CurrentLoop = {currentLoop} || {percentageDiff} % --- {tradeAction} {self.data[row[self.idDesc]][self.symbolNameDesc]} ({self.data[row[self.idDesc]][self.symbolDesc]}"
                + f" - {row[self.idDesc]}) // Ahora = {self.data[row[self.idDesc]][self.priceDesc]} BNB, Antes = {self.data[row[self.idDesc]][self.prevPriceDesc]} BNB", color)
                
                printInfo(f"{self.pancakeSwapBaseUrl}inputCurrency={self.data[row[self.idDesc]][self.bscContractDesc]}", color)

                #if len(tokens) > 0:

                if self.isTrading: # and self.binanceSmartChainDesc in tokens.keys():

                    if self.sendNotifications:
                        self.sendEmails(
                            tradeAction=tradeAction, urlAction=urlAction, cryptoData=self.data[row[self.idDesc]],
                            percentageDiff=percentageDiff, color=HTMLcolor, token=self.data[row[self.idDesc]][self.bscContractDesc]
                        )

                    if isToBuy:
                        self.buyToken(token=self.data[row[self.idDesc]][self.bscContractDesc])
                        time.sleep(30)
                        self.buyToken(token=self.data[row[self.idDesc]][self.bscContractDesc])
                        time.sleep(30)
                        self.buyToken(token=self.data[row[self.idDesc]][self.bscContractDesc])
                        time.sleep(30)
                        self.buyToken(token=self.data[row[self.idDesc]][self.bscContractDesc])
                        time.sleep(30)
                        self.buyToken(token=self.data[row[self.idDesc]][self.bscContractDesc])
                        time.sleep(30)
                        self.buyToken(token=self.data[row[self.idDesc]][self.bscContractDesc])
                        time.sleep(30)
                        self.buyToken(token=self.data[row[self.idDesc]][self.bscContractDesc])
                        time.sleep(30)
                        self.buyToken(token=self.data[row[self.idDesc]][self.bscContractDesc])
                        time.sleep(30)
                        self.buyToken(token=self.data[row[self.idDesc]][self.bscContractDesc])
                        time.sleep(30)
                        self.buyToken(token=self.data[row[self.idDesc]][self.bscContractDesc])
                        time.sleep(30)
                        self.buyToken(token=self.data[row[self.idDesc]][self.bscContractDesc])
                        
                        exit()
                    else:
                        self.sellToken(token=self.data[row[self.idDesc]][self.bscContractDesc])

        endDate = dt.datetime.now()
        printInfo(f"End loop {currentLoop} // Start = {startDate}, End = {endDate} ||| {endDate - startDate}", bcolors.WARN)

        #time.sleep(self.delay)


    def getCsvSymbolsNotSold(self):

        df = pd.read_csv(self.tradingHistoryCsv, sep=self.separator)

        df[self.idDesc] = df[self.idDesc].astype(int)

        df = df[(df[self.isTradingDesc] == boolToInt(val=self.isTrading)) & (df[self.isSoldDesc] == 0)]

        self.csvSymbolsNotSold = df[self.idDesc].tolist()

        #print(self.csvSymbolsNotSold)

        return df


    def getCsvBscTokens(self, dataDf: pd.DataFrame()):

        df = pd.read_csv(self.bscContractsCsv, sep=self.separator)

        df[self.idDesc] = df[self.idDesc].astype(int)

        self.csvBscContractTokens = df[self.idDesc].tolist()
        df = df[df[self.bscContractDesc].notnull()]

        print(df)

        dataDf = dataDf[(dataDf[self.isActiveDesc] == 1) & (dataDf[self.fullyDilluttedMarketCapDesc] <= 1000000)]

        print(dataDf)

        self.bscContractsDf = df.loc[df[self.idDesc].isin(dataDf[self.idDesc]),:]

        print(self.bscContractsDf)


    # Insert token data if not in .csv file already
    def insertBscContracts(self, row, headers):

        t = self.getTokens(cryptoSlug=row[self.slugDesc])

        if self.binanceSmartChainDesc in t.keys():
            bscContract = t[self.binanceSmartChainDesc]
        else:
            bscContract = None

        tokenData = {
            self.idDesc: int(row[self.idDesc]),
            self.symbolDesc: row[self.symbolDesc],
            self.symbolNameDesc: row[self.symbolNameDesc],
            self.slugDesc: row[self.slugDesc],
            self.bscContractDesc: bscContract,
        }

        output = pd.DataFrame()
        output = output.append(tokenData, ignore_index=True)

        output.to_csv(self.bscContractsCsv, index=False, columns=tokenData.keys(), mode="a", header=headers)

        printInfo(f"Contract insertado para {row[self.symbolNameDesc]} ({bscContract})", bcolors.OK)

        time.sleep(2)


    def getData(self):

        df = pd.DataFrame()

        while len(df) == 0:

            try:

                with urllib.request.urlopen(self.allCoinMarketCapCoinsUrl) as url:
                    rawData = json.loads(url.read().decode())

                for i, data in rawData.items():
                    for desc, listOfDicts in data.items():

                        if desc == self.cryptoCurrencyListDesc:
                            
                            df = pd.DataFrame(listOfDicts)
                            
                            # Select few columns only
                            df = df[self.selectDataColumns]
                            
                            # df = df.drop(['tags', 'cmcRank', 'marketPairCount', 'lastUpdated', 'isAudited', 'platform', 'auditInfoList'], axis = 1)

                            df = df.rename(columns = {self.nameDesc: self.symbolNameDesc})

                            # Prepare column to expand
                            df[self.columnToExpand] = df[self.columnToExpand].apply(lambda cell: cell[0])

                            # Expand column in df
                            df = df.drop(self.columnToExpand, axis=1).join(pd.DataFrame(df[self.columnToExpand].values.tolist()))

                            #print(len(df[df[self.priceDesc] <= 1]))

            except:
                printInfo("Error obteniendo datos en getData()", bcolors.ERRMSG)
                
            if len(df) == 0:
                printInfo("No se han obtenido datos en getData()", bcolors.ERRMSG)
                time.sleep(self.delay)
            else:
                break

        return df


    def sendEmails(self, tradeAction, urlAction, cryptoData, percentageDiff, color, token):

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
        <h3>Precio:</h3>
        <h3>Ahora = {cryptoData[self.priceDesc]} BNB</h3>
        <h3>Antes = {cryptoData[self.prevPriceDesc]} BNB</h3>
        """

        emailContent = content + f"""<h3><a href="{coinMarketCapUrl}">{coinMarketCapDesc}</a></h3>
        """
        whatsappContent = subject + content + f"""
        {coinMarketCapDesc}
        {coinMarketCapUrl}
        """

        """
        for platform, token in tokens.items():

            if platform == self.binanceSmartChainDesc:
                baseUrl = self.pancakeSwapBaseUrl
            elif platform == self.ethereumDesc:
                baseUrl = self.uniswapBaseUrl
            else:
                continue
        """

        # Set URL to buy or sell coins
        tradeUrl = self.pancakeSwapBaseUrl + urlAction + "=" + token

        desc = f"{tradeAction} en Bscscan con token {token}"

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

        cryptoUrl = self.cryptoBaseUrl + cryptoSlug

        while True:

            try:
                html_page = urllib.request.urlopen(cryptoUrl)
                soup = BeautifulSoup(html_page, "html.parser")

                allHrefs = []

                for link in soup.findAll('a'):
                    href = str(link.get('href'))

                    if self.tokenUrl in href:
                        allHrefs.append(href)

                allHrefs = list(dict.fromkeys(allHrefs))

                for href in allHrefs:

                    if self.bscscanDesc in href:
                        platform = self.binanceSmartChainDesc
                    elif self.etherscanDesc in href:
                        platform = self.ethereumDesc
                    else:
                        continue

                    contractToken = href.rsplit('/', 1)[-1][:42]

                    tokens[platform] = contractToken

                # Sort dict
                if len(tokens) > 0:
                    tokens = {key: val for key, val in sorted(tokens.items(), key = lambda ele: ele[0])}

                break

            except:
                printInfo("Error obteniendo datos en getTokens()", bcolors.ERRMSG)
                time.sleep(self.delay)

        return tokens
    

    def sendWhatsapp(self, message):

        try:

            client = Client(self.account_sid, self.auth_token)

            for number in self.mobileNumbers:
            
                message = client.messages.create( 
                                            from_='whatsapp:+14155238886',  
                                            body=message,      
                                            to='whatsapp:' + number 
                                        ) 
            
                #printInfo(f"WhatsApp message: {message.sid}", bcolors.OK)

        except:
            printInfo(f"No se ha/n podido enviar mensaje/s de WhatsApp", bcolors.ERRMSG)


    def buyToken(self, token):

        while True:

            try:
                
                balance = self.web3.eth.get_balance(self.senderAddress)
                humanReadable = self.web3.fromWei(balance,'ether')

                printInfo(f"Total BNB amount: {humanReadable}", bcolors.WARN)
                
                #Contract Address of Token we want to buy
                tokenToBuy = self.web3.toChecksumAddress(token)        # web3.toChecksumAddress("0x6615a63c260be84974166a5eddff223ce292cf3d")
                spend = self.web3.toChecksumAddress(self.wbnbContract) # wbnb contract
                
                #Setup the PancakeSwap contract
                contract = self.web3.eth.contract(address=self.panRouterContractAddress, abi=self.panabi)

                nonce = self.web3.eth.get_transaction_count(self.senderAddress)

                pancakeswap2_txn = contract.functions.swapExactETHForTokensSupportingFeeOnTransferTokens( # swapExactETHForTokens
                0, # set to 0, or specify minimum amount of tokeny you want to receive - consider decimals!!!
                [spend,tokenToBuy],
                self.senderAddress,
                (int(time.time()) + 10000)
                ).buildTransaction({
                'from': self.senderAddress,
                'value': self.web3.toWei(self.bnbAmountToBuy,'ether'), # This is the Token(BNB) amount you want to Swap from
                'gas': 250000,
                'gasPrice': self.web3.toWei('5','gwei'),
                'nonce': nonce,
                })
                    
                signed_txn = self.web3.eth.account.sign_transaction(pancakeswap2_txn, private_key=self.privateKey)
                tx_token = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)


                printInfo(f"Compra realizada! Transacción --> {self.bscscanTransactionBaseUrl}{self.web3.toHex(tx_token)}", bcolors.OKMSG)

                break

            except:
                printInfo("Error en buyToken()", bcolors.ERRMSG)
                time.sleep(self.delay)


    def sellToken(self, token):

        while True:

            try:

                sender_address = self.senderAddress #TokenAddress of holder
                spend = self.web3.toChecksumAddress(self.wbnbContract)  #WBNB Address

                #Get BNB Balance
                balance = self.web3.eth.get_balance(sender_address)
                humanReadable = self.web3.fromWei(balance,'ether')

                printInfo(f"Total BNB amount: {humanReadable}", bcolors.WARN)
                
                #Contract id is the new token we are swaping to
                #contract_id = web3.toChecksumAddress("0xc9849e6fdb743d08faee3e34dd2d1bc69ea11a51")
                contract_id = self.web3.toChecksumAddress(token)
                
                #Setup the PancakeSwap contract
                contract = self.web3.eth.contract(address=self.panRouterContractAddress, abi=self.panabi)

                #Create token Instance for Token
                sellTokenContract = self.web3.eth.contract(contract_id, abi=self.sellAbi)

                #Get Token Balance
                balance = sellTokenContract.functions.balanceOf(sender_address).call()
                symbol = sellTokenContract.functions.symbol().call()
                readable = self.web3.fromWei(balance,'ether')

                if int(readable) == 0:
                    printInfo(f"El balance de {symbol} es 0 y no hay nada que vender", bcolors.WARN)
                    break

                printInfo(f"Balance: {readable} {symbol}", bcolors.WARN)

                #Enter amount of token to sell
                tokenValue = self.web3.toWei(readable, 'ether')

                #Approve Token before Selling
                tokenValue2 = self.web3.fromWei(tokenValue, 'ether')
                start = time.time()
                approve = sellTokenContract.functions.approve(self.panRouterContractAddress, balance).buildTransaction({
                            'from': sender_address,
                            'gasPrice': self.web3.toWei('5','gwei'),
                            'nonce': self.web3.eth.get_transaction_count(sender_address),
                            })

                signed_txn = self.web3.eth.account.sign_transaction(approve, private_key=self.privateKey)
                tx_token = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
                printInfo(f"Venta aprobada --> {self.bscscanTransactionBaseUrl}{self.web3.toHex(tx_token)}", bcolors.OK)

                # Wait after approve 10 seconds before sending transaction
                time.sleep(10)

                printInfo(f"Canjeando {tokenValue2} {symbol} por BNB", bcolors.WARN)
                # Swaping exact Token for ETH 

                pancakeswap2_txn = contract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens( # swapExactTokensForETH
                            tokenValue ,0, 
                            [contract_id, spend],
                            sender_address,
                            (int(time.time()) + 1000000)

                            ).buildTransaction({
                            'from': sender_address,
                            'gasPrice': self.web3.toWei('5','gwei'),
                            'nonce': self.web3.eth.get_transaction_count(sender_address),
                            })
                    
                signed_txn = self.web3.eth.account.sign_transaction(pancakeswap2_txn, private_key=self.privateKey)
                tx_token = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)

                printInfo(f"Venta realizada para {symbol}! Transacción --> {self.bscscanTransactionBaseUrl}{self.web3.toHex(tx_token)}", bcolors.OKMSG)

                break

            except:
                printInfo("Error en sellToken()", bcolors.ERRMSG)
                time.sleep(self.delay)


    def main(self):

        # Update possible contracts
        self.getNewBscContracts()

        loopsCounter = 0
        eachLoopsInfo = 10

        with ThreadPoolExecutor(max_workers=5) as executor:

            while True:

                if loopsCounter % eachLoopsInfo == 0:
                    printInfo(f"--- For Loop: {loopsCounter}", bcolors.WARN)

                future = executor.submit(self.core, loopsCounter)
                loopsCounter += 1
                time.sleep(self.delay)
