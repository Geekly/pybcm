import http
from lxml import html, etree
import requests
from pybcm.elementreader import PriceURL, URL_STORE_LINKS_XPATH
from pybcm.vendors import *
from bs4 import BeautifulSoup as Soup

import utils

logger = utils.setup_custom_logger('SpiderIT.py')

USER_AGENT_DICT = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }

# config = BCMConfig('../config/bcm.ini')

vmap = VendorMap()
#spider = ElementSpider(vmap)

url = PriceURL().expand('P', '3005', '23')
logger.info(url)

#cookies = http.cookiejar.CookieJar

with requests.Session() as s:
    s.headers = USER_AGENT_DICT
    h = s.head(url=url, headers=dict(USER_AGENT_DICT)) # do it for the cookies
    r = s.get(url=url, headers=dict(USER_AGENT_DICT))
    tree = html.fromstring(r.content)
    stores = tree.xpath(URL_STORE_LINKS_XPATH)
    logger.info(stores)

for store in stores:
    print(etree.tostring(store))
    print(store.xpath("./td/a/img/@title"))

#for i in imgs:
#    print(etree.tostring(i))



#xp = response.selector.xpath(URL_STORE_LINKS_XPATH)
#logger.info(xp)
# create a response



# create a selector
xpath = URL_STORE_LINKS_XPATH



