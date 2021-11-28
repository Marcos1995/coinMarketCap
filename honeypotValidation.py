import commonFunctions

import requests
from bs4 import BeautifulSoup
import urllib.request, json

# ------------------------------------------------------------------------------------------

def getRealTradingPrice(tx="https://bscscan.com/tx/0x2e75d498f315ff772dfb835e7521f0c67a344d995381229f84b708759a69410c"):
    
    from requests_html import HTMLSession

    session = HTMLSession()

    url='https://bscscan.com/tokenholdings'
    token={'a': '0xFAe2dac0686f0e543704345aEBBe0AEcab4EDA3d'}

    r = session.get(tx)
    print(r)
    a = r.html.render(sleep=2)
    print(a)

    exit()

    resp = requests.get(tx)
    print(resp)
    soup = BeautifulSoup(resp.content, 'html.parser')
    print(soup)

    exit()

    link = "http://www.somesite.com/details.pl?urn=2344"

    f = urllib.request.urlopen(tx, timeout=10)
    myfile = f.read()

    print(myfile)
    exit()
    
    #while True:
    commonFunctions.printInfo(tx)
    """

    #try:
    html_page = urllib.request.urlopen(tx)
    print(html_page)
    soup = BeautifulSoup(html_page, "html.parser")
    print(soup)

    for link in soup.findAll('span'):
        href = str(link.get('data-original-title'))

        print(href)

    exit()
    """

    #except Exception as e:
        #commonFunctions.printInfo(f"Error obteniendo datos en getTokens() {e.args}", bcolors.ERRMSG)
        #time.sleep(self.delay)

    #return tokens