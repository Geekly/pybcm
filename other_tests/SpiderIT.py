import http
from lxml import html
import requests
from pybcm.elementreader import ElementSpider, PriceURL, URL_STORE_LINKS_XPATH
from pybcm.vendors import *
from bs4 import BeautifulSoup as Soup

import log

logger = log.setup_custom_logger('SpiderIT.py')

USER_AGENT_DICT = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }

# config = BCMConfig('../config/bcm.ini')

vmap = VendorMap()
#spider = ElementSpider(vmap)

url = PriceURL().expand('P', '3005', '23')
logger.info(url)

#cookies = http.cookiejar.CookieJar

r = requests.get(url=url, headers=dict(USER_AGENT_DICT))
tree = html.fromstring(r.content)
stores = tree.xpath(URL_STORE_LINKS_XPATH)
logger.info(stores)


#xp = response.selector.xpath(URL_STORE_LINKS_XPATH)
#logger.info(xp)
# create a response



# create a selector
xpath = URL_STORE_LINKS_XPATH



