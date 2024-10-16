import commonFunctions
import sqliteClass

import telegramClass
import tokenFOMOclass

from numpy import add
import requests
import pandas as pd
import datetime as dt
import os
import time
import urllib.request, json
import bcolors
from bs4 import BeautifulSoup
#from uniswap import Uniswap
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
import json

# ------------------------------------------------------------------------------------

# Get MM private key (file not included for safety purposes)
def getPrivateKey():
    try:
        with open("/home/ubuntu/Documents/Projects/config.txt") as mytxt:
            for line in mytxt:
                return line
    except Exception as e:
        commonFunctions.printInfo(f"Error en getPrivateKey() {e}", bcolors.ERRMSG)
        exit()


class cmc:

    def __init__(self, buyTrigger, sellTrigger, isTrading: bool, bnbAmountToBuy: float, sendNotifications: bool, tradingType: int, maxThreads: int, delay):

        # Check parameters
        if not isinstance(buyTrigger, (int, float)):
            commonFunctions.printInfo(f"El parametro buyTrigger ha de ser de tipo int o float", bcolors.ERRMSG)
            exit()

        elif not isinstance(sellTrigger, (int, float)):
            commonFunctions.printInfo(f"El parametro sellTrigger ha de ser de tipo int o float", bcolors.ERRMSG)
            exit()

        elif not isinstance(isTrading, bool):
            commonFunctions.printInfo(f"El parametro isTrading ha de ser de tipo bool", bcolors.ERRMSG)
            exit()

        elif not isinstance(bnbAmountToBuy, (int, float)):
            commonFunctions.printInfo(f"El parametro bnbAmountToBuy ha de ser de tipo int o float", bcolors.ERRMSG)
            exit()

        elif not isinstance(sendNotifications, bool):
            commonFunctions.printInfo(f"El parametro sendNotification ha de ser de tipo bool", bcolors.ERRMSG)
            exit()

        elif not isinstance(tradingType, int):
            commonFunctions.printInfo(f"El parametro tradingType ha de ser de tipo int", bcolors.ERRMSG)
            exit()

        elif not isinstance(maxThreads, int):
            commonFunctions.printInfo(f"El parametro maxThreads ha de ser de tipo int", bcolors.ERRMSG)
            exit()
        
        elif not isinstance(delay, (int, float)):
            commonFunctions.printInfo(f"El parametro delay ha de ser de tipo int o float", bcolors.ERRMSG)
            exit()

        # Loading...
        commonFunctions.printInfo(f"Cargando configuraciones...", bcolors.HEADER)

        # Assign parameters to self values
        self.buyTrigger = buyTrigger
        self.sellTrigger = sellTrigger
        self.isTrading = isTrading
        self.bnbAmountToBuy = bnbAmountToBuy
        self.sendNotifications = sendNotifications

        self.tradingType = tradingType

        # Type of trading
        # 0 = CoinMarketCap cryptos
        # 1 = TelegramGroup cryptos
        # ELSE = TokenFOMO cryptos (has to be the best one) 
        
        if self.tradingType == 0:
            tradingHistoryCsv="coinmarketcapTradingHistory.csv"
            bscContractsCsv="coinmarketcapBscContracts.csv"
            self.extraClass = None
        elif self.tradingType == 1:
            tradingHistoryCsv="telegramTradingHistory.csv"
            bscContractsCsv="telegramBscContracts.csv"
            self.extraClass = telegramClass.telegram(contractCsv=bscContractsCsv, tradingType=self.tradingType)
        else:
            tradingHistoryCsv="tokenFOMOtradingHistory.csv"
            bscContractsCsv="tokenFOMObscContracts.csv"
            self.extraClass = tokenFOMOclass.tokenFOMO(contractCsv=bscContractsCsv, tradingType=self.tradingType, firstN=10)

        self.tradingHistoryCsv = tradingHistoryCsv
        self.bscContractsCsv = bscContractsCsv

        self.maxThreads = maxThreads
        self.delay = delay

        # Get .csv symbols with contracts
        if os.path.exists(self.bscContractsCsv):
            self.writeBscContractsHeader = False
        else:
            self.writeBscContractsHeader = True

        self.bscContractsDf = pd.DataFrame()
        self.dfCsvSymbolsNotSold = pd.DataFrame()

        self.contractTokensCsv = []
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

        self.FK_cryptoIdDesc = "FK_cryptoId"

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
        self.buyDatetimeDesc = "buyDatetime"
        self.sellDatetimeDesc = "sellDatetime"

        self.buyURLDesc = "buyURL"
        self.approveSellURLDesc = "approveSellURL"
        self.sellURLDesc = "sellURL"

        self.realBuyPriceDesc = "realBuyPrice"
        self.realSellPriceDesc = "realSellPrice"

        self.percentageDiffDesc = "percentageDiff"
        self.sellPercentageDiffDesc = "sellPercentageDiff"
        self.isSoldDesc = "isSold"
        self.isTradingDesc = "isTrading"

        self.separator = ","

        self.bscscanDesc = "bscscan"
        self.etherscanDesc = "etherscan"
        
        self.ethereumDesc = "Ethereum"
        self.binanceSmartChainDesc = "BinanceSmartChain"

        self.contractDesc = "contract"

        self.resultDesc = "result"

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
        self.pancakeSwapRouterContractAddress = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
        self.pancakeSwapRouterContractAddressAbi = self.getAddressAbi(address=self.pancakeSwapRouterContractAddress)

        self.getPriceAddress = "0xBCfCcbde45cE874adCB698cC183deBcF17952812"
        self.getPriceAbi = self.getAddressAbi(address=self.getPriceAddress)

        #pancakeswap router abi 
        #self.pancakeSwapRouterContractAddressAbi = '[{"inputs":[{"internalType":"address","name":"_factory","type":"address"},{"internalType":"address","name":"_WETH","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"amountADesired","type":"uint256"},{"internalType":"uint256","name":"amountBDesired","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountTokenDesired","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountIn","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountOut","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsIn","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"reserveA","type":"uint256"},{"internalType":"uint256","name":"reserveB","type":"uint256"}],"name":"quote","outputs":[{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETHSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermit","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermitSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityWithPermit","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapETHForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETHSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]'

        # Abi for Token to sell - all we need from here is the balanceOf & approve function can replace with shortABI
        self.sellAbi = '[{"inputs":[{"internalType":"string","name":"_NAME","type":"string"},{"internalType":"string","name":"_SYMBOL","type":"string"},{"internalType":"uint256","name":"_DECIMALS","type":"uint256"},{"internalType":"uint256","name":"_supply","type":"uint256"},{"internalType":"uint256","name":"_txFee","type":"uint256"},{"internalType":"uint256","name":"_lpFee","type":"uint256"},{"internalType":"uint256","name":"_MAXAMOUNT","type":"uint256"},{"internalType":"uint256","name":"SELLMAXAMOUNT","type":"uint256"},{"internalType":"address","name":"routerAddress","type":"address"},{"internalType":"address","name":"tokenOwner","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"minTokensBeforeSwap","type":"uint256"}],"name":"MinTokensBeforeSwapUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"tokensSwapped","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"ethReceived","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"tokensIntoLiqudity","type":"uint256"}],"name":"SwapAndLiquify","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"bool","name":"enabled","type":"bool"}],"name":"SwapAndLiquifyEnabledUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[],"name":"_liquidityFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_maxTxAmount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_taxFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"claimTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"tAmount","type":"uint256"}],"name":"deliver","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"excludeFromFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"excludeFromReward","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"geUnlockTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"includeInFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"includeInReward","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"isExcludedFromFee","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"isExcludedFromReward","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"time","type":"uint256"}],"name":"lock","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"numTokensSellToAddToLiquidity","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tAmount","type":"uint256"},{"internalType":"bool","name":"deductTransferFee","type":"bool"}],"name":"reflectionFromToken","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"liquidityFee","type":"uint256"}],"name":"setLiquidityFeePercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"maxTxPercent","type":"uint256"}],"name":"setMaxTxPercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"swapNumber","type":"uint256"}],"name":"setNumTokensSellToAddToLiquidity","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bool","name":"_enabled","type":"bool"}],"name":"setSwapAndLiquifyEnabled","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"taxFee","type":"uint256"}],"name":"setTaxFeePercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"swapAndLiquifyEnabled","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"rAmount","type":"uint256"}],"name":"tokenFromReflection","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalFees","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"uniswapV2Pair","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"uniswapV2Router","outputs":[{"internalType":"contract IUniswapV2Router02","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"unlock","outputs":[],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]'

        #self.getPriceABI = '[{"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"token0","type":"address"},{"indexed":true,"internalType":"address","name":"token1","type":"address"},{"indexed":false,"internalType":"address","name":"pair","type":"address"},{"indexed":false,"internalType":"uint256","name":"","type":"uint256"}],"name":"PairCreated","type":"event"},{"constant":true,"inputs":[],"name":"INIT_CODE_PAIR_HASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"allPairs","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"allPairsLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"}],"name":"createPair","outputs":[{"internalType":"address","name":"pair","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"feeTo","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"feeToSetter","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"getPair","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_feeTo","type":"address"}],"name":"setFeeTo","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"name":"setFeeToSetter","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]'

        #self.pancakeSwapAbi =  [{"inputs":[{"internalType":"address","name":"_factory","type":"address"},{"internalType":"address","name":"_WETH","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"amountADesired","type":"uint256"},{"internalType":"uint256","name":"amountBDesired","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountTokenDesired","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountIn","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountOut","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsIn","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"reserveA","type":"uint256"},{"internalType":"uint256","name":"reserveB","type":"uint256"}],"name":"quote","outputs":[{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETHSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermit","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermitSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityWithPermit","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapETHForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETHSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}];
        self.tokenAbi = '[{"inputs":[{"internalType":"string","name":"_name","type":"string"},{"internalType":"string","name":"_symbol","type":"string"},{"internalType":"uint256","name":"_decimals","type":"uint256"},{"internalType":"uint256","name":"_supply","type":"uint256"},{"internalType":"uint256","name":"_txFee","type":"uint256"},{"internalType":"uint256","name":"_burnFee","type":"uint256"},{"internalType":"uint256","name":"_charityFee","type":"uint256"},{"internalType":"address","name":"_FeeAddress","type":"address"},{"internalType":"address","name":"tokenOwner","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[],"name":"FeeAddress","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_BURN_FEE","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_CHARITY_FEE","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_TAX_FEE","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_value","type":"uint256"}],"name":"burn","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"tAmount","type":"uint256"}],"name":"deliver","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"excludeAccount","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"includeAccount","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"isCharity","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"isExcluded","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mint","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tAmount","type":"uint256"},{"internalType":"bool","name":"deductTransferFee","type":"bool"}],"name":"reflectionFromToken","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"setAsCharityAccount","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"rAmount","type":"uint256"}],"name":"tokenFromReflection","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalBurn","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalCharity","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalFees","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_txFee","type":"uint256"},{"internalType":"uint256","name":"_burnFee","type":"uint256"},{"internalType":"uint256","name":"_charityFee","type":"uint256"}],"name":"updateFee","outputs":[],"stateMutability":"nonpayable","type":"function"}]'

        self.pancakeSwapRouter = self.web3.eth.contract(address=self.pancakeSwapRouterContractAddress, abi=self.pancakeSwapRouterContractAddressAbi)

        self.tokenAmount = 10 ** 18
        self.tokenDecimalsDesc = "tokenDecimals"

        # Trading variables!!
        self.gas = 350000 # default is 250000
        self.gasPrice = self.web3.toWei('5','gwei') # default is 5

        self.wbnbContract = self.web3.toChecksumAddress("0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c")
        self.usdtContract = self.web3.toChecksumAddress("0x55d398326f99059ff775485246999027b3197955")

        self.contract = self.web3.eth.contract(address=self.getPriceAddress, abi=self.getPriceAbi)

        self.senderAddress = "0xa9eC6E2129267f01a2E772E208F8b0Ed802748D0"
        self.privateKey = getPrivateKey()

        commonFunctions.printInfo(f"{self.isTradingDesc} = {self.isTrading}", bcolors.WARN)

        self.isTradingInt = commonFunctions.boolToInt(val=self.isTrading)

        # Print trading variables!!!!
        if self.isTrading:
            balance = self.web3.eth.get_balance(self.senderAddress)
            humanReadable = self.web3.fromWei(balance,'ether')
            commonFunctions.printInfo(f"Total BNB amount: {humanReadable}", bcolors.WARN)
            commonFunctions.printInfo(f"BNB amount to buy for each crypto = {self.bnbAmountToBuy} BNB", bcolors.WARN)
            commonFunctions.printInfo(f"Gas = {self.gas}", bcolors.WARN)
            commonFunctions.printInfo(f"GasPrice = {self.gasPrice}", bcolors.WARN)

        # -----------------------------------------------------------------------------------

        # Telegram test
        # self.telegramGroupNameDesc = "telegramGroupName"
        # self.newTelegramGroupNameDesc = "newTelegramGroupName"
        # self.contractDesc = "contracts"


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

        except Exception as e:
            return 0
            #commonFunctions.printInfo(f"Error calculando el precio en getPancakeSwapPrice() {e.args}", bcolors.ERRMSG)

        return float(bnbPriceInUSDT * tokenPriceInBNB)


    def getTokenDecimals(self, token):

        try:
            tokenRouter = self.web3.eth.contract(address=token, abi=self.tokenAbi)
            tokenDecimals = tokenRouter.functions.decimals().call()
        except Exception as e:
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


    def getAddressAbi(self, address):

        abi = ""

        abiUrl = "https://api.bscscan.com/api?module=contract&action=getabi&address=" + address

        while len(abi) == 0:

            try:
                with urllib.request.urlopen(abiUrl) as url:
                    rawData = json.loads(url.read().decode())

                # If abi is available
                if int(rawData[self.statusDesc]) == 1:
                    abi = rawData[self.resultDesc]
                else:
                    time.sleep(5)

            except Exception as e:
                commonFunctions.printInfo(f"Error obteniendo datos en getAddressAbi() {e.args}", bcolors.ERRMSG)
                time.sleep(self.delay)

        return abi


    def getNewBscContracts(self):

        # Get API data
        if self.tradingType == 0:
            dataDf = self.getData()
        else:
            dataDf = sqliteClass.db().executeQuery(f"""
                SELECT
                    id, symbol, symbolName, slug, contract
                FROM dimCryptos
                WHERE FK_typeId = {self.tradingType}
                """
            )

        while True:

            isDone = True

            # Get .csv symbols with contracts
            self.getBscContracts(dataDf=dataDf)

            # Not CoinMarketCap, skip this section
            if self.tradingType != 0:
                break

            # For each dataframe row
            for i, row in dataDf.iterrows():
                if row[self.contractDesc] not in self.contractTokensCsv:
                    # Insert new cryptos in the file
                    self.insertBscContracts(row=row)
                    isDone = False

            if isDone:
                break

        commonFunctions.printInfo(f"Existen {len(self.contractTokensCsv)} cryptos en el fichero '{self.bscContractsCsv}'", bcolors.OK)


    def core(self, currentLoop):

        #commonFunctions.printInfo(f"Start Loop {currentLoop}", bcolors.OK)
        startDate = dt.datetime.now()

        # Get .csv symbols not sold
        self.getCsvSymbolsNotSold()

        # For each dataframe row
        for i, row in self.bscContractsDf.iterrows():

            # If "current" values are not set
            if self.data.get(row[self.contractDesc], {self.priceDesc: -1})[self.priceDesc] == -1:

                self.data.setdefault(row[self.contractDesc], {})[self.symbolNameDesc] = row[self.symbolNameDesc]
                self.data[row[self.contractDesc]][self.symbolDesc] = row[self.symbolDesc]
                self.data[row[self.contractDesc]][self.slugDesc] = row[self.slugDesc]

                self.data[row[self.contractDesc]][self.priceDesc] = self.getPancakeSwapPrice(token=row[self.contractDesc])

                commonFunctions.printInfo(f"{self.data[row[self.contractDesc]][self.symbolNameDesc]} = {self.data[row[self.contractDesc]][self.priceDesc]} BNB", bcolors.OK)
                #continue


            # If "previous" values are set
            else:
                hasBoughtPrice = False
                prevPancakeSwapPrice = prevPrice = self.data[row[self.contractDesc]][self.priceDesc]

                if row[self.contractDesc] in self.csvSymbolsNotSold:
                        prevPrice = float(self.dfCsvSymbolsNotSold[self.dfCsvSymbolsNotSold[self.contractDesc] == row[self.contractDesc]][self.priceDesc])
                        hasBoughtPrice = True
                        #commonFunctions.printInfo(f"El symbol {self.data[row[self.contractDesc]][self.symbolNameDesc]} ya tiene prevPrice que es {prevPrice} BNB", bcolors.OK)

                self.data[row[self.contractDesc]][self.prevPriceDesc] = prevPrice
                self.data[row[self.contractDesc]][self.priceDesc] = self.getPancakeSwapPrice(token=row[self.contractDesc])

                # If the current price is == 0, skip this crypto for now. Or if the price didn't vary
                if self.data[row[self.contractDesc]][self.priceDesc] == 0 or (hasBoughtPrice and prevPancakeSwapPrice == self.data[row[self.contractDesc]][self.priceDesc]):
                    continue

                # If the prev price is 0, assign 0 to the result var price / prevPrice to avoid "Division by 0 error"
                if self.data[row[self.contractDesc]][self.prevPriceDesc] == 0:
                    commonFunctions.printInfo(f"La oportunidad de ORO!!!! {self.data[row[self.contractDesc]][self.symbolNameDesc]} --> {self.data[row[self.contractDesc]][self.prevPriceDesc]} // {self.data[row[self.contractDesc]][self.priceDesc]} BNB", bcolors.OKMSG)
                    percentageDiffWoFormat = 2
                else:
                    # Calculate diff percentage
                    percentageDiffWoFormat = self.data[row[self.contractDesc]][self.priceDesc] / self.data[row[self.contractDesc]][self.prevPriceDesc]
                
                # Format price vs. prevPrice percentage diff
                percentageDiff = commonFunctions.formatPercentages(percentageDiffWoFormat)

                # Double check to prevent insert info twice
                if (self.tradingType == 0 and (percentageDiff <= self.buyTrigger or percentageDiff >= self.sellTrigger)) or self.tradingType != 0:
                    #commonFunctions.printInfo(f"Current loop = {currentLoop} || Comprobamos doblemente para saber si realmente hemos de hacer trading de {self.data[row[self.contractDesc]][self.symbolDesc]} - {percentageDiff}", bcolors.BLUE)
                    self.getCsvSymbolsNotSold()
                else:
                    continue

                # Print to see the progress
                if self.tradingType != 0:

                    if percentageDiff >= 1000:
                        color = bcolors.BLUE
                    elif percentageDiff >= 50:
                        color = bcolors.WARN
                    else:
                        color = ""

                    commonFunctions.printInfo(f"{self.data[row[self.contractDesc]][self.symbolNameDesc]} ({row[self.contractDesc]})" +
                    f" --> Antes = {prevPrice} // Ahora = {self.data[row[self.contractDesc]][self.priceDesc]} BNB // Diff = {percentageDiff} %", color)

                # If we should buy or sell a crypto
                if ((self.tradingType == 0 and percentageDiff <= self.buyTrigger) or self.tradingType != 0)\
                and row[self.contractDesc] not in self.csvSymbolsNotSold: # buy
                    
                    color = bcolors.ERR
                    HTMLcolor = "red"
                    tradeAction = "Comprar"
                    urlAction = "outputCurrency"
                    isToBuy = True

                elif percentageDiff >= self.sellTrigger and prevPancakeSwapPrice > self.data[row[self.contractDesc]][self.priceDesc]\
                and row[self.contractDesc] in self.csvSymbolsNotSold: # sell

                    color = bcolors.OK
                    HTMLcolor = "green"
                    tradeAction = "Vender"
                    urlAction = "inputCurrency"
                    isToBuy = False

                else: # Nothing to do, so let's continue with the other coins
                    continue

                # Set trading transactions URLs
                buyURL = approveSellURL = sellURL = None

                if self.sendNotifications:
                    self.sendEmails(
                        tradeAction=tradeAction, urlAction=urlAction, cryptoData=self.data[row[self.contractDesc]],
                        percentageDiff=percentageDiff, color=HTMLcolor, token=row[self.contractDesc]
                    )

                # Trade and send notifications (Emails and WhatsApp)
                if self.isTrading: # and self.binanceSmartChainDesc in tokens.keys():

                    commonFunctions.printInfo(row[self.contractDesc], bcolors.OKMSG)
                    if isToBuy:
                        buyURL = self.buyToken(token=row[self.contractDesc])
                    else:
                        sellURLs = self.sellToken(token=row[self.contractDesc])

                        time.sleep(5)

                        if len(sellURLs) == 2:
                            approveSellURL = sellURLs[0]
                            sellURL = sellURLs[1]
                        elif len(sellURLs) == 1:
                            approveSellURL = sellURLs[0]

                
                if isToBuy: # buy

                    # Prepare data to insert in .csv file
                    tempRow = {}

                    for x, y in row.items():
                        tempRow[x] = y

                    tempRow[self.FK_cryptoIdDesc] = row[self.idDesc]
                    tempRow[self.contractDesc] = row[self.contractDesc]
                    tempRow[self.isSoldDesc] = 0
                    tempRow[self.isTradingDesc] = self.isTradingInt
                    tempRow[self.prevPriceDesc] = self.data[row[self.contractDesc]][self.prevPriceDesc]
                    tempRow[self.priceDesc] = self.data[row[self.contractDesc]][self.priceDesc]
                    tempRow[self.sellPriceDesc] = None
                    tempRow[self.percentageDiffDesc] = percentageDiff
                    tempRow[self.sellPercentageDiffDesc] = None
                    tempRow[self.buyDatetimeDesc] = dt.datetime.now()
                    tempRow[self.sellDatetimeDesc] = None
                    tempRow[self.realBuyPriceDesc] = None
                    tempRow[self.realSellPriceDesc] = None
                    tempRow[self.buyURLDesc] = buyURL
                    tempRow[self.approveSellURLDesc] = None
                    tempRow[self.sellURLDesc] = None

                    # To dataFrame
                    tempDf = pd.DataFrame([tempRow])

                    sqliteClass.db().insertIntoFromPandasDf(sourceDf=tempDf, targetTable="tradingHistory")

                else: # sell

                    color = bcolors.OK
                    HTMLcolor = "green"
                    tradeAction = "Vender"
                    urlAction = "inputCurrency"
                    isToBuy = False

                    # ------------------------------------------------------------------

                    sqliteClass.db().executeQuery(f"""
                        UPDATE tradingHistory
                        SET
                            {self.isSoldDesc} = 1,
                            {self.sellPriceDesc} = {self.data[row[self.contractDesc]][self.priceDesc]},
                            {self.sellPercentageDiffDesc} = {percentageDiff},
                            {self.sellDatetimeDesc} = {dt.datetime.now()},
                            {self.approveSellURLDesc} = {approveSellURL},
                            {self.sellURLDesc} = {sellURL}
                        WHERE
                            {self.isSoldDesc} = 0 AND
                            {self.isTradingDesc} = {self.isTradingInt} AND
                            {self.contractDesc} = {row[self.contractDesc]}
                    """)

                    # # Update .csv setting the new cells value
                    # tempfile = NamedTemporaryFile(mode='w', delete=False)

                    # df = pd.read_csv(self.tradingHistoryCsv, sep=self.separator)

                    # with open(self.tradingHistoryCsv, 'r', newline='') as csvfile, tempfile:

                    #     reader = csv.DictReader(csvfile, fieldnames=list(df), delimiter=self.separator)
                    #     writer = csv.DictWriter(tempfile, fieldnames=list(df), delimiter=self.separator, lineterminator='\n')

                    #     for r in reader:

                    #         if r[self.symbolDesc] == self.symbolDesc:
                    #             writer.writerow(r)
                    #             continue

                    #         if r[self.contractDesc] == row[self.contractDesc] and int(r[self.isTradingDesc]) == self.isTradingInt and int(r[self.isSoldDesc]) == 0:
                    #             r[self.isSoldDesc] = 1
                    #             r[self.sellPriceDesc] = self.data[row[self.contractDesc]][self.priceDesc]
                    #             r[self.sellPercentageDiffDesc] = percentageDiff
                    #             r[self.sellDatetimeDesc] = dt.datetime.now()
                    #             r[self.approveSellURLDesc] = approveSellURL
                    #             r[self.sellURLDesc] = sellURL

                    #         writer.writerow(r)

                    # shutil.move(tempfile.name, self.tradingHistoryCsv)

                #tokens = self.getTokens(cryptoSlug=self.data[row[self.contractDesc]][self.slugDesc])

                commonFunctions.printInfo(f"CurrentLoop = {currentLoop} || {percentageDiff} % --- {tradeAction} {self.data[row[self.contractDesc]][self.symbolNameDesc]} ({self.data[row[self.contractDesc]][self.symbolDesc]}"
                + f" - {row[self.contractDesc]}) // Ahora = {self.data[row[self.contractDesc]][self.priceDesc]} BNB, Antes = {self.data[row[self.contractDesc]][self.prevPriceDesc]} BNB", color)
                
                commonFunctions.printInfo(f"{self.pancakeSwapBaseUrl}inputCurrency={row[self.contractDesc]}", color)

        endDate = dt.datetime.now()
        #commonFunctions.printInfo(f"End loop {currentLoop} // Start = {startDate}, End = {endDate} ||| {endDate - startDate}", bcolors.WARN)

        #time.sleep(self.delay)


    def getCsvSymbolsNotSold(self):

        if not os.path.exists(self.tradingHistoryCsv):
            self.dfCsvSymbolsNotSold = pd.DataFrame()
            return
        
        df = pd.read_csv(self.tradingHistoryCsv, sep=self.separator)

        df[self.idDesc] = df[self.idDesc].astype(int)

        if self.tradingType == 0:
            df = df[df[self.isSoldDesc] == 0]

        self.dfCsvSymbolsNotSold = df[df[self.isTradingDesc] == self.isTradingInt]

        self.csvSymbolsNotSold = df[self.contractDesc].tolist()

        #commonFunctions.printInfo(self.csvSymbolsNotSold, bcolors.WARN)


    def getBscContracts(self, dataDf: pd.DataFrame()):

        if self.writeBscContractsHeader:
            commonFunctions.printInfo(f'No existe el fichero "{self.bscContractsCsv}"', bcolors.WARN)
            return

        # df = pd.read_csv(self.bscContractsCsv, sep=self.separator)

        df = sqliteClass.db().executeQuery(f"""
            SELECT
                id, symbol, symbolName, slug, contract
            FROM dimCryptos
            WHERE FK_typeId = {self.tradingType}
            """
        )

        df[self.idDesc] = df[self.idDesc].astype(int)

        self.contractTokensCsv = df[self.contractDesc].tolist()
        print(self.contractTokensCsv)

        # CoinMarketCap
        if self.tradingType == 0:

            df = df[df[self.contractDesc].notnull()]
            print(df)

            dataDf = dataDf[
                (dataDf[self.isActiveDesc] == 1)
                & (dataDf[self.fullyDilluttedMarketCapDesc] <= 1000000)
            ]
            print(dataDf)

            self.bscContractsDf = df.loc[df[self.contractDesc].isin(dataDf[self.contractDesc]),:]
        
        else:
            self.bscContractsDf = df

        print(self.bscContractsDf)


    # Insert token data if not in .csv file already
    def insertBscContracts(self, row):

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
            self.contractDesc: bscContract,
        }

        output = pd.DataFrame()
        output = output.append(tokenData, ignore_index=True)

        output.to_csv(self.bscContractsCsv, index=False, columns=tokenData.keys(), mode="a", header=self.writeBscContractsHeader)
        self.writeBscContractsHeader = False

        commonFunctions.printInfo(f"Contract insertado para {row[self.symbolNameDesc]} ({bscContract})", bcolors.OK)

        # Sleep time to prevent blocks
        time.sleep(3)


    def getData(self):

        dataDf = df = pd.DataFrame()

        while len(dataDf) == 0:

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
                            dataDf = df.drop(self.columnToExpand, axis=1).join(pd.DataFrame(df[self.columnToExpand].values.tolist()))

                            #print(len(df[df[self.priceDesc] <= 1]))

            except Exception as e:
                commonFunctions.printInfo(f"Error obteniendo datos en getData() {e.args}", bcolors.ERRMSG)
                
            if len(dataDf) == 0:
                commonFunctions.printInfo("No se han obtenido datos en getData()", bcolors.ERRMSG)
                time.sleep(self.delay)

        return dataDf


    # Send gmails, in case of ***ERROR***, allow this https://myaccount.google.com/lesssecureapps --> Explained here https://geekflare.com/send-gmail-in-python/
    def sendEmails(self, tradeAction, urlAction, cryptoData, percentageDiff, color, token):

        try:
            ssl_context = ssl.create_default_context()
            service = smtplib.SMTP_SSL(self.smtp_server_domain_name, self.port, context=ssl_context)
            service.login(self.sender_mail, self.password)

        except Exception as e:
            commonFunctions.printInfo(f"Error en sendEmails() {e.args}", bcolors.ERRMSG)
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

        # Send whatsapp message, not working anymore
        self.sendWhatsapp(message=whatsappContent)
        
        for email in self.recipientEmails:

            try:
                result = service.sendmail(self.sender_mail, email, f"Subject: {subject}\n{emailContent}")

            except Exception as e:
                commonFunctions.printInfo(f"Error enviando email en sendEmails() {e.args}", bcolors.ERRMSG)
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

            except Exception as e:
                commonFunctions.printInfo(f"Error obteniendo datos en getTokens() {e.args}", bcolors.ERRMSG)
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
            
                #commonFunctions.printInfo(f"WhatsApp message: {message.sid}", bcolors.OK)

        except Exception as e:
            commonFunctions.printInfo(f"No se ha/n podido enviar mensaje/s de WhatsApp {e.args}", bcolors.ERRMSG)


    def buyToken(self, token):

        try:
            
            balance = self.web3.eth.get_balance(self.senderAddress)
            humanReadable = self.web3.fromWei(balance,'ether')

            commonFunctions.printInfo(f"Total BNB amount: {humanReadable}", bcolors.WARN)
            
            #Contract Address of Token we want to buy
            tokenToBuy = self.web3.toChecksumAddress(token)        # web3.toChecksumAddress("0x6615a63c260be84974166a5eddff223ce292cf3d")
            spend = self.web3.toChecksumAddress(self.wbnbContract) # wbnb contract
            
            #Setup the PancakeSwap contract
            #contract = self.web3.eth.contract(address=self.pancakeSwapRouterContractAddress, abi=self.pancakeSwapRouterContractAddressAbi)

            nonce = self.web3.eth.get_transaction_count(self.senderAddress)

            pancakeswap2_txn = self.pancakeSwapRouter.functions.swapExactETHForTokensSupportingFeeOnTransferTokens( # swapExactETHForTokens
            0, # set to 0, or specify minimum amount of tokeny you want to receive - consider decimals!!!
            [spend,tokenToBuy],
            self.senderAddress,
            (int(time.time()) + 50000)
            ).buildTransaction({
            'from': self.senderAddress,
            'value': self.web3.toWei(self.bnbAmountToBuy,'ether'), # This is the Token(BNB) amount you want to Swap from
            'gas': self.gas,
            'gasPrice': self.gasPrice,
            'nonce': nonce,
            })
                
            signed_txn = self.web3.eth.account.sign_transaction(pancakeswap2_txn, private_key=self.privateKey)
            tx_token = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)


            commonFunctions.printInfo(f"Compra realizada! Transacción --> {self.bscscanTransactionBaseUrl}{self.web3.toHex(tx_token)}", bcolors.OKMSG)

            buyURL = self.bscscanTransactionBaseUrl + self.web3.toHex(tx_token)

        except Exception as e:
            commonFunctions.printInfo(f"Error en buyToken() {e.args}", bcolors.ERRMSG)
            buyURL = None

        return buyURL


    def sellToken(self, token):

        sellURLs = []

        try:

            sender_address = self.senderAddress #TokenAddress of holder
            spend = self.web3.toChecksumAddress(self.wbnbContract)  #WBNB Address

            #Get BNB Balance
            balance = self.web3.eth.get_balance(sender_address)
            humanReadable = self.web3.fromWei(balance,'ether')

            commonFunctions.printInfo(f"Total BNB amount: {humanReadable}", bcolors.WARN)
            
            #Contract id is the new token we are swaping to
            #contract_id = web3.toChecksumAddress("0xc9849e6fdb743d08faee3e34dd2d1bc69ea11a51")
            contract_id = self.web3.toChecksumAddress(token)
            
            #Setup the PancakeSwap contract
            #contract = self.web3.eth.contract(address=self.pancakeSwapRouterContractAddress, abi=self.pancakeSwapRouterContractAddressAbi)

            #Create token Instance for Token
            sellTokenContract = self.web3.eth.contract(contract_id, abi=self.sellAbi)

            #Get Token Balance
            balance = sellTokenContract.functions.balanceOf(sender_address).call()
            symbol = sellTokenContract.functions.symbol().call()
            readable = self.web3.fromWei(balance,'ether')

            if int(readable) == 0:
                commonFunctions.printInfo(f"El balance de {symbol} es 0 y no hay nada que vender", bcolors.WARN)
                return sellURLs

            commonFunctions.printInfo(f"Balance: {readable} {symbol}", bcolors.WARN)

            #Enter amount of token to sell
            tokenValue = self.web3.toWei(readable, 'ether')

            #Approve Token before Selling
            tokenValue2 = self.web3.fromWei(tokenValue, 'ether')
            start = time.time()
            approve = sellTokenContract.functions.approve(self.pancakeSwapRouterContractAddress, balance).buildTransaction({
                        'from': sender_address,
                        'gasPrice': self.gasPrice,
                        'nonce': self.web3.eth.get_transaction_count(sender_address),
                        })

            signed_txn = self.web3.eth.account.sign_transaction(approve, private_key=self.privateKey)
            sell_approved_tx_token = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)

            commonFunctions.printInfo(f"Venta aprobada --> {self.bscscanTransactionBaseUrl}{self.web3.toHex(sell_approved_tx_token)}", bcolors.OK)

            sellURLs.append(self.bscscanTransactionBaseUrl + self.web3.toHex(sell_approved_tx_token))

            # Wait after approve 10 seconds before sending transaction
            time.sleep(10)

            commonFunctions.printInfo(f"Canjeando {tokenValue2} {symbol} por BNB", bcolors.WARN)
            # Swaping exact Token for ETH 

            pancakeswap2_txn = self.pancakeSwapRouter.functions.swapExactTokensForETHSupportingFeeOnTransferTokens( # swapExactTokensForETH
                        tokenValue ,0, 
                        [contract_id, spend],
                        sender_address,
                        (int(time.time()) + 50000)

                        ).buildTransaction({
                        'from': sender_address,
                        'gasPrice': self.gasPrice,
                        'nonce': self.web3.eth.get_transaction_count(sender_address),
                        })
                
            signed_txn = self.web3.eth.account.sign_transaction(pancakeswap2_txn, private_key=self.privateKey)
            sell_tx_token = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)

            commonFunctions.printInfo(f"Venta realizada para {symbol}! Transacción --> {self.bscscanTransactionBaseUrl}{self.web3.toHex(sell_tx_token)}", bcolors.OKMSG)

            sellURLs.append(self.bscscanTransactionBaseUrl + self.web3.toHex(sell_tx_token))

        except Exception as e:
            commonFunctions.printInfo(f"Error en sellToken() {e.args}", bcolors.ERRMSG)
            time.sleep(self.delay)

        return sellURLs


    def sellEverything(self):

        # Update possible contracts
        self.getNewBscContracts()

        if self.isTradingInt != 1 or self.isTrading != True:
            commonFunctions.printInfo("No se pueden vender las cryptos si no asignamos isTrading = True", bcolors.ERRMSG)

            # CoinMarketCap
            if self.tradingType == 0:
                exit()
            else:
                return

        # For each dataframe row
        for i, row in self.bscContractsDf.iterrows():

            # Declare trading transaction URLs
            approveSellURL = sellURL = None

            sellURLs = self.sellToken(token=row[self.contractDesc])

            if len(sellURLs) == 0:
                continue
            elif len(sellURLs) == 2:
                approveSellURL = sellURLs[0]
                sellURL = sellURLs[1]
            elif len(sellURLs) == 1:
                approveSellURL = sellURLs[0]

            sqliteClass.db().executeQuery(f"""
                UPDATE tradingHistory
                SET
                    {self.isSoldDesc} = 1,
                    {self.sellPriceDesc} = {self.data[row[self.contractDesc]][self.priceDesc]},
                    {self.sellPercentageDiffDesc} = {0},
                    {self.sellDatetimeDesc} = {dt.datetime.now()},
                    {self.approveSellURLDesc} = {approveSellURL},
                    {self.sellURLDesc} = {sellURL}
                WHERE
                    {self.isSoldDesc} = 0 AND
                    {self.isTradingDesc} = {self.isTradingInt} AND
                    {self.contractDesc} = {row[self.contractDesc]}
            """)

            # # Update .csv setting the new cells value
            # tempfile = NamedTemporaryFile(mode='w', delete=False)

            # df = pd.read_csv(self.tradingHistoryCsv, sep=self.separator)

            # with open(self.tradingHistoryCsv, 'r', newline='') as csvfile, tempfile:

            #     reader = csv.DictReader(csvfile, fieldnames=list(df), delimiter=self.separator)
            #     writer = csv.DictWriter(tempfile, fieldnames=list(df), delimiter=self.separator, lineterminator='\n')

            #     for r in reader:

            #         if r[self.symbolDesc] == self.symbolDesc:
            #             writer.writerow(r)
            #             continue

            #         if r[self.contractDesc] == row[self.contractDesc] and int(r[self.isTradingDesc]) == self.isTradingInt and int(r[self.isSoldDesc]) == 0:
            #             r[self.isSoldDesc] = 1
            #             r[self.sellPriceDesc] = self.data[row[self.contractDesc]][self.priceDesc]
            #             r[self.sellPercentageDiffDesc] = 0
            #             r[self.sellDatetimeDesc] = dt.datetime.now()
            #             r[self.approveSellURLDesc] = approveSellURL
            #             r[self.sellURLDesc] = sellURL

            #         writer.writerow(r)

            # shutil.move(tempfile.name, self.tradingHistoryCsv)

    
    def checkExistingCryptos(self):

        # Update possible contracts
        self.getNewBscContracts()

        dataDf = sqliteClass.db().executeQuery(f"""
            SELECT
                *
            FROM vwTransactions
            """
        )

        # For each dataframe row
        for i, row in dataDf.iterrows():

            currentPrice = self.getPancakeSwapPrice(token=row[self.contractDesc])

            if currentPrice == 0:
                currentPrice = 1

            # Calculate diff percentage
            percentageDiffWoFormat = currentPrice / row[self.priceDesc]
            # Format price vs. prevPrice percentage diff
            percentageDiff = commonFunctions.formatPercentages(percentageDiffWoFormat)

            if percentageDiff >= 1000:
                color = bcolors.BLUE
            elif percentageDiff >= 50:
                color = bcolors.WARN
            else:
                color = ""

            commonFunctions.printInfo(f"{row[self.symbolNameDesc]} ({row[self.contractDesc]})" +
            f" --> Antes = {row[self.priceDesc]} // Ahora = {currentPrice} BNB // Diff = {percentageDiff} %", color)


    def insertDataIntoSQLite(self):

        # df = pd.read_csv("tokenFOMObscContracts.csv", sep=self.separator)
        # commonFunctions.printInfo(df)
        # df = df[[self.symbolDesc, self.symbolNameDesc, self.slugDesc, self.contractDesc]]
        # commonFunctions.printInfo(df)
        # df["FK_typeId"] = self.tradingType
        # commonFunctions.printInfo(df)

        exit()

        #sqliteClass.db().insertIntoFromPandasDf(sourceDf=df, targetTable="dimCryptos")
        #sqliteClass.db().insertIntoFromPandasDf(sourceDf=df, targetTable="tradingHistory")


    def main(self):

        # Update or sell contracts
        self.getNewBscContracts()

        # if os.path.exists(self.tradingHistoryCsv):
        #     os.remove(self.tradingHistoryCsv)

        loopsCounter = 0
        eachLoopsInfo = 10

        with ThreadPoolExecutor(max_workers=self.maxThreads) as executor:

            while True:

                if loopsCounter % eachLoopsInfo == 0:
                    commonFunctions.printInfo(f"--- For Loop: {loopsCounter}", bcolors.WARN)

                future = executor.submit(self.core, loopsCounter)
                loopsCounter += 1
                time.sleep(self.delay)
