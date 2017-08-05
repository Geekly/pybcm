# Copyright (c) 2012-2017, Keith Hooks
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Loads store inventory data for individual elements
"""

import io
import logging
import re
from abc import ABCMeta

import requests
from lxml import html
from uritemplate import URITemplate

import log
from legoutils import WantedElement, PriceTuple, Condition
from vendors import VendorMap

logger = logging.getLogger('pybcm.elementreader')


# logger.debug('Begin elementreader.py')


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

# FILE_STORE_LINKS = '//tbody/tr/td/table[3]/tbody/tr[5]/td[3]/table[3]/tbody/tr/td/table/tbody/tr[td/a]'

URL_NEW_LINKS_XPATH = "(//td[contains(.,'Currently')])[2]/table[3]//tr[position()>=2 and position()<last()-6]"
URL_USED_LINKS_XPATH = "(//td[contains(.,'Currently')])[4]/table[3]//tr[position()>=2 and position()<last()-6]"

STORE_CHILD_LINK = './/a/@href'
STORE_NAME = './/a/img/@title'
STORE_QTY = './td[2]/text()'
STORE_PRICE = './td[3]/text()'

# Part status codes
NEW = Condition.NEW
USED = Condition.USED





class ElementReader(metaclass=ABCMeta):
    """ Base class for reading the information of a single Lego elementid
        
        What we call Elements, Bricklink refers to as items.
        
        Sub-classes of this file read different data sources including Bricklink website and text file.

        Attributes:

        The ElementReader will read the information about a single Bricklink Item from the Price Catalog
        the color and type are not handled except in the URL of the webreader, which are passed in.

        #returns prices[] =([itemid, vendorid, vendorqty, vendorprice])
    """

    # regex matches
    suLink = re.compile("sID=(\d+).*(?:itemID|bindID)=(\d+)")
    suStore = re.compile("Store:\s(.*)")
    suPrice = re.compile("\$(\d*.\d*)")

    def __init__(self, vendormap_):
        """ Start up..."""
        # logger.debug("ElementReader.__init__()")
        self.vendormap = vendormap_
        self._tree = None
        self._stores_element_list = list()
        # self._prices = list()

    @property
    def vendormap(self):
        return self._vendormap

    @vendormap.setter
    def vendormap(self, vendormap_):
        self._vendormap = vendormap_

    # TODO: create a price dict first to prevent elementid/storeid duplicates, but return a list
    def _build_price_list(self, element_id, store_elements_lists):
        """
        
        store_elements_lists is a tuple of (NEW, USED) prices
        
        Parse the etree and return an element_id and list of PriceTuples
        
        Returns:
            list of Pricetuples 
        
        """
        _prices = []
        # store_elements_list = tree.xpath(URL_STORE_LINKS_XPATH) #list of tr elements
        print("Building price list for element: %s" % element_id)
        # TODO: convert to an array earlier for performance
        new_list = store_elements_lists[0]
        used_list = store_elements_lists[1]

        for idx, condition_store_list in enumerate(store_elements_lists):
            condition = [NEW, USED][idx]
            if condition_store_list:  # check if list is empty
                # suLink = re.compile("sID=(\d+).*(?:itemID|bindID)=(\d+)")  # \&itemID=(\d+)
                # suStore = re.compile("Store:\s(.*)")
                # suPrice = re.compile("\$(\d*.\d*)")  # says that the \~ is redundant
                for store in condition_store_list:
                    # look for NEW elements
                    # look for USED elements
                    # create text strings from the store element
                    e_store_url = ''.join(store.xpath(STORE_CHILD_LINK))
                    if not e_store_url:
                        raise IndexError(e_store_url)

                    storematch = re.search(self.suLink, e_store_url)

                    if storematch:
                        store_id, item_id = storematch.groups()
                        e_store_name = ''.join(store.xpath(STORE_NAME))
                        e_price = ''.join(store.xpath(STORE_PRICE))
                        e_qty = ''.join(store.xpath(STORE_QTY))

                        store_name_match = re.search(self.suStore, e_store_name)
                        store_name = store_name_match.group(1)
                        price = float(re.search(self.suPrice, e_price).group(1))
                        quantity = int(e_qty)

                        if quantity > 0:  # don't bother adding the vendor if it doesn't have any quantity for this item
                            self.vendormap[store_id] = store_name
                            # check if there are already price/qty entries for this element
                            item_key = (element_id, store_id)
                            if item_key in _prices:
                                # TODO: handle this better by choosing the "best" entry to keep instead of just the first
                                logger.debug("Duplicate store entry found: %s" % (item_key,))
                            else:
                                # TODO: add condition as an arguement
                                _prices.append( PriceTuple(element_id, store_id, store_name, price,
                                                                             quantity, condition))
                    else:
                        raise ValueError('Cannot match a store URL')
            else:
                raise ValueError('List of store elements is empty')
                # convert dict to list and return it

        return _prices


class ElementFileReader(ElementReader):
    """ A Bricklink 'File' is a single html page in file format which represents a single part.
    It's mainly for testing purposes. The element can't be specific, since there's only information
    about a single element in the file. We take what we get.
    """

    def __init__(self, vendormap_):
        super().__init__(vendormap_)

    @classmethod
    def read_store_list(cls, filename):
        with io.open(filename, 'rt') as f:
            html_string = f.read()
        tree = html.fromstring(html_string)
        element_stores = tree.xpath(URL_NEW_LINKS_XPATH)
        element_id = None
        return element_stores, element_id


class ElementWebReader(ElementReader):
    def __init__(self, vendormap_):
        """ Start up...
        :param vendormap_:
        """
        # logger.debug("ElementWebReader.__init__()")
        logger.debug("ElementWebReader vendormap id: %s" % id(vendormap_))
        super().__init__(vendormap_)

    def web_price_list(self, itemtypeID, itemID, itemColorID, options=NEW | USED):
        element_id, element_store_lists = self._read_store_list(itemtypeID, itemID, itemColorID, options)
        price_list = self._build_price_list(element_id, element_store_lists)
        return element_id, price_list

    @classmethod
    def _read_store_list(cls, itemtypeID, itemID, itemColorID, options):
        """Returns a tuple (NEW, USED) of store element lists each containing store and price info
        """
        logger.debug("Reading element %s, %s, %s from web" % (itemtypeID, itemID, itemColorID))
        element_id = WantedElement.joinElement(itemID, itemColorID)
        url = PriceURL().expand(itemtypeID, itemID, itemColorID)
        logger.info("Gathering data at %s" % url)
        with requests.Session() as s:
            s.headers = USER_AGENT_DICT
            # if the head isn't requested prior to the page request, the images will be missing
            _ = s.head(url=url, headers=dict(USER_AGENT_DICT))  # do it for the cookies
            r = s.get(url=url, headers=dict(USER_AGENT_DICT))
            tree = html.fromstring(r.content)

        new_list, used_list = None, None

        if NEW & options:
            new_list = tree.xpath(URL_NEW_LINKS_XPATH)
        if USED & options:
            used_list = tree.xpath(URL_USED_LINKS_XPATH)

        store_elements_lists = (new_list, used_list)

        return element_id, store_elements_lists


if __name__ == '__main__':
    # filename = "../BrickLink Price Guide - Part 3070b in Black Color.htm"
    # prices = ElementFileReader(filename)
    # print prices.readAllItems()
    logger = log.setup_custom_logger('pybcm.elementreader')

    logger.debug('Started elementreader.py')

    vendormap = VendorMap()

    br = ElementWebReader(vendormap)

    elementid, prices = br.web_price_list('P', '3005', '23')

    for p in prices:
        print(p.elementid)

    print(vendormap.__repr__())
