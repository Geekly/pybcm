import sys
import unittest
from pybcm.elementreader import *
from pybcm.vendors import *
from pybcm.bcmconfig import BCMConfig
import os.path
from lxml import etree
from lxml.html.clean import Cleaner
from bs4 import BeautifulSoup as Soup
import logging


class TestElementReader(unittest.TestCase):

    @classmethod
    def clean(cls, text):
        """

        :type text: cleaned html
        """
        log = logging.getLogger("TestElementReader")

        try:
            cleaner_ = Cleaner(scripts=True, embedded=True, meta=True, style=True, comments=True)
                              # remove_tags=['a', 'li', 'td'])

            clean_text = cleaner_.clean_html(text)
            log.info(len(clean_text) - len(text))
            return clean_text
        except Exception as e:
            log.debug(e)
            'Error in clean_html'
            print
            sys.exc_info()
            return text

    @classmethod
    def setUpClass(cls):
        cls._config = BCMConfig('config/bcm.ini')
        #logging.basicConfig(stream=sys.stderr)
        logging.getLogger("TestElementReader").setLevel(logging.DEBUG)
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
    def testElementFileReaderMethods(self):

        log = logging.getLogger("TestElementReader")
        reader = ElementFileReader(VendorMap())
        element_filename = "Sampledata/BrickLink Price Guide - Part 3004 in Light Bluish Gray Color.htm"
        self.assertTrue(os.path.isfile(element_filename))
        with io.open(element_filename, 'rt') as f:
            soup = Soup(f, 'lxml')
        with io.open("outfile.html", 'w') as g:
            g.write(str(soup))

        cleaner_ = Cleaner(scripts=True, embedded=True, meta=True, style=True, comments=True)
                              # remove_tags=['a', 'li', 'td'])

        soup_text = str(soup)

        clean_text = cleaner_.clean_html(soup_text)
        log.debug(clean_text)
#     log.info("Characters removed" + str(len(clean_text) - len(soup_text)))

#      clean_text = self.clean(str(soup))
#     parser = etree.HTMLParser(encoding='utf-8')  #  remove_blank_text=True, remove_comments=True, encoding='utf-8')
        # with io.open(element_filename, 'r') as f:
        #     filetext = f.read()
        #     # cleantext = self.clean(filetext)
        #
        #     with io.open("outfile.html", 'w') as g:
        #         g.write(cleantext)


        log.info("Parsing item from file...")
# datatree = etree.parse(clean_text, parser)
        #datatree = etree.HTML(f.read(), parser)
        #log.debug(datatree)
        # print( etree.tostring(datatree))

        #item = reader.read_item_from_file(element_filename)
        #print(item)
        pass

