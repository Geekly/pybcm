import pytest

import log
from pybcm.config import BCMConfig
from pybcm.rest import RestClient, build_uri_template

logger = log.setup_custom_logger("test.pybcm.{}".format(__name__))


@pytest.fixture(scope="module")
def rc():
    _rc = RestClient(config=BCMConfig(r'../config/bcm.ini'))
    return _rc


def test_get(rc):
    url = r'https://api.bricklink.com/api/store/v1/items/PART/3004'
    resp = rc.get(url)
    logger.info(resp)


def test_get_data(rc):
    url = r'https://api.bricklink.com/api/store/v1/items/PART/3004'
    data = rc.get_data(url)
    logger.info(data)


def test_get_item(rc):
    item = rc.get_item('3006', 'PART')
    logger.debug("Get part {}".format(item))


def test_get_image(rc):
    response = rc.get_item_image('3006', 'PART', 86)
    logger.info(response)


def test_get_known_colors(rc):
    colors = rc.get_known_colors('3006', 'PART')
    logger.debug("Get colors for part {}: {}".format('3006', colors))


def test_get_price_guide(rc):
    price_guide = rc.get_price_guide('3004', 'PART', '86')
    logger.debug("Get price guide: {}".format(price_guide))


def test_get_subsets(rc):
    subsets = rc.get_subsets('10808-1', 'SET')
    logger.debug("Gathering subsets {}".format(subsets))


def test_get_supersets(rc):
    pass


def test_get_part_price_guide(rc):
    itemid, colorid, new_or_used = '3004', '86', 'N'
    guide = rc.get_part_price_guide(itemid, colorid, new_or_used)
    logger.debug("Gathering price guide: {}".format(guide))


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