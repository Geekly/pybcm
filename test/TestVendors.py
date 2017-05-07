import unittest
from pybcm.vendors import *
import logging


class TestVendors(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    def testVendorMethods(self):
        log = logging.getLogger("TestVendors.testVendorMethods")
        vendor = Vendor('441396', 'The Brick Diet')
        # log.debug(vendor.xml)
        # log.debug(vendor)
        self.assertEquals(vendor.xml, str(vendor))

    def testVendorMap(self):
        log = logging.getLogger("TestVendors.testVendorMap")
        vmap = VendorMap()

        vendor1 = Vendor('441396', 'The Brick Diet')

        self.assertTrue(vmap.addVendor(vendor1))
        self.assertFalse(vmap.addVendor(vendor1))  # try to add a duplicate vendor

        vmap.addVendor(Vendor('441676', 'Bricks on the Wall'))
        vmap.addVendor(Vendor('425676', 'In the Brick of it'))

        self.assertEquals(vmap.getNumVendors(), 3)
        self.assertEquals(vmap.getVendorName('425676'), 'In the Brick of it')

        self.assertEquals(vmap.xml, str(vmap))  # __str__ should call the xml property

        log.info(vmap)