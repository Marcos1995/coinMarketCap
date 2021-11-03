# importing the requests library
import requests
import urllib.request, json
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import pandas as pd
import datetime as dt
import os

class TokenFOMO:

    def __init__(self, bscContractCsv):

        self.bscContractCsv = bscContractCsv

        # id,symbol,symbolName,slug,bscContract
        self.idDesc = "id"
        self.symbolDesc = "symbol"
        self.symbolNameDesc = "symbolName"
        self.slugDesc = "slug"
        self.bscContractDesc = "bscContract"

        self.nameDesc = "name"
        self.addrDesc = "addr"

        # Get data from TokenF0MO
        self.tokenFOMOurl = "https://tokenfomo.io/api/tokens/bsc"
        self.token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiX21hcmNvczE5OTUiLCJpYXQiOjE2MzUxMDUzMDAsImV4cCI6MTYzNzY5NzMwMH0.1fq2Ac6ho07hdJU3Uu98F6pnzCUZEyj6MLNR1_DzUdc"

        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

        self.newTokensDf = pd.DataFrame()

        currentTime = dt.datetime.now(dt.timezone.utc).astimezone()
        self.getHoursOffset = int(str(currentTime)[-6:-3])

        self.core()


    def getTokens(self, firstN=10):

        try:
            r = requests.get(self.tokenFOMOurl, headers=self.headers)
            if r.status_code == 200:
                newTokens = json.loads(r.content.decode('utf-8'))
            else:
                print("No hay datos de la API de tokenFOMO")
                exit()

            newTokensDf = pd.DataFrame(newTokens)
            newTokensDf["datetime"] = pd.to_datetime(newTokensDf['timestamp'], unit='s') + pd.Timedelta(hours=self.getHoursOffset)
            newTokensDf[self.symbolDesc] = newTokensDf[self.symbolDesc].str.replace('[^a-zA-Z0-9]', '', regex=True).str.strip()
            newTokensDf[self.nameDesc] = newTokensDf[self.nameDesc].str.replace('[^a-zA-Z0-9]', '', regex=True).str.strip()

            self.newTokensDf = newTokensDf.iloc[:firstN]

        except Exception as e:
            print(e)
            exit()


    def dropAndCreateFile(self):

        finalDf = pd.DataFrame()

        finalDf[self.idDesc] = self.newTokensDf.index
        finalDf[self.symbolDesc] = self.newTokensDf[self.symbolDesc]
        finalDf[self.symbolNameDesc] = self.newTokensDf[self.nameDesc]
        finalDf[self.slugDesc] = self.newTokensDf[self.symbolDesc]
        finalDf[self.bscContractDesc] = self.newTokensDf[self.addrDesc]

        # Do we need to write headers in the .csv file?
        if os.path.exists(self.bscContractCsv):
            os.remove(self.bscContractCsv)
        
        # Create file and insert data
        finalDf.to_csv(self.bscContractCsv, index=False, columns=list(finalDf), mode="a", header=True)


    def getBscContractCsvDf(self):
        return pd.read_csv(self.bscContractCsv)

    
    def core(self):
        self.getTokens(firstN=10)
        self.dropAndCreateFile()

# a = TokenFOMO()
# a.main()

"""
url = "https://tokenfomo.io/"

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

req = urllib.request.Request(url=url, headers=hdr)
print(req)
html_page = urllib.request.urlopen(req)
print(html_page.read())
exit()
soup = BeautifulSoup(html_page, "html.parser")

newTokens = json.loads(soup.find("script", id="__NEXT_DATA__").string)

#print(newTokens)

c = []

for i, d in newTokens["props"]["pageProps"]["tokens"].items():
    c.extend(d)

print(len(c))

df = pd.DataFrame(c)

print(list(df))

df = df[
    (df["network"] == "BSC")
    & (df["defunct"] == False)
    & (df["has_source_code"] == True)
    & (df["ready"] == True)
    & (df["source_md5"] is not None)
]

for column in df.columns:
    print(f"{column} // {len(df[column].unique())}")
    print(df[column].unique())
    print("-------------------------------------------------------------------")
"""