"""
Created on Oct 26, 2012

@author: khooks
"""

import re
import io
import requests
from lxml import html, etree
from uritemplate import URITemplate, expand
from vendors import VendorMap
import utils
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from legoutils import LegoElement
import logging

logger = utils.setup_custom_logger('root')
logger.debug('Begin elementreader.py')


class PriceURL:
    """ PriceURl implements an easily readible, funcational, and modifiable URL for retreiving prices
    :param item_type:
    :param item_number:
    :param  =color_id:
    
    Usage:
        url_template = PriceURL()
        uri = url_template.expand(item_type=itemtypeID, item_number=itemID, color_id=itemColorID)
        'https://www.bricklink.com/catalogPG.asp?P=3004&colorID=8'
    """

    url = ('https://www.bricklink.com/catalogPG.asp?'
           '{item_type} = {item_number} &'
           'colorID = {color_id}'
           )

    def __init__(self):
        self.raw_url = PriceURL.url.replace(" ", "")  # Spaces improved readability
        self.url_template = URITemplate(self.raw_url)

    def expand(self, itemtypeID, itemID, itemColorID):
        self.url = self.url_template.expand(item_type=itemtypeID, item_number=itemID, color_id=itemColorID)
        return self.url


USER_AGENT_DICT = {
    'User-Agent':
        ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko)'
         'Chrome/50.0.2661.102 Safari/537.36')}

#FILE_STORE_LINKS = '//tbody/tr/td/table[3]/tbody/tr[5]/td[3]/table[3]/tbody/tr/td/table/tbody/tr[td/a]'
URL_STORE_LINKS_XPATH = "(//td[contains(.,'Currently')])[2]/table[3]//tr[position()>=2 and position()<last()-6]"

STORE_CHILD_LINK = './/a/@href'
STORE_NAME = './/a/img/@title'
STORE_QTY = './td[2]/text()'
STORE_PRICE = './td[3]/text()'

StoreEntry = namedtuple('StoreEntry', 'elementid storeid storename price qty')

class ElementReader(metaclass=ABCMeta):
    """ Base class for reading the information of a single Lego elementid
        
        What we call Elements, Bricklink refers to as items.
        
        Sub-classes of this file read different data sources including Bricklink website and text file.

        Attributes:

        The ElementReader will read the information about a single Bricklink Item from the Price Catalog
        the color and type are not handled except in the URL of the webreader, which are passed in.

        #returns prices[] =([itemid, vendorid, vendorqty, vendorprice])
    """

    def __init__(self, vendormap_):
        """ Start up..."""
        self.__vendormap = vendormap_
        self.tree = None
        self._stores_element_list = list()
        self.prices = list()

    @property
    def vendor_map(self):
        return self.__vendormap

    @vendor_map.setter
    def vendor_map(self, vendormap_):
        self.__vendormap = vendormap_

    def build_price_list(self, element_id, store_elements_list):
        """
        Read a single item from its Price Guide page
            Vendor Name
            Vendor ID
            Vendor Price
            Vendor Qty
            Parse the etree and return a price list
        """
        self.prices = list()
        # store_elements_list = tree.xpath(URL_STORE_LINKS_XPATH) #list of tr elements

        if store_elements_list:  # check if list is empty
            suLink = re.compile("sID=(\d+).*itemID=(\d+)")  # \&itemID=(\d+)
            suStore = re.compile("Store:\s(.*)")
            suPrice = re.compile("\$(\d*.\d*)")  # says that the \~ is redundant
            for store in store_elements_list:
                # create text strings from the store element
                e_store_url = ''.join(store.xpath(STORE_CHILD_LINK))
                if not e_store_url:
                    raise IndexError(e_store_url)

                storematch = re.search(suLink, e_store_url)

                if storematch:
                    store_id, item_id = storematch.groups()
                    e_store_name = ''.join(store.xpath(STORE_NAME))
                    e_price = ''.join(store.xpath(STORE_PRICE))
                    e_qty = ''.join(store.xpath(STORE_QTY))

                    store_name_match = re.search(suStore, e_store_name)
                    store_name = store_name_match.group(1)
                    price = float(re.search(suPrice, e_price).group(1))
                    quantity = int(e_qty)

                    if quantity > 0:  # don't bother adding the vendor if it doesn't have any quantity for this item
                        self.vendor_map[store_id] = store_name
                        self.prices.append(StoreEntry(element_id, store_id, store_name, price, quantity))
                else:
                    raise ValueError('Cannot match a store URL')
        else:
            raise ValueError('List of store elements is empty')
        return self.prices


class ElementFileReader(ElementReader):
    """ A Bricklink 'File' is a single html page in file format which represents a single part.
    It's mainly for testing purposes. The element can't be specific, since there's only information
    about a single element in the file. We take what we get.
    """

    def __init__(self, vendormap_):
        ElementReader.__init__(self, vendormap_)

    @classmethod
    def read_store_list(cls, filename):
        with io.open(filename, 'rt') as f:
            html_string = f.read()
        tree = html.fromstring(html_string)
        element_stores = tree.xpath(URL_STORE_LINKS_XPATH)
        element_id = None
        return element_stores, element_id


class ElementWebReader(ElementReader):
    def __init__(self, vendormap_):
        """ Start up...
        :param vendormap_:
        """
        ElementReader.__init__(self, vendormap_)

    def get_price_list(self, itemtypeID, itemID, itemColorID):
        element_store_list, element_id = self.read_store_list(itemtypeID, itemID, itemColorID)
        _prices = self.build_price_list(element_id, element_store_list)
        return _prices, element_id

    def read_store_list(self, itemtypeID, itemID, itemColorID):
        """Returns a list of elements each containing store and price info
        """

        element_id = LegoElement.joinElement(itemID, itemColorID)
        url = PriceURL().expand(itemtypeID, itemID, itemColorID)

        with requests.Session() as s:
            s.headers = USER_AGENT_DICT
            # if the head isn't requested prior to the page request, the images will be missing
            _ = s.head(url=url, headers=dict(USER_AGENT_DICT))  # do it for the cookies
            r = s.get(url=url, headers=dict(USER_AGENT_DICT))
            tree = html.fromstring(r.content)

        self._stores_element_list = tree.xpath(URL_STORE_LINKS_XPATH)
        return self._stores_element_list, element_id


if __name__ == '__main__':
    # filename = "../BrickLink Price Guide - Part 3070b in Black Color.htm"
    # prices = ElementFileReader(filename)
    # print prices.readAllItems()

    from config import BCMConfig
    import logging

    logger.debug('Started')

    vendormap = VendorMap()

    br = ElementWebReader(vendormap)

    prices, elementid = br.get_price_list('P', '3005', '23')

    for p in prices:
        print(p)

    print(vendormap.__repr__())