import sys
import io
from pybcm.elementreader import ElementReader, ElementFileReader, ElementWebReader
from pybcm.vendors import *
from pybcm.bcmconfig import BCMConfig
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
    def loadTree(cls, element_filename):
        log = logging.getLogger("TestElementReader.loadTree")
        with io.open(element_filename, 'rt') as f:
            file_text = f.read()
            clean_text = cls.clean(file_text)
            soup = Soup(clean_text, 'lxml')
            log.debug(str(soup))
        with io.open('etree_out.html', 'w') as g:
            g.write(str(soup))
        parser = etree.HTMLParser(encoding='utf-8')  # remove_blank_text=True, remove_comments=True, encoding='utf-8')
        root = etree.fromstring(clean_text, parser)
        return root

    @classmethod
    def clean(cls, text):
        """
        :type text: cleaned html
        """
        log = logging.getLogger("TestElementReader.clean")

        try:
            cleaner_ = Cleaner(scripts=True, embedded=True, meta=True, style=True, comments=True)
                              # remove_tags=['a', 'li', 'td'])
            clean_text = cleaner_.clean_html(text)
            clean_text = clean_text.replace('\n', '').replace('\t', '')
            log.info("Removed " + (str(len(text) - len(clean_text))) + " characters removed.")
            return clean_text

        except Exception as e:
            log.debug(e)
            log.debug(sys.exc_info())
            raise Exception('Error in clean_html')
            return text


    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.DEBUG)
        log = logging.getLogger("TestElementReader")
        log.debug("Test in TestElementREader.setUpClass")
        cls._config = BCMConfig('../config/bcm.ini')

        # cls._vendormap = VendorMap()
        pass

    def _testElementReaderMethods(self):
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
        log = logging.getLogger("TestCleaner")

        self.assertTrue(os.path.isfile(self.element_filename))

        log.info("Parsing item from file...")
        datatree = self.datatree # self.loadTree(self.element_filename)

        pass

    def testElementFileReaderMethods(self):
        log = logging.getLogger("TestElementFileReader")
        element_filename = "Sampledata/BrickLink Price Guide - Part 3004 in Light Bluish Gray Color.htm"
        self.assertTrue(os.path.isfile(element_filename))
        reader = ElementFileReader(VendorMap())
        # item = reader.read_item_from_file(element_filename)

    def testStaticGetStoreElements(self):
        log = logging.getLogger("testGetStoreElements")
        # datatree = self.loadTree(self.element_filename)
        datatree = self.datatree
        storeelements = ElementReader.get_store_elements_from_tree(datatree)
        log.debug(str(storeelements))


if ( __name__ == '__main__'):

    log = logging.getLogger("ElementReaderIT")

    erit = ElementReaderIT()
    erit.setUpClass()

    efr = ElementFileReader(VendorMap())
    datatree = efr.read_tree_from_file(ElementReaderIT.element_filename)
    with io.open('etree_out.html', 'wb') as g:
        g.write(etree.tostring(datatree, pretty_print='true', encoding='utf-8'))
    log.debug(datatree)
    items = efr.read_items_from_tree(datatree)


