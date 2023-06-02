#import logging

import pytest

import logging
from pybcm.vendors import VendorMap

#logger = log.setup_custom_logger(__name__)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def vmap():
    #logging.getLogger(''.join([__name__, ".testVendorMap"]))
    _vmap = VendorMap()
    _vmap['341396'] = 'The Brick Diet'
    _vmap['443396'] = 'The Brick Town'
    _vmap['543196'] = 'Bricks a lot for the memories'
    _vmap['441676'] = 'Bricks on the Wall'
    _vmap['425676'] = 'In the Brick of it'
    return _vmap


def test_VendorMap(vmap):
    assert len(vmap) == 5
    assert vmap['425676'] == 'In the Brick of it'


def test_xml(vmap):
    logger.info(vmap.xml)


def test_json(vmap):
    logger.info(vmap.json)
