import numpy as np
import pytest
from pandas import HDFStore

import log
from pybcm.dataframe import *

#from pybcm.dataframe import bcm_from_tuplelist, PRICEGUIDE_INDEX

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
    bdf = pd.read_csv('./resources/priceguide.csv')
    bdf = bdf.set_index(PRICEGUIDE_INDEX)
    assert isinstance(bdf, pd.DataFrame)
    return bdf

@pytest.fixture(scope="module")
def price_array():
    pa = np.loadtxt('./resources/priceguide.csv')
    return pa

@pytest.fixture(scope="function")
def price_df():
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

#
# @pytest.fixture(scope="function")
# def pdf(price_df):
#     _pdf = PriceDataFrame()
#     _pdf.df = price_df.set_index(['item', 'color'])
#     return _pdf


def test_tuple_as_df():
    test_tuple = [('4003', '86', 'PART', 42), ('4003', '10', 'PART', 12)]
    df = bcm_from_tuplelist(test_tuple)
    assert isinstance(df, pd.DataFrame)
    return df


def test_remove_duplicates_by_index(indexed_pg_df):
    assert isinstance(indexed_pg_df, pd.DataFrame)
    A = indexed_pg_df
    B = A.remove_duplicates_by_index()
    assert isinstance(B, pd.DataFrame)
    assert not A.shape == B.shape
    print(B)


# def test_remove_duplicates_from_PriceGuideDf(pdf):
#     assert isinstance(pdf, PriceDataFrame)
#     A = pdf.df
#     B = remove_duplicates_by_index(A)
#     assert isinstance(B, pd.DataFrame)
#     assert not A.shape == B.shape
#     print(B)


def test_df_not_in_dfb(dfa, dfb):
    not_in_it = dfa.not_in_dfb(dfb, idx=['item', 'color'])
    a = not_in_it
    b = dfa.iloc[[0, 1]]
    print(not_in_it, dfa.iloc[[0, 1]])
    np.testing.assert_array_equal(a.values, b.values)


def test_df_in_dfb(dfa, dfb):
    in_it = dfa.in_dfb(dfb, idx=['item', 'color'])
    a = in_it
    b = dfa.iloc[[2, 3]]
    print(a)
    print(b)
    np.testing.assert_array_equal(a.values, b.values)


# def test_want_list_from_rest_inv(inv):
#     assert True


# def test_merge_prices_with_want(price_df, want_list):
#     assert True


def test_fixtures(dfa, dfb, dfa_indexed, dfb_indexed):
    print(dfa)
    print(dfb)
    print(dfa_indexed)
    print(dfb_indexed)