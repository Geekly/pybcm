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
    _store = pd.HDFStore("./resources/test.hd5")
    return _store

@pytest.fixture(scope="session")
def price_df():
    df = pd.DataFrame({'item': [1, 1, 2, 2], 'color': ['A', 'B', 'A', 'C'], 'value': [1.2, 1, 2, 4]})


def test_a_thing(store):
    print(store.prices)


def test_summary():
    pass


def test_get_set_inv():
    pass


def test_get_item_prices_df():
    pass


def test_get_inv_prices():
    pass


def test_add_prices_to_store():
    pass


def test_estimate_inv_cost():
    pass


def test_prune_pull_list():
    pass