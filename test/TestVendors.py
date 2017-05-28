import unittest
from pybcm.vendors import *
import logging


class TestVendors(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    def testVendorMethods(self):
        log = logging.getLogger("TestVendors.testVendorMethods")
        vendor = Vendor('441396', 'The Brick Diet')
        log.debug(vendor.xml)
        log.debug(vendor)
        log.debug(vendor.__repr__())
        self.assertEquals(vendor.xml, str(vendor))

    def testVendorMap(self):
        log = logging.getLogger("TestVendors.testVendorMap")
        vmap = VendorMap()
        vmap.addVendor(Vendor('341396', 'The Brick Diet'))
        vmap.addVendor(Vendor('443396', 'The Brick Town'))
        vmap.addVendor(Vendor('543196', 'Bricks a lot for the memories'))

        vmap['441676'] = 'Bricks on the Wall'
        vmap['425676'] = 'In the Brick of it'

        self.assertEquals(len(vmap), 5)
        self.assertEquals(vmap['425676'], 'In the Brick of it')
        self.assertEquals(vmap.xml, str(vmap))  # __str__ should call the xml property

        log.info(vmap)
