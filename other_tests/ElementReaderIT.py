import requests
from lxml import html, etree

from deprecated import log
from deprecated.elementreader import PriceURL, URL_STORE_LINKS_XPATH
from pybcm.vendors import *

logger = log.setup_custom_logger(__name__)

USER_AGENT_DICT = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }

vmap = VendorMap()
url = PriceURL().expand('P', '3005', '23')
logger.info(url)

with requests.Session() as s:
    s.headers = USER_AGENT_DICT
    h = s.head(url=url, headers=dict(USER_AGENT_DICT)) # do it for the cookies
    r = s.get(url=url, headers=dict(USER_AGENT_DICT))
    tree = html.fromstring(r.content)
    stores = tree.xpath(URL_STORE_LINKS_XPATH)
    logger.info(stores)

for store in stores:
    logger.debug(etree.tostring(store))
    logger.debug(store.xpath("./td/a/img/@title"))

#for i in imgs:
#    print(etree.tostring(i))

#xp = response.selector.xpath(URL_STORE_LINKS_XPATH)
#logger.info(xp)
# create a response

# create a selector
xpath = URL_STORE_LINKS_XPATH



