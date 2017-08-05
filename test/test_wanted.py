import pytest

import log
from pybcm.wanted import *

logger = log.setup_custom_logger(__name__)


@pytest.fixture(scope="module")
def wantedDict():
    wanted = WantedDict()
    _wantedlistfilename = "../Sampledata/Remaining Falcon.bsx"
    wanted.read(_wantedlistfilename)
    return wanted


def testProperties(wantedDict):
    assert wantedDict.unique_items == 5
    assert wantedDict.total_items == 36


def testFirst(wantedDict):
    assert True is True


def testGetQty(wantedDict):
    assert wantedDict.get_wanted_qty('3004|2') == 5
