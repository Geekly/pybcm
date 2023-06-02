import logging

import pytest

from pybcm.const import GuideType, NewUsed
from pybcm.config import BCMConfig
from pybcm.rest import RestClient, build_uri_template

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logging.getLogger('oauthlib.oauth1').setLevel(logging.WARNING)
logging.getLogger('requests_oauthlib').setLevel(logging.WARNING)
#logging.getLogger('urllib3').setLevel(logging.WARNING)


@pytest.fixture(scope="module")
def rc():
    _rc = RestClient(config=BCMConfig(r'../config/bcm.ini'))
    return _rc


def test_get(rc):
    url = r'https://api.bricklink.com/api/store/v1/items/PART/3004'
    resp = rc._get(url)
    logger.info(resp)


def test_get_data(rc):
    url = r'https://api.bricklink.com/api/store/v1/items/PART/3004'
    data = rc._get_data(url)
    logger.info(data)


def test_get_item(rc):
    item = rc.get_item('3006', 'PART')
    item = rc.get_item('3006', 'PART')
    logger.info("Get part {}".format(item))


def test_get_image(rc):
    response = rc.get_item_image('3006', 'PART', 86)
    logger.info(response)


def test_get_known_colors(rc):
    colors = rc.get_known_colors('3006', 'PART')
    logger.info("Get colors for part {}: {}".format('3006', colors))


def test_get_price_guide(rc):
    price_guide = rc.get_price_guide('3006', 'PART', '10', new_or_used=NewUsed.N, guide_type=GuideType.sold)
    # check if New and Sold:
    assert 'date_ordered' in price_guide['price_detail'][0]
    assert price_guide['new_or_used'] == 'N'

    # check if Used and Stock
    price_guide = rc.get_price_guide('3006', 'PART', '10', new_or_used=NewUsed.U, guide_type=GuideType.stock)
    assert 'shipping_available' in price_guide['price_detail'][0]
    assert price_guide['new_or_used'] == 'U'

    logger.info("Get price guide: {}".format(price_guide))


def test_get_subsets(rc):
    subsets = rc.get_subsets('10808-1', 'SET')
    logger.info("Gathering subsets {}".format(subsets))


def test_get_supersets(rc):
    pass


def test_get_part_price_guide(rc):
    itemid, colorid, new_or_used = '3004', '86', 'N'
    guide = rc.get_part_price_guide(itemid, colorid, new_or_used)
    logger.info("Gathering price guide: {}".format(guide))


def test_build_uri_template():
    key = 'get_item'
    template = build_uri_template(key)
    assert template.uri == 'https://api.bricklink.com/api/store/v1/items/{type}/{no}'
    url = template.expand(type='PART', no='3004')
    assert url == 'https://api.bricklink.com/api/store/v1/items/PART/3004'
    logger.info(template)
    logger.info(url)


def test_get_color_list(rc):
    color_list = rc.get_all_colors()
    logger.info(color_list)


def test_get_category_list(rc):
    cat_list = rc.get_category_list()
    logger.info(cat_list)