from typing import final
import commonFunctions
import sqliteClass

import bcolors
import requests
import urllib.request, json
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import pandas as pd
import datetime as dt
import os

class tokenFOMO:

    def __init__(self, contractCsv, tradingType=3, firstN=10):

        self.contractCsv = contractCsv
        self.tradingType = tradingType
        self.firstN = firstN

        # id,symbol,symbolName,slug,contract
        self.idDesc = "id"
        self.symbolDesc = "symbol"
        self.symbolNameDesc = "symbolName"
        self.slugDesc = "slug"
        self.contractDesc = "contract"
        self.FK_typeIdDesc = "FK_typeId"

        self.nameDesc = "name"
        self.addrDesc = "addr"

        self.timestampDesc = "timestamp"
        self.lauchDatetimeDesc = "launchDatetime"

        self.regexNonAlphaNumerical = "[^a-zA-Z0-9]"

        # Get data from TokenF0MO
        self.tokenFOMOurl = "https://tokenfomo.io/api/tokens/bsc"
        self.token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoianRkMDIzIiwiaWF0IjoxNjM4MTUyMTYwLCJleHAiOjE2Mzg3NTY5NjB9.k6nNJCdEtpaP9v1G6o-kJ5FuMuX11kEt6xGyUQAh5Cc"
        #self.token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiX21hcmNvczE5OTUiLCJpYXQiOjE2MzUxMDUzMDAsImV4cCI6MTYzNzY5NzMwMH0.1fq2Ac6ho07hdJU3Uu98F6pnzCUZEyj6MLNR1_DzUdc"

        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

        self.newTokensDf = pd.DataFrame()

        currentTime = dt.datetime.now(dt.timezone.utc).astimezone()
        self.getHoursOffset = int(str(currentTime)[-6:-3])

        self.core()


    def getTokens(self):

        try:
            r = requests.get(self.tokenFOMOurl, headers=self.headers)
            if r.status_code == 200:
                newTokens = json.loads(r.content.decode('utf-8'))
            else:
                commonFunctions.printInfo("No hay datos de la API de tokenFOMO", bcolors.ERRMSG)
                exit()

            newTokensDf = pd.DataFrame(newTokens)
            newTokensDf[self.lauchDatetimeDesc] = pd.to_datetime(newTokensDf[self.timestampDesc], unit='s') # ADD tinezone time -> + pd.Timedelta(hours=self.getHoursOffset)
            newTokensDf[self.symbolDesc] = newTokensDf[self.symbolDesc].str.replace(self.regexNonAlphaNumerical, '', regex=True).str.strip()
            newTokensDf[self.nameDesc] = newTokensDf[self.nameDesc].str.replace(self.regexNonAlphaNumerical, '', regex=True).str.strip()

            self.newTokensDf = newTokensDf.iloc[:self.firstN]

            print(self.newTokensDf)

            #exit()

        except Exception as e:
            commonFunctions.printInfo(e, bcolors.ERRMSG)
            exit()


    def insertData(self):

        finalDf = pd.DataFrame()

        #finalDf[self.idDesc] = self.newTokensDf.index
        finalDf[self.symbolDesc] = self.newTokensDf[self.symbolDesc]
        finalDf[self.symbolNameDesc] = self.newTokensDf[self.nameDesc]
        finalDf[self.slugDesc] = self.newTokensDf[self.symbolDesc]
        finalDf[self.contractDesc] = self.newTokensDf[self.addrDesc]
        finalDf[self.lauchDatetimeDesc] = self.newTokensDf[self.lauchDatetimeDesc]
        finalDf[self.FK_typeIdDesc] = self.tradingType

        sqliteClass.db().insertIntoFromPandasDf(sourceDf=finalDf, targetTable="dimCryptos")

        # # Do we need to write headers in the .csv file?
        # if os.path.exists(self.contractCsv):
        #     os.remove(self.contractCsv)
        
        # # Create file and insert data
        # finalDf.to_csv(self.contractCsv, index=False, columns=list(finalDf), mode="a", header=True)

    
    def core(self):
        self.getTokens()
        self.insertData()

# a = tokenFOMO(contractCsv="")


# url = "https://tokenfomo.io/"

# hdr = {
# 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux aarch64; rv:94.0) Gecko/20100101 Firefox/94.0',
# 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
# 'Accept-Language': 'en-US,en;q=0.5',
# 'Accept-Encoding': 'gzip, deflate, br',
# 'Connection': 'keep-alive',
# 'Cookie': 'h=58288152257d54ff2b26078b1837aba2933f3a1de801d46ac04815e37a7c744a8663a5ea488eafee545e85ddd69bad7468657b943debd7fe361a73c3a8883fdc0984ecf5538c0189d097d074110ebed58c4374e590fe6c8247bd95d9ff235b05e83ee06176f72c571e1515c52bf651852ff613338fd24e850b75b2a9c749bbe58adbcd7531154cb940106d9012e2ed35702e3736c0a02bf163bebbdb2dd55409580a39f4e708e858b35b4b0c3f6c1c0e213aabc435012d8a7f2b171a7ee9ab6fcfcf97f852467e38003b11eded28e60dcbd768c7c7d88653123dddb30eb0fdfa31c8e7ea81e0b87340f175f20504a2cf2e001371151ad16cb366a13edd36785ffb5cd7a08ecf51bbfc7f5cc3e8ad4128c6632099c42570dcf5d9027de2433d5de8343d6cef4441740f5a4283e7a6f975be39b5da02cc5b26cd3912f01de060217d94e650348dc621a183899094d9606d47f71e7e53928cc4d4b78542617cbac0a28b10dfc1ba6a7aa7fac0dfa2285f802817a4fae48a8ee5bf998813071391e64e8909d7b3c436d1f6a0a2a293b35ff2f2362d349408c2ea120d774bc51745edd1caaa107f4017dbfeae4ef18ee5b93dbcbedc5364bfb1e099c86cd1b370d91139c3fde922b2f071f5bcaa4c50b8c2004b60e09f9b08f5cdb0fff35ce7074b56617cceb30f3c3b011914ebb1b19c2256a0f679ce7ce8b163e048bd5ae1da4f05',
# 'Upgrade-Insecure-Requests': '1',
# 'Sec-Fetch-Dest': 'document',
# 'Sec-Fetch-Mode': 'navigate',
# 'Sec-Fetch-Site': 'none',
# 'Sec-Fetch-User': '?1',
# 'Sec-GPC': '1',
# 'Pragma': 'no-cache',
# 'Cache-Control': 'no-cache'
# }
# # hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
# #        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
# #        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
# #        'Accept-Encoding': 'none',
# #        'Accept-Language': 'en-US,en;q=0.8',
# #        'Connection': 'keep-alive'}

# req = urllib.request.Request(url=url, headers=hdr)
# print(req)
# html_page = urllib.request.urlopen(req)
# data = html_page.read()[:10]

# print(data)

# data = data.encode('hex', errors='ignore')
# print(data)
# exit()
# contents = data.decode('utf-16', 'ignore')

# print(contents)

# #print(base64.b64decode(data))

# print(type(data))
# print(len(data))
# print(ord(str(data)[0]))
# bytesObj = data
# string = bytesObj.decode('utf-8')
# print(string)
# print(123)
# exit()
# # import HTMLSession from requests_html
# from requests_html import HTMLSession
 
# # create an HTML Session object
# session = HTMLSession()
 
# # Use the object above to connect to needed webpage
# resp = session.get(url, headers=hdr)

# print(resp)
 
# # Run JavaScript code on webpage
# print(
#     resp.html.render()
# )

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support.expected_conditions import presence_of_element_located

# #This example requires Selenium WebDriver 3.13 or newer
# with webdriver.Firefox() as driver:
#     wait = WebDriverWait(driver, 10)
#     driver.get(url)
#     #driver.find_element(By.ID, "__NEXT_DATA__")#.send_keys("cheese" + Keys.RETURN)
#     first_result = wait.until(presence_of_element_located((By.ID, "__NEXT_DATA__")))
#     print(first_result.get_attribute("textContent"))


# soup = BeautifulSoup(html_page, "html.parser")

# newTokens = json.loads(soup.find("script", id="__NEXT_DATA__").string)

# #print(newTokens)

# c = []

# for i, d in newTokens["props"]["pageProps"]["tokens"].items():
#     c.extend(d)

# print(len(c))

# df = pd.DataFrame(c)

# print(list(df))

# df = df[
#     (df["network"] == "BSC")
#     & (df["defunct"] == False)
#     & (df["has_source_code"] == True)
#     & (df["ready"] == True)
#     & (df["source_md5"] is not None)
# ]

# for column in df.columns:
#     print(f"{column} // {len(df[column].unique())}")
#     print(df[column].unique())
#     print("-------------------------------------------------------------------")
