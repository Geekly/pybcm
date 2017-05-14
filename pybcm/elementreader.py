"""
Created on Oct 26, 2012

@author: khooks
"""

import re
import io
import http.cookiejar
from urllib import request, parse
from urllib.error import HTTPError, URLError
from vendors import Vendor, VendorMap
from xpath_usage import *
from lxml import etree
import logging

class ElementReader(object):
    """ Base class for reading the information of a single Lego elementid
        
        What we call Elements, Bricklink refers to as items.
        
        Sub-classes of this file read different data sources including Bricklink website and text file.

        Attributes:

        The ElementReader will read the information about a single Bricklink Item from the Price Catalog
        the color and type are not handled except in the URL of the webreader, which are passed in.

        #returns prices[] =([itemid, vendorid, vendorqty, vendorprice)
    """

    def __init__(self, vendormap_):
        """ Start up..."""
        self.__vendormap = vendormap_

    @property
    def vendor_map(self):
        return self.__vendormap

    @vendor_map.setter
    def vendor_map(self, vendormap_):
        self.__vendormap = vendormap_

    @staticmethod
    def get_store_elements_from_tree(datatree):
        """Extracts a list of store Elements (with url) and their price & quantity data from the datatree
                datatree (lxml.etree):
        """
        # xpath definitions are stored in xpath_usage.py
        store_rows = datatree.xpath(STORE_LINKS)
        if store_rows:
            stores = store_rows  # find all the rows that contain links
        else:
            stores = None
        return stores

    #  TODO: Make this function static
    def read_items_from_tree(self, datatree):
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
        stores = self.get_store_elements_from_tree(datatree)  # all store tr's
        if stores:  # check if list is empty
            suLink = re.compile("sID=(\d+).*itemID=(\d+)")  # \&itemID=(\d+)
            suStore = re.compile("Store\:\s(.*)")
            suPrice = re.compile("\$(\d*.\d*)")  # says that the \~ is redundant
            for store in stores:
                # create text strings from the store element
                link_list = store.xpath(STORE_CHILD_LINK)
                if (link_list):
                    td_link = store.xpath(STORE_CHILD_LINK)[0]
                else:
                    raise IndexError(td_link)

                storematch = re.search(suLink, td_link)

                if storematch:
                    store_id, item_id = storematch.groups()
                    td_name = store.xpath(STORE_NAME)[0]
                    td_price = store.xpath(STORE_PRICE)[0]
                    td_qty = store.xpath(STORE_QTY)[0]

                    #  we don't pay attention to this since it's defined upstream.
                    # TODO: we should check to see if retrived itemid are the same

                    store_name_match = re.search(suStore, td_name)
                    store_name = store_name_match.group(1)
                    price = float(re.search(suPrice, td_price).group(1))
                    quantity = int(td_qty)

                    if quantity > 0:  # don't bother adding the vendor if it doesn't have any quantity for this item
                        self.__vendormap.addVendor(Vendor(store_id, store_name))
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
    def read_tree_from_file(filename):
        parser = etree.HTMLParser(remove_blank_text=True, remove_comments=True, encoding='utf-8')
        with io.open(filename, 'r') as f:
            datatree = etree.HTML(f.read(), parser)
        return datatree

    # TODO: move to ElementReader
    def read_item_from_file(self, filename):
        datatree = self.read_tree_from_file(filename)

        itemprices = self.read_items_from_tree(datatree)
        return itemprices


class ElementWebReader(ElementReader):

    logoff_url = 'href="https://www.bricklink.com/logoff.asp"'

    def __init__(self, vendormap, login='', password=''):
        """ Start up...
        :param vendormap:
        """
        ElementReader.__init__(self, vendormap)

        self._login = login
        self._password = password

        # self.blbrowser = twillbrowser()
        url = "https://www.bricklink.com/login.asp"
        self.blbrowser = SomeBrowser()
        login_response = self.blbrowser.login(url, self._login, self._password)
        self.loggedin = self.is_logged_in(login_response)

    def read_item_from_url(self, itemtypeID, itemID, itemColorID):
        # global vendor_map
        # extract the info from the site and return it as a dictionary
        # need to find and return itemID, storeID's, itemQty, itemPrice for each url
        # we also need to extract real vendor names during this search
        # returns prices[] =([itemid, vendorid, vendorqty, vendorprice)
        # ElementReader.vendor_map = vendor_map
        if not isinstance(self.vendor_map, VendorMap):
            raise Exception("global vendor_map does not exist")
        url = "http://www.bricklink.com/catalogPG.asp?itemType=" + itemtypeID + '&itemNo=' + itemID + '&itemSeq=1&colorID=' + itemColorID + '&v=P&priceGroup=Y&prDec=2'
        logging.info("Reading item from %s" % url)
        # itemprices = []
        page_ = self.blbrowser.open(url)
        parser = etree.HTMLParser(remove_blank_text=True, remove_comments=True, encoding='utf-8')
        datatree = etree.HTML(page_, parser)
        itemprices = self.read_items_from_tree(datatree)
        return itemprices

    def is_logged_in(self, page):
        #TODO: verify this does what we hope it does
        """Search the page for the log off URL to determine if currently logged in
        
        """
        # logoff_url = 'href="https://www.bricklink.com/logoff.asp"'
        logoff_url_xpath = LOGOFF_URL
        parser = etree.HTMLParser(remove_blank_text=True, remove_comments=True, encoding='utf-8')
        datatree = etree.HTML(page, parser)
        r = datatree.xpath(logoff_url_xpath)
        return


class SomeBrowser:
    def __init__(self):

        self.url = ''
        self.response = ''
        self.data = ''
        self.cookies = http.cookiejar.CookieJar()
        self.opener = request.build_opener(
            request.HTTPRedirectHandler(),
            request.HTTPSHandler(debuglevel=0),
            request.HTTPCookieProcessor(self.cookies))

    def open(self, url):
        try:
            self.url = url
            req = request.Request(self.url)
            response = self.opener.open(req)
            # response = urllib.request.urlopen(req)
            the_page = response.read()
            logging.debug("Opening URL:" + url)
            return the_page
        except HTTPError as e:
            logging.debug("Http Error: ", e.code, url)
        except URLError as e:
            logging.debug("URL Error:", e.reason, url)

    def login(self, url, loginname, passwd):

        try:
            self.url = url
            values = {
                'a': 'a',
                'logFrmFlag': 'Y',
                'frmUserName': loginname,
                'frmPassword': passwd}

            data = parse.urlencode(values).encode('utf-8')
            response = self.opener.open(url, data)
            the_page = response.read().decode('utf-8')
            return the_page
        except HTTPError as e:
            logging.debug("Http Error: ", e.code, url)
        except URLError as e:
            logging.debug("URL Error:", e.reason, url)

            # def remove_accents(input_str):

            # nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
            # return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


if __name__ == '__main__':
    # filename = "../BrickLink Price Guide - Part 3070b in Black Color.htm"
    # prices = ElementFileReader(filename)
    # print prices.readAllItems()

    from bcmconfig import BCMConfig

    logging.basicConfig(level=logging.DEBUG)
    logging.info('Started')

    vendormap = VendorMap()

    config = BCMConfig('../config/bcm.ini')
    br = ElementWebReader(vendormap, config.username, config.password)

    br.read_item_from_url('P', '3001', '80')
    br.read_item_from_url('P', '3001', '80')
    print(br.read_item_from_url('P', '3001', '80'))

    # bfr = ElementFileReader()
    # bfr.readItemFromFile("../BrickLink Price Guide - Part 3001 in Dark Green Color.htm")
    page = br.blbrowser.open('http://www.bricklink.com/my.asp')
    br.is_logged_in(page)

    logging.info('Done!')
