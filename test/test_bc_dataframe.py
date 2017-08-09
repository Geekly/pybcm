import pandas as pd
import pytest
from pandas import HDFStore

import log
from pybcm.bc_dataframe import *

logger = log.setup_custom_logger("test.pybcm.{}".format(__name__))


@pytest.fixture(scope="module")
def simple_df():
    store = HDFStore('../resources/data/test.hd5')
    df = store.prices
    return df


@pytest.fixture(scope="function")
def flat_pg_df():
    df = pd.read_csv('fixtures/priceguide.csv')
    return df

@pytest.fixture(scope="function")
def indexed_pg_df():
    df = pd.read_csv('fixtures/priceguide.csv')
    df = df.set_index(PRICEGUIDE_INDEX)
    return df


@pytest.fixture(scope="function")
def dfA():
    dfA = pd.DataFrame({'item': [1, 1, 2, 2], 'color': ['A', 'B', 'C', 'D'], 'value': [1.2, 1, 2, 4]},
                       columns=['item', 'color', 'value'])
    dfA = dfA.reset_index(drop=True)
    return dfA


@pytest.fixture(scope="function")
def dfB():
    dfB = pd.DataFrame({'item': [2, 2, 3, 3], 'color': ['C', 'D', 'F', 'G'], 'value': [2, 4, 8, 9]},
                       columns=['item', 'color', 'value'])
    dfB = dfB.reset_index(drop=True)
    return dfB


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


def test_df_not_in_prices_df(dfA, dfB):
    not_in_it = dfa_not_in_dfb(dfA, dfB, idx=['item', 'color'])
    print(not_in_it)
    pd.testing.assert_frame_equal(not_in_it, dfA.iloc[[0, 1]])