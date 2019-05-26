import numpy as np
# import pandas as pd
import pytest

from deprecated import log
# from pybcm.dataframe import *
from pybcm.config import BCMConfig
from pybcm.trowel import Trowel

#TODO: many of these methods still need to be completed


logger = log.setup_custom_logger("test.pybcm.{}".format(__name__))

@pytest.fixture(scope="module")
def config():
    _config = BCMConfig('../config/bcm.ini')  # create the settings object and load the file
    return _config

@pytest.fixture(scope="session")
def test_store():
    _store = pd.HDFStore("./resources/test.hd5")
    return _store

@pytest.fixture(scope="module")
def trowel():
    _trowel = Trowel(config)
    return _trowel

@pytest.fixture(scope="session")
def price_df():
    df = pd.DataFrame([['3008', '11', 'N', 1.25, .25, 5],
                       ['3008', '11', 'U', .99, .75, 5],
                       ['3008', '10', 'N', .74, .35, 13],
                       ['3008', '10', 'U', .55, .24, 13],
                       ['3008', '86', 'N', .45, .22, 7],
                       ['3008', '87', 'U', .33, .3, 4]],
                      columns=['item', 'color', 'new_or_used', 'avg_price', 'min_price', 'wanted_qty'])
    return df


# def test_add_prices_to_store_stuff(trowel, test_store):
#     trowel.store = test_store
#     p = test_store.prices
#     p.drop(p.index, inplace=True)
#     adding = test_store.prices.df_btm
#     trowel.add_prices_to_store(adding)
#     print(test_store.prices)


def test_best_prices(trowel, price_df):
    result = (trowel.best_prices(price_df)).sort_values(by=['item', 'color', 'new_or_used'])
    expected_result = price_df.iloc[[3, 1, 4, 5]]
    np.testing.assert_array_equal(result.values, expected_result.values)


def test_estimate_inv_cost(trowel, price_df):
    best = trowel.best_prices(price_df)
    print(best)


def test_summary():
    pass


def test_get_set_inv(trowel):
    inv = trowel.get_set_inv('10808 - 1')
    logger.info(inv)
    pass


def test_get_item_prices_df(trowel):
    pg = trowel.get_item_prices_df('3008', 'PART', '11', guide_type='sold')
    print(pg)
    pass


def test_get_inv_prices():
    pass


def test_add_prices_to_store():
    pass


def test_estimate_inv_cost():
    pass


def test_prune_pull_list():
    pass