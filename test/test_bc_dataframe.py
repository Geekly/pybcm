import pandas as pd
import pytest
from pandas import HDFStore

import log
from pybcm.dataframe import *

logger = log.setup_custom_logger("test.pybcm.{}".format(__name__))


@pytest.fixture(scope="module")
def simple_df():
    store = HDFStore('./resources/test.hd5')
    df = store.prices
    return df


@pytest.fixture(scope="function")
def flat_pg_df():
    df = pd.read_csv('./resources/priceguide.csv')
    return df

@pytest.fixture(scope="function")
def indexed_pg_df():
    df = pd.read_csv('./resources/priceguide.csv')
    df = df.set_index(PRICEGUIDE_INDEX)
    return df


@pytest.fixture(scope="function")
def price_array():
    df = pd.read_csv('./resources/priceguide.csv')
    return df.values


@pytest.fixture(scope="function")
def dfa():
    _dfa = pd.DataFrame({'item': [1, 1, 2, 2], 'color': ['A', 'B', 'C', 'D'], 'value': [1.5, 7, 2., 4.]},
                        columns=['item', 'color', 'value'])
    _dfa = _dfa.reset_index(drop=True)
    return _dfa


@pytest.fixture(scope="function")
def dfa_indexed(dfa):
    _dfa = dfa.set_index(['item', 'color'])
    return _dfa


@pytest.fixture(scope="function")
def dfb():
    _dfb = pd.DataFrame({'item': [2, 2, 3, 3], 'color': ['C', 'D', 'F', 'G'], 'value': [2., 4., 8., 9.]},
                       columns=['item', 'color', 'value'])
    _dfb = _dfb.reset_index(drop=True)
    return _dfb


@pytest.fixture(scope="function")
def dfb_indexed(dfb):
    _dfb = dfb.set_index(['item', 'color'])
    return _dfb


@pytest.fixture(scope="function")
def pdf(price_array):
    _pdf = PriceDataFrame(price_array)
    _pdf.df = _pdf.df.set_index(['item', 'color'])
    return _pdf


def test_tuple_as_df():
    test_tuple = [('4003', '86', 'PART', 42), ('4003', '10', 'PART', 12)]
    df = tuplelist_as_df(test_tuple)
    assert isinstance(df, pd.DataFrame)
    return df


def test_remove_duplicates_by_index(indexed_pg_df):
    assert isinstance(indexed_pg_df, pd.DataFrame)
    A = indexed_pg_df
    B = remove_duplicates_by_index(A)
    assert isinstance(B, pd.DataFrame)
    assert not A.shape == B.shape
    print(B)


def test_remove_duplicates_from_PriceGuideDf(pdf):
    assert isinstance(pdf, PriceDataFrame)
    A = pdf.df
    B = remove_duplicates_by_index(A)
    assert isinstance(B, pd.DataFrame)
    assert not A.shape == B.shape
    print(B)


def test_df_not_in_prices_df(dfa, dfb):
    not_in_it = dfa_not_in_dfb(dfa, dfb, idx=['item', 'color'])
    print(not_in_it)
    pd.testing.assert_frame_equal(not_in_it, dfa.iloc[[0, 1]])


def test_PriceDataFrame_init(price_array):
    _pdf = PriceDataFrame(price_array)
    print(_pdf.df)


def test_dfa_in_dfb(dfa, dfb):
    assert True
    pass


def test_df_to_tuplelist(dfa):
    assert True
    pass


def test_want_list_from_rest_inv(inv):
    assert True


def test_merge_prices_with_want(price_df, want_list):
    assert True


def test_fixtures(dfa, dfb, dfa_indexed, dfb_indexed):
    print(dfa)
    print(dfb)
    print(dfa_indexed)
    print(dfb_indexed)