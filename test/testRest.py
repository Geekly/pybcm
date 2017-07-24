import unittest

from pybcm.rest import *


class TestRest(unittest.TestCase):

    logger = log.setup_custom_logger('pybcm')

    def setUp(self):
        self.rc = RestClient()
        pass

    def test_get_item(self):
        item = self.rc.get_item('3006', 'PART')
        logger.debug(item)

    def test_get_known_colors(self):
        colors = self.rc.get_known_colors('3006', 'PART')
        logger.debug(colors)

    def test_get_price_guide(self):
        price_guide = self.rc.get_price_guide('3004', 'PART', '86')
        logger.debug(price_guide)

    def test_get_subsets(self):
        subsets = self.rc.get_subsets('30300-1', 'SET')
        logger.debug(subsets)

if __name__ == '__main__':
    unittest.main()
