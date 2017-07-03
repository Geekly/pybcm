import sys
import io
from pybcm.elementreader import ElementReader, ElementFileReader, ElementWebReader, PriceURL
from pybcm.vendors import *
from pybcm.config import BCMConfig
import pybcm.xpath_usage
import os.path
from lxml import etree
from lxml.html.clean import Cleaner
# from bs4 import BeautifulSoup as Soup
import logging

# //table/tbody/tr/td/font/b[text()="Currently Available"]


class ElementReaderIT():

    element_filename = "../Sampledata/BrickLink Price Guide - Part 3004 in Light Bluish Gray Color.htm"

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.DEBUG)
        log_ = logging.getLogger("TestElementReader")
        log_.debug("Test in TestElementREader.setUpClass")
        cls._config = BCMConfig('../config/bcm.ini')

        # cls._vendormap = VendorMap()
        pass

    def testElementReaderMethods(self):
        # vendormap_ = VendorMap()
        reader = ElementReader(VendorMap())
        self.assertNotEquals(reader, None)


    # def testElementWebReaderMethods(self):
    #     vendormap_ = VendorMap()
    #     # config_ = BCMConfig('../config/bcm.ini')
    #     reader1 = ElementWebReader(vendormap_, login=config_.username, config_.password='')
    #     pass
    #
    def testGetStoreElements(self):
        log_ = logging.getLogger("TestCleaner")
        self.assertTrue(os.path.isfile(self.element_filename))
        log_.info("Parsing item from file...")
        datatree = self.datatree # self.loadTree(self.element_filename)

        pass

    def testElementFileReaderMethods(self):
        log_ = logging.getLogger("TestElementFileReader")
        element_filename = "Sampledata/BrickLink Price Guide - Part 3004 in Light Bluish Gray Color.htm"
        self.assertTrue(os.path.isfile(element_filename))
        reader = ElementFileReader(VendorMap())
        item = reader.read_item_from_file(element_filename)

    def testStaticGetStoreElements(self):
        log_ = logging.getLogger("testGetStoreElements")
        # datatree = self.loadTree(self.element_filename)
        datatree_ = self.datatree
        storeelements = ElementReader.get_store_elements_from_tree(datatree_)
        log_.debug(str(storeelements))


if __name__ == '__main__':

    log = logging.getLogger("ElementReaderIT")
    config = BCMConfig('../config/bcm.ini')

    erit = ElementReaderIT()
    erit.setUpClass()

    url_t = PriceURL()
    url = url_t.expand('P', '3004', '1')
    print("Price URL: %s" % url)

    file_vmap = VendorMap()
    efr = ElementFileReader(file_vmap)

    fileitems = efr.read_item_from_file(ElementReaderIT.element_filename)

    #with io.open('etree_out.html', 'wb') as g:
    #    g.write(etree.tostring(datatree, pretty_print='true', encoding='utf-8'))

    url_vmap = VendorMap()
    eur = ElementWebReader(url_vmap, config.username, config.password)
    prices = eur.read_item_from_url('P', '3004', 1)
    log.debug(prices)


