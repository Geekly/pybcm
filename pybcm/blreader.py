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

from lxml import etree

from .vendors import Vendor, VendorMap


class BricklinkReader(object):
    """ Base class for reading the information of a single Lego elementid

        Sub-class this file to read different data sources including Bricklink website and text file.

        Attributes:

        The BricklinkReader will read the information about a single Bricklink Item from the Price Catalog
        the color and type are not handled except in the URL of the webreader, which are passed in.

        #returns prices[] =([itemid, vendorid, vendorqty, vendorprice)
    """

    def __init__(self, vendormap):
        """ Start up..."""
        self._vendormap = vendormap

    @property
    def vendormap(self):
        return self._vendormap

    def readitemfromtree(self, datatree):
        """Parse the etree and return a price array

        """
        #global vendorMap
        prices = []
        stores = getstoreelementsfromtree(datatree)  # all store tr's
        if stores:  # check if list is empty
            suLink = re.compile("sID=(\d+).*itemID=(\d+)")  # \&itemID=(\d+)
            suStore = re.compile("Store:.(.*)\".title")
            suPrice = re.compile("[US\$\s~]")  # says that the \~ is redundant
            for store in stores:
                #print(etree.tostring(store))
                td = store.xpath('./td')
                #td[0] contains the Store name
                linktext = etree.tostring(td[0]).decode()
                #print( linktext)
                storematch = re.search(suLink, linktext)
                if storematch:
                    storeid = str(storematch.group(1))
                    #  we don't pay attention to this since it's defined upstream.
                    # TODO: we should check to see if retrived itemid are the same
                    itemid = storematch.group(2)
                    storenamematch = re.search(suStore, linktext)
                    storename = storenamematch.group(1)
                    #print("Storename: " + storename)

                    #td[1] contains the Quantity
                    quantity = int(td[1].text)
                    if quantity > 0:  # don't bother adding the vendor if it doesn't have any quantity for this item
                        #td[2] is empty
                        #td[3] contains the price
                        #BricklinkReader.vendormap.addvendor( Vendor(storeID, storename) )
                        self._vendormap.addvendor(Vendor(storeid, storename))
                        pricestring = td[3].text
                        price = float(re.sub(suPrice, '', pricestring))
                        prices.append([storeid, quantity, price])
                        #print([itemID, storeID, quantity, price])

        return prices


def getstoreelementsfromtree(datatree):
    """Extracts a list of stores and their price & quantity data from the datatree
        Args:
            datatree (lxml.etree):
    """
    #print(etree.tostring(datatree))
    topparents = datatree.xpath(
        "//td[table/tr/td/font/b[text()[contains(.,'Currently Available')]]]")  # contains all the info we want
    if topparents:
        currentroot = topparents[0]  # this table contains the Currently Available text and all of the other information
        #drill down to the table containing store entry tr's
        stores = currentroot.xpath("./table/tr/td/table/tr[td/a]")  # find all the rows that contain links
    else:
        stores = None

    return stores


class BricklinkWebReader(BricklinkReader):

    def __init__(self, vendormap, login='', password=''):
        """ Start up...
        :param vendormap:
        """
        BricklinkReader.__init__(self, vendormap)

        self._login = login
        self._password = password

        #self.blbrowser = twillbrowser()
        url = "https://www.bricklink.com/login.asp"
        self.blbrowser = SomeBrowser()
        self.blbrowser.login(url, self._login, self._password)

    def readitemfromurl(self, itemtypeID, itemID, itemColorID):
        # global vendorMap
        #extract the info from the site and return it as a dictionary
        # need to find and return itemID, storeID's, itemQty, itemPrice for each url
        # we also need to extract real vendor names during this search
        #returns prices[] =([itemid, vendorid, vendorqty, vendorprice)
        #BricklinkReader.vendormap = vendormap
        if not isinstance(self.vendormap, VendorMap):
            raise Exception("global vendorMap does not exist")
        url = "http://www.bricklink.com/catalogPG.asp?itemType=" + itemtypeID + '&itemNo=' + itemID + '&itemSeq=1&colorID=' + itemColorID + '&v=P&priceGroup=Y&prDec=2'
        logging.info("Reading item from %s" % url)
        #itemprices = []
        page = self.blbrowser.open(url)
        parser = etree.HTMLParser(remove_blank_text=True, remove_comments=True, encoding='utf-8')
        datatree = etree.HTML(page, parser)
        itemprices = self.readitemfromtree(datatree)
        return itemprices


class BricklinkFileReader(BricklinkReader):
    """ A Bricklink 'File' is a single html page in file format which represents a single part.
    It's mainly for testing purposes.
    """

    def __init__(self, vendormap):
        BricklinkReader.__init__(self, vendormap)

    def readitemfromfile(self, filename):
        parser = etree.HTMLParser(remove_blank_text=True, remove_comments=True, encoding='utf-8')
        with io.open(filename, 'r') as f:
            #print( "Parsing item from file..." )
            datatree = etree.HTML(f.read(), parser)
            #print( etree.tostring(datatree))
        itemprices = self.readitemfromtree(datatree)
        return itemprices


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
            #response = urllib.request.urlopen(req)            
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

        #def remove_accents(input_str):

        #nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
        #return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


if __name__ == '__main__':
    #filename = "../BrickLink Price Guide - Part 3070b in Black Color.htm"
    #prices = BricklinkFileReader(filename)
    #print prices.readAllItems() 

    logging.basicConfig(level=logging.DEBUG)
    logging.info('Started')

    # TODO:  replace login info with app config settings
    br = BricklinkWebReader("XXXXX", "XXXXXX")

    br.readitemfromurl('P', '3001', '80')
    br.readitemfromurl('P', '3001', '80')
    print(br.readitemfromurl('P', '3001', '80'))

    #bfr = BricklinkFileReader()
    #bfr.readItemFromFile("../BrickLink Price Guide - Part 3001 in Dark Green Color.htm")

    logging.info('Done!')