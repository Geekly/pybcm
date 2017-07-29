import unittest

from pybcm.blrest import *


class TestRest(unittest.TestCase):

    logger = log.setup_custom_logger('pybcm')

    def setUp(self):
        self.rc = RestClient()
        pass

    def test_get_item(self):

        item = self.rc.get_item('3006', 'PART')
        logger.debug("Get part {}". format(item))

    def test_get_known_colors(self):
        colors = self.rc.get_known_colors('3006', 'PART')
        logger.debug("Get colors for part {}: {}".format('3006', colors))

    def test_get_price_guide(self):
        price_guide = self.rc.get_price_guide('3004', 'PART', '86')
        logger.debug("Get price guide: {}".format(price_guide))

    def test_get_subsets(self):
        subsets = self.rc.get_subsets('30300-1', 'SET')
        logger.debug("Gathering subsets {}".format(subsets))

    def test_get_part_price_guide(self):
        itemid, colorid, new_or_used = '3004', '86', 'N'
        guide = self.rc.get_part_price_guide(itemid, colorid, new_or_used)
        logger.debug("Gathering price guide: {}".format(guide))

if __name__ == '__main__':
    unittest.main()
