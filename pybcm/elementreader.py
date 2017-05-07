"""
Created on Oct 26, 2012

@author: khooks
"""

import re
import io
import http.cookiejar
from urllib import request, parse
from urllib.error import HTTPError, URLError
import logging
from .vendors import Vendor, VendorMap
from lxml import etree


class ElementReader(object):
    """ Base class for reading the information of a single Lego elementid

        Sub-class this file to read different data sources including Bricklink website and text file.

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

    def read_item_from_tree(self, datatree):
        """Parse the etree and return a price array

        """
        # global vendor_map
        prices = []
        stores = self.get_store_elements_from_tree(datatree)  # all store tr's
        if stores:  # check if list is empty
            suLink = re.compile("sID=(\d+).*itemID=(\d+)")  # \&itemID=(\d+)
            suStore = re.compile("Store:.(.*)\".title")
            suPrice = re.compile("[US\$\s~]")  # says that the \~ is redundant
            for store in stores:
                # print(etree.tostring(store))
                td = store.xpath('./td')
                # td[0] contains the Store name
                linktext = etree.tostring(td[0]).decode()
                # print( linktext)
                storematch = re.search(suLink, linktext)
                if storematch:
                    storeid = str(storematch.group(1))
                    #  we don't pay attention to this since it's defined upstream.
                    # TODO: we should check to see if retrived itemid are the same
                    itemid = storematch.group(2)
                    storenamematch = re.search(suStore, linktext)
                    storename = storenamematch.group(1)
                    # print("Storename: " + storename)

                    # td[1] contains the Quantity
                    quantity = int(td[1].text)
                    if quantity > 0:  # don't bother adding the vendor if it doesn't have any quantity for this item
                        # td[2] is empty
                        # td[3] contains the price
                        # ElementReader.vendor_map.addVendor( Vendor(storeID, storename) )
                        self.__vendormap.addVendor(Vendor(storeid, storename))
                        pricestring = td[3].text
                        price = float(re.sub(suPrice, '', pricestring))
                        prices.append([storeid, quantity, price])
                        # print([itemID, storeID, quantity, price])

        return prices

    @staticmethod
    def get_store_elements_from_tree(datatree):
        """Extracts a list of stores and their price & quantity data from the datatree
            Args:
                datatree (lxml.etree):
        """
        # print(etree.tostring(datatree))
        topparents = datatree.xpath(
            "//td[table/tr/td/font/b[text()[contains(.,'Currently Available')]]]")  # contains all the info we want
        if topparents:
            currentroot = topparents[0]  # this table contains the Currently Available text and all of the
            # other information
            # drill down to the table containing store entry tr's
            stores = currentroot.xpath("./table/tr/td/table/tr[td/a]")  # find all the rows that contain links
        else:
            stores = None

        return stores


class ElementFileReader(ElementReader):
    """ A Bricklink 'File' is a single html page in file format which represents a single part.
    It's mainly for testing purposes.
    """

    def __init__(self, vendormap_):
        ElementReader.__init__(self, vendormap_)

    def read_item_from_file(self, filename):
        parser = etree.HTMLParser(remove_blank_text=True, remove_comments=True, encoding='utf-8')
        with io.open(filename, 'r') as f:
            # print( "Parsing item from file..." )
            datatree = etree.HTML(f.read(), parser)
            # print( etree.tostring(datatree))
        itemprices = self.read_item_from_tree(datatree)
        return itemprices


class ElementWebReader(ElementReader):

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
        page = self.blbrowser.open(url)
        parser = etree.HTMLParser(remove_blank_text=True, remove_comments=True, encoding='utf-8')
        datatree = etree.HTML(page, parser)
        itemprices = self.read_item_from_tree(datatree)
        return itemprices

    def is_logged_in(self, page):
        """Search the page for the log off URL to determine if currently logged in

        """
        logoff_url = 'href="https://www.bricklink.com/logoff.asp"'
        logoff_url_xpath = '/html/body/center/table[1]/tbody/tr/td/table/tbody/tr/td[3]/span/font/a'
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

    from .bcmconfig import BCMConfig

    logging.basicConfig(level=logging.DEBUG)
    logging.info('Started')

    vendormap = VendorMap()

    config = BCMConfig()
    br = ElementWebReader(vendormap, config.username, config.password)

    br.read_item_from_url('P', '3001', '80')
    br.read_item_from_url('P', '3001', '80')
    print(br.read_item_from_url('P', '3001', '80'))

    # bfr = ElementFileReader()
    # bfr.readItemFromFile("../BrickLink Price Guide - Part 3001 in Dark Green Color.htm")
    page = br.blbrowser.open('http://www.bricklink.com/my.asp')
    br.is_logged_in(page)

    logging.info('Done!')
