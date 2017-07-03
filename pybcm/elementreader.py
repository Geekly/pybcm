"""
Created on Oct 26, 2012

@author: khooks
"""

import re
import io
from uritemplate import URITemplate, expand
from brickbrowser import BrickBrowser
from vendors import VendorMap
from bs4 import BeautifulSoup as Soup

# from xpath_usage import *
from lxml import etree
import logging
import log

logger = log.setup_custom_logger('root')
# Override logging level
logger.setLevel(logging.DEBUG)
logger.debug('Begin elementreader.py')

FILE_STORE_LINKS = '//tbody/tr/td/table[3]/tbody/tr[5]/td[3]/table[3]/tbody/tr/td/table/tbody/tr[td/a]'
URL_STORE_LINKS_XPATH = '//*[@id="id-main-legacy-table"]/tbody/tr/td/table[3]/tbody/tr[4]/td[3]/table[3]/tbody/tr/td/table/tbody/tr[position()>=2 and position()<last()-6]'
# URL_STORE_LINKS_XPATH = "//*/table[2]/tbody/tr[5]/td[3]/table/tbody/tr/td/table/tbody/tr[count(td)>2][position()>=2]"
# //*[@id="id-main-legacy-table"]/tbody/tr/td/table[3]/tbody/tr[4]/td[3]/table/tbody/tr/td/table/tbody/tr[2]
# URL_STORE_LINKS_XPATH = ( '//tbody/tr/td/table[3]/tbody/tr[5]/td[3]/table[3]/tbody/tr/td/table/tbody/tr[count(td)=4][position()>=2]'
# '|//tbody/tr/td/table[3]/tbody/tr[4]/td[3]/table[3]/tbody/tr/td/table/tbody/tr[count(td)=3][position()>=2]')
# //tbody/tr/td/table[3]/tbody/tr[5]/td[3]/table[3]/tbody/tr/td/table/tbody/tr[position()>=2]
# //tbody/tr/td/table[3]/tbody/tr[5]/td[3]/table[3]/tbody/tr/td/table/tbody/tr[count(td)>2][position()>=2]

ALT_URL = '//*[@id="id-main-legacy-table"]/tbody/tr/td/table[3]/tbody/tr[5]/td[3]/table/tbody/tr/td/table'
STORE_CHILD_LINK = './td/a/@href'
STORE_NAME = './td/a/img/@alt'
STORE_PRICE = './td[4]/text()'
STORE_QTY = './td[2]/text()'


class PriceURL:
    # PriceURl implements an easily readible, funcational, and modifiable URL for retreiving prices

    # Usage:
    #    url_template = PriceURL()
    #    uri = url_template.expand(item_type=itemtypeID, item_number=itemID, color_id=itemColorID)
    #    'https://www.bricklink.com/catalogPG.asp?itemType = P & itemNo = 3004 & itemSeq = 1 & colorID = 8 & v = P & prDec = 2'

    """url = ('https://www.bricklink.com/catalogPG.asp?'
           'itemType = {item_type} &'
           'itemNo = {item_number} & itemSeq = 1 &'
           'colorID = {color_id} & v = P & prDec = 2')"""
    url = ('https://www.bricklink.com/catalogPG.asp?'
           '{item_type}={item_number} &'
           'colorID = {color_id}'
           )

    def __init__(self):
        self.raw_url = PriceURL.url.replace(" ", "")  # Spaces improved readability
        self.url_template = URITemplate(self.raw_url)

    def expand(self, itemtypeID, itemID, itemColorID):
        self.url = self.url_template.expand(item_type=itemtypeID, item_number=itemID, color_id=itemColorID)
        return self.url


class ElementReader(object):
    """ Base class for reading the information of a single Lego elementid
        
        What we call Elements, Bricklink refers to as items.
        
        Sub-classes of this file read different data sources including Bricklink website and text file.

        Attributes:

        The ElementReader will read the information about a single Bricklink Item from the Price Catalog
        the color and type are not handled except in the URL of the webreader, which are passed in.

        #returns prices[] =([itemid, vendorid, vendorqty, vendorprice)
    """

    parser = etree.HTMLParser(remove_comments=True, encoding='utf-8')

    def __init__(self, vendormap_):
        """ Start up..."""
        self.__vendormap = vendormap_

    @property
    def vendor_map(self):
        return self.__vendormap

    @vendor_map.setter
    def vendor_map(self, vendormap_):
        self.__vendormap = vendormap_

    def read_items_from_html(self, html_string, stores_xpath):
        datatree = etree.HTML(html_string, ElementReader.parser)
        itemprices = self.read_items_from_tree(datatree, stores_xpath)
        return itemprices

    @staticmethod
    def get_store_elements_from_tree(datatree, stores_xpath):
        """Extracts a list of store Elements (with url) and their price & quantity data from the datatree
                datatree (lxml.etree):
        """
        # xpath definitions are stored in xpath_usage.py

        store_rows = datatree.xpath(stores_xpath)
        if store_rows:
            stores = store_rows  # find all the rows that contain links
        else:
            stores = None
        return stores

    #  TODO: Make this function static

    def read_items_from_tree(self, datatree, stores_xpath):
        """
        Read a single item from its Price Guide page
            Vendor Name
            Vendor ID
            Vendor Price
            Vendor Qty
            Parse the etree and return a price array

        """
        # global vendor_map
        prices = []
        stores = self.get_store_elements_from_tree(datatree, stores_xpath)  # all store tr's
        if stores:  # check if list is empty
            suLink = re.compile("sID=(\d+).*itemID=(\d+)")  # \&itemID=(\d+)
            suStore = re.compile("Store\:\s(.*)")
            suPrice = re.compile("\$(\d*.\d*)")  # says that the \~ is redundant
            for store in stores:
                # create text strings from the store element
                link_list = store.xpath(STORE_CHILD_LINK)
                if link_list:
                    td_link = store.xpath(STORE_CHILD_LINK)[0]
                else:
                    raise IndexError(link_list)

                storematch = re.search(suLink, td_link)

                if storematch:
                    store_id, item_id = storematch.groups()
                    td_name = store.xpath(STORE_NAME)[0]
                    td_price = store.xpath(STORE_PRICE)[0]
                    td_qty = store.xpath(STORE_QTY)[0]

                    #  we don't pay attention to this since it's defined upstream.
                    # TODO: we should check to see if retrived itemid are the same

                    store_name_match = re.search(suStore, td_name)
                    # store_name = store_name_match.group(1)
                    price = float(re.search(suPrice, td_price).group(1))
                    quantity = int(td_qty)

                    if quantity > 0:  # don't bother adding the vendor if it doesn't have any quantity for this item
                        self.vendor_map[store_id] = td_name
                        # .addVendor(Vendor(store_id, store_name))
                        prices.append([store_id, quantity, price])

        return prices


class ElementFileReader(ElementReader):
    """ A Bricklink 'File' is a single html page in file format which represents a single part.
    It's mainly for testing purposes. The element can't be specifiec, since there's only information
    about a single element in the file. We take what we get.
    """

    def __init__(self, vendormap_):
        ElementReader.__init__(self, vendormap_)

    @staticmethod
    def read_html_from_file(filename):
        with io.open(filename, 'rt') as f:
            html_string = f.read()
        return html_string

    def read_item_from_file(self, filename):
        html_string = self.read_html_from_file(filename)
        itemprices = self.read_items_from_html(html_string, FILE_STORE_LINKS)
        return itemprices


class ElementWebReader(ElementReader):
    logoff_url = 'href="https://www.bricklink.com/logoff.asp"'

    def __init__(self, vendormap_, login='', password=''):
        """ Start up...
        :param vendormap_:
        """
        ElementReader.__init__(self, vendormap_)

        self._login = login
        self._password = password
        self.blbrowser = BrickBrowser(self._login, self._password)
        self.priceUrl = PriceURL()
        # login_response = self.blbrowser.login(url, self._login, self._password)
        # self.loggedin = self.is_logged_in(login_response)

    def read_html_from_url(self, itemtypeID, itemID, itemColorID):
        url = self.priceUrl.expand(itemtypeID, itemID, itemColorID)
        logging.info("Reading item from %s" % url)
        # itemprices = []
        page_ = self.blbrowser.open(url)
        return page_, url

    def read_item_from_url(self, itemtypeID, itemID, itemColorID):
        # global vendor_map
        # extract the info from the site and return it as a dictionary
        # need to find and return itemID, storeID's, itemQty, itemPrice for each url
        # we also need to extract real vendor names during this search
        # returns prices[] =([itemid, vendorid, vendorqty, vendorprice)

        page_, url = self.read_html_from_url(itemtypeID, itemID, itemColorID)
        itemprices = self.read_items_from_html(page_, URL_STORE_LINKS_XPATH)
        if len(itemprices) < 1:
            raise ValueError("No items were returned from URL")

        return itemprices

        # def is_logged_in(self, page):
        #     #TODO: verify this does what we hope it does
        #     """Search the page for the log off URL to determine if currently logged in
        #
        #     """
        #     # logoff_url = 'href="https://www.bricklink.com/logoff.asp"'
        #     logoff_url_xpath = LOGOFF_URL
        #     parser = etree.HTMLParser(remove_blank_text=True, remove_comments=True, encoding='utf-8')
        #     datatree = etree.HTML(page, parser)
        #     r = datatree.xpath(logoff_url_xpath)
        #     return


class ElementSpider(ElementReader):
    def __init__(self, vendormap_):
        """ Start up...
        :param vendormap_:
        """
        ElementReader.__init__(self, vendormap_)

    def get_element(self, itemtypeID, itemID, itemColorID):
        url = PriceURL().expand('P', '3005', '23')
        pass


if __name__ == '__main__':
    # filename = "../BrickLink Price Guide - Part 3070b in Black Color.htm"
    # prices = ElementFileReader(filename)
    # print prices.readAllItems()

    from config import BCMConfig

    logging.basicConfig(level=logging.DEBUG)
    logging.info('Started')

    vendormap = VendorMap()

    config = BCMConfig('../config/bcm.ini')
    br = ElementWebReader(vendormap, config.username, config.password)

    page = br.read_item_from_url('P', '3005', '23')

    # bfr = ElementFileReader()
    # bfr.readItemFromFile("../BrickLink Price Guide - Part 3001 in Dark Green Color.htm")
    page = br.blbrowser.open('http://www.bricklink.com/my.asp')
    br.is_logged_in(page)

    logging.info('Done!')
