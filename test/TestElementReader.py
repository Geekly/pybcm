import sys
import io
import unittest
from pybcm.elementreader import ElementReader, ElementFileReader, ElementWebReader
from pybcm.vendors import *
from pybcm.config import BCMConfig
import os.path
from lxml import etree
from lxml.html.clean import Cleaner
from bs4 import BeautifulSoup as Soup
import logging

logger = logging.getLogger('pybcm.test.TestElementReader')

class TestElementReader(unittest.TestCase):

    _element_filename = "Sampledata/BrickLink Price Guide - Part 3004 in Light Bluish Gray Color.htm"
    _reader = ElementFileReader(VendorMap())


    @classmethod
    def loadTree(cls, element_filename):
        log = logging.getLogger("TestElementReader.loadTree")
        ElementFileReader.read_tree_from_file(element_filename)
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
        # logger = logging.getLogger('pybcm.test.TestElementReader')
        logging.basicConfig(level=logging.DEBUG)
        logger.debug("Test in TestElementREader.setUpClass")
        cls._config = BCMConfig('config/bcm.ini')
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


    def testElementFileReaderMethods(self):
        log = logging.getLogger("TestElementFileReader")
        element_filename = "Sampledata/BrickLink Price Guide - Part 3004 in Light Bluish Gray Color.htm"
        self.assertTrue(os.path.isfile(element_filename))

        store_list = self._reader.read_store_list(element_filename)
        logger.debug(store_list)


