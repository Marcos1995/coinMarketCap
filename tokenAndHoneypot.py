# importing the requests library
import requests
import urllib.request, json
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import urllib.request, json
import pandas as pd

# api-endpoint
URL = "https://honeypot.is/?address=0x925f039459f8932c62a6718bcc08b38125f0322c"

a = "https://tokensniffer.com/tokens/new" # "https://tokenfomo.io/?f=bsc" # "https://tokenfomo.io/_next/data/0L9_dSyYfw0z-HZMRaHjE/index.json?f=bsc"

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

req = urllib.request.Request(url=a, headers=hdr)
html_page = urllib.request.urlopen(req)
soup = BeautifulSoup(html_page, "html.parser")

newTokens = json.loads(soup.find("script", id="__NEXT_DATA__").string)

#print(newTokens)

c = []

for i, d in newTokens["props"]["pageProps"]["tokens"].items():
    c.extend(d)

print(len(c))

df = pd.DataFrame(c)

print(list(df))

df = df[df["network"] == "BSC"]

print(df)

# allHrefs = []

# for str in soup.find_all(id='__NEXT_DATA__'):
#     print(1)
#     print("-----------------------")

# with urllib.request.urlopen(req) as url:
#     rawData = json.loads(url.read().decode())

# print(rawData)