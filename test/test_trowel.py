import pandas as pd
import pytest

from pybcm.config import BCMConfig
from pybcm.trowel import Trowel


@pytest.fixture(scope="module")
def config():
    _config = BCMConfig('../config/bcm.ini')  # create the settings object and load the file
    return _config

@pytest.fixture(scope="module")
def trowel():
    _trowel = Trowel(config)
    return trowel

@pytest.fixture(scope="session")
def store():
    _store = pd.HDFStore("../data/test.hd5")
    return _store

@pytest.fixture(scope="session")
def price_df():
    df = pd.DataFrame({'item': [1, 1, 2, 2], 'color': ['A', 'B', 'A', 'C'], 'value': [1.2, 1, 2, 4]})


def test_a_thing(store):
    print(store.prices)
