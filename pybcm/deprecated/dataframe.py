# Copyright (c) 2017, Keith Hooks
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import logging

import pandas as pd
from pandas.testing import assert_frame_equal

# pandas.DataFrame has functionality added to it via monkeypatching. pandas.DataFrame should not be imported directly
# in the codebase. Import pybcm.dataframe instead.

logger = logging.getLogger("pybcm.{}".format(__name__))

WANTED_INDEX = ['item', 'color']
WANTED_COLUMNS = None # TODO: define these
PRICEGUIDE_INDEX = ['item', 'color', 'new_or_used']
PRICEGUIDE_COLUMNS = ['avg_price', 'max_price', 'min_price', 'qty_avg_price',
                      'total_quantity', 'unit_quantity', 'currency_code']


def monkeypatch_method(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func
    return decorator


@monkeypatch_method(pd.DataFrame)
def indexed_df(self, idx=None):
    if idx is None:
        idx = ['item', 'color', 'new_or_used']
    dfa = self.set_index(idx)
    a = dfa.remove_duplicates_by_index()
    return a


@monkeypatch_method(pd.DataFrame)
def to_tuplelist(self):
    """Converts the rows of DataFrame df to a list of tuples"""
    df = self.reset_index()
    df = df.drop('index', axis=1)
    values = df.values
    return list(map(tuple, values))


@monkeypatch_method(pd.DataFrame)
def not_in_dfb(self, dfb, idx=None):
    """ Returns the rows of DataFrame dfa that are NOT in DataFrame dfb
        based on the index idx. dfa and dfb should be flat dataframes
    """
    if idx is None:
        idx = ['item', 'color']
    a = self.indexed_df(idx)
    b = dfb.indexed_df(idx)
    common_i = a.index.isin(b.index)
    a = a[~common_i]
    return a.reset_index()


@monkeypatch_method(pd.DataFrame)
def in_dfb(self, dfb, idx=None):
    """ Returns the rows of DataFrame dfa that are in DataFrame dfb
        based on index idx
    """
    if idx is None:
        idx = ['item', 'color', 'new_or_used']
    a = self.indexed_df(idx)
    b = dfb.indexed_df(idx)
    common_i = a.index.isin(b.index)
    a = a[common_i]
    return a.reset_index()


@monkeypatch_method(pd.DataFrame)
def remove_duplicates_by_index(self):
    # remove duplicates and sort
    dfa = self[~self.index.duplicated()]
    dfa = dfa.sort_index()
    return dfa


@monkeypatch_method(pd.DataFrame)
def unique_indices_by_levels(self, levels=[0, 1]):
    idx = [self.index.get_level_values(i).values for i in levels]
    return set(zip(*idx))

"""BCM dataframe helper functions"""
def wanted_df_from_tuplelist(needed):
    """ Converts a list of (itemid, color, qty) tuple values to a dataframe"""
    df = pd.DataFrame(needed, columns=['item', 'color', 'itemtype', 'qty'])
    return df


def want_list_from_rest_inv(inv_):
    # returns list(itemid, color, new_or_used) tuples without new_or_used
    __need_list = [(__item['item']['no'],           # itemid
                    str(__item['color_id']),        # color
                    __item['item']['type'],         # itemtype
                    __item['quantity'])             # wantedqty
                   for __item
                   in [match['entries'][0] for match in inv_]]
    # double the list with both 'N' and 'U'
    # __need_list = [(*item, new_or_used) for item in items_only for new_or_used in ['N', 'U']]
    return __need_list


def assert_frame_not_equal(df1, df2, **kwargs):
    # assert_frame_equal exists, but we need the ability to assert that frames are not equal
    try:
        assert_frame_equal(df1, df2, **kwargs)
        raise AssertionError('DataFrames are equal.')
    except AssertionError:
        pass


if __name__ == '__main__':


    d = {'one': [1., 2., 3., 4.],
         'two': [4., 3., 2., 1.]}

    bc = pd.DataFrame(d, columns=['one', 'two'])
    bc['one']

    print(bc)




