import logging
import unittest

from log import setup_custom_logger
from pybcm.vendors import *

#logger = setup_custom_logger(__name__)
logger = logging.getLogger(__name__)


class TestVendors(unittest.TestCase):
    def setUp(self):
        pass

    def testVendorMap(self):
        logging.getLogger(''.join([__name__, ".testVendorMap"]))
        vmap = VendorMap()
        vmap['341396'] = 'The Brick Diet'
        vmap['443396'] = 'The Brick Town'
        vmap['543196'] = 'Bricks a lot for the memories'
        vmap['441676'] = 'Bricks on the Wall'
        vmap['425676'] = 'In the Brick of it'

        self.assertEquals(len(vmap), 5)
        self.assertEquals(vmap['425676'], 'In the Brick of it')
        #self.assertEquals(vmap.xml, str(vmap))  # __str__ should call the xml property

        print(vmap.json)
