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

from rest import RestClient
from config import BCMConfig

logger = logging.getLogger("pybcm.{}".format(__name__))

WANTED_INDEX = ['item', 'color']
WANTED_COLUMNS = None # TODO: define these
PRICEGUIDE_INDEX = ['item', 'color', 'new_or_used']
PRICEGUIDE_COLUMNS = ['avg_price', 'max_price', 'min_price', 'qty_avg_price',
                      'total_quantity', 'unit_quantity', 'currency_code']


class BcmDataFrame(pd.DataFrame):
    """
    A pandas composition class that know how to fill itself from the rest api
    and is friendly with tuples and other dataframes

    The dataframe is maintained as flat, but can return a indexed copy(reference?) of itself

    """
    def __init__(self, data):

        if data.size:
            self.df = pd.DataFrame(data)
        else:
            self.df = None

    def not_in_dfb(self):
        pass

    def in_dfb(self):
        pass

class PriceDataFrame(BcmDataFrame):

    def __init__(self, data):
        super(PriceDataFrame, self).__init__(data)
        self.df.columns = PRICEGUIDE_INDEX + PRICEGUIDE_COLUMNS


class WantedDataFrame(BcmDataFrame):

    def __init__(self, data):
        super(WantedDataFrame, self).__init__(data)


def remove_duplicates_by_index(dfa):
    # remove duplicates and sort
    dfa = dfa[~dfa.index.duplicated()]
    dfa = dfa.sort_index()
    return dfa


def tuplelist_as_df(needed, idx=['item', 'color']):
    """ Converts a list of (itemid, color, qty) tuple values to a dataframe"""
    df = pd.DataFrame(needed, columns=['item', 'color', 'itemtype', 'qty'])
    df = df.set_index(idx)
    return df


def dfa_not_in_dfb(dfa, dfb, idx=['item', 'color']):
    """ Returns the rows of DataFrame dfa that are NOT in DataFrame dfb
        based on the index idx. dfa and dfb should be flat dataframes
    """
    a = dfa.set_index(idx)
    b = dfb.set_index(idx)
    common_i = a.index.isin(b.index)
    a = a[~common_i]
    return a.reset_index()


def dfa_in_dfb(dfa, dfb, idx=['item', 'color']):
    """ Returns the rows of DataFrame dfa that are in DataFrame dfb
        based on index idx
    """
    dfb = remove_duplicates_by_index(dfb) # doesn't change dfb externally
    #prices_df = remove_duplicates_by_index(prices_df)
    common_i = dfa.reset_index().set_index(idx).index.isin(dfb.index)
    return dfa[common_i]


def df_to_tuplelist(df):
    """Converts the rows of DataFrame df to a list of tuples"""
    return list(map(tuple, df.reset_index().values))


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


def merge_prices_with_want(want_tuplelist, prices_df):
    prices_df = prices_df.reset_index()
    want_df = pd.DataFrame(want_tuplelist, columns=['item', 'color', 'itemtype', 'wanted_qty'])
    full_df = pd.merge(want_df, prices_df)
    full_df = full_df.set_index(PRICEGUIDE_INDEX)
    return full_df


"""Wrapper for the Rest client that provides results in pandas format"""


class rest_wrapper:
    def __init__(self, config=BCMConfig('../config/bcm.ini')):
        self.rc = RestClient()
        self.config = config

    def get_item(self, itemid, itemtypeid):
        raise NotImplemented

    def get_supersets(self, itemid):
        raise NotImplemented

    def get_subsets(self, itemid, itemtypeid):
        raise NotImplemented

    def get_priceguide_df(self, itemid, itemtypeid, colorid, guide_type='sold'):
        """
        :param itemid:
        :param itemtypeid:
        :param colorid:
        :param guide_type:
        :return:

        get_priceguide_df returns a dictionary of the following format:

        typ = {
            "item": {
                "no": "7644-1",
                "type": "SET"
            },
            "new_or_used": "N",
            "currency_code": "USD",
            "min_price": "96.0440",
            "max_price": "695.9884",
            "avg_price": "162.3401",
            "qty_avg_price": "155.3686",
            "unit_quantity": 298,
            "total_quantity": 359,
            "price_detail": [

            ]
        }
        For sale ('stock'):
        {
            "quantity":2,
            "qunatity":2,
            "unit_price":"96.0440",
            "shipping_available":true
        }
        Previously sold ('sold'):
        {
            "quantity":1,
            "unit_price":"98.2618",
            "seller_country_code":"CZ",
            "buyer_country_code":"HK",
            "date_ordered":"2013-12-30T14:59:01.850Z"
        }

        """
        pg_new = self.rc.get_price_guide(itemid, itemtypeid, colorid, 'N', guide_type)
        pg_used = self.rc.get_price_guide(itemid, itemtypeid, colorid, 'U', guide_type)
        if pg_new is None or pg_used is None:
            raise ValueError("Problem retrieiving {}: {}".format(itemid, colorid))
        pg_json = (pg_new, pg_used)
        pg = make_priceguide_pandas_from_json(pg_json, colorid)
        return pg

    def get_part_price_guide_df(self, itemid, colorid):
        pg = self.get_priceguide_df(itemid, 'PART', colorid)
        return pg

    def get_known_colors(self, itemid, itemtypeid):
        colors = self.rc.get_known_colors(itemid, itemtypeid)
        df = pd.DataFrame.from_dict(colors, orient="columns").set_index(['color_id'])
        return df


def make_priceguide_pandas_from_json(dict_tuple, color, sold_or_stock='sold'):
    """ Build a DataFrame of the priceguide for a single part(item + color). Color is
        required since color is not contained in the priceguide information
        dict_tuple = ({new_prices}, {used_prices}) where {_prices} look like:

        {
          "item": {
            "no": "3006",
            "type": "PART"
          },
          "new_or_used": "N",
          "currency_code": "USD",
          "min_price": "0.0525",
          "max_price": "3.4290",
          "avg_price": "0.5332",
          "qty_avg_price": "0.3653",
          "unit_quantity": 978,
          "total_quantity": 14810,
          "price_detail": [
            {
              "quantity": 1,
              "unit_price": "0.6384",
              "seller_country_code": "US",
              "buyer_country_code": "US",
              "date_ordered": "2017-02-16T23:58:22.797Z",
              "qunatity": 1
            },
            {
              "quantity": 1,
              "unit_price": "0.5925",
              "seller_country_code": "US",
              "buyer_country_code": "US",
              "date_ordered": "2017-02-18T05:42:10.397Z",
              "qunatity": 1
            }
          ]
        }
    """
    # top_fields = ['item', 'new_or_used', 'avg_price', 'max_price', 'min_price',
    #              'qty_avg_price', 'total_quantity', 'unit_quantity', 'currency_code', 'price_detail']

    numeric_fields = ['avg_price', 'max_price', 'min_price', 'qty_avg_price', 'total_quantity', 'unit_quantity']
    summary_pull_fields = ['new_or_used', 'currency_code'] + numeric_fields

    df_columns = ['item', 'color'] + summary_pull_fields

    common_values = {'item': dict_tuple[0]['item']['no'],
                     'color': color}

    summary = [{key: dict_tuple[idx][key] for key in summary_pull_fields} for idx in (0, 1)]
    for item in summary:
        item.update({**common_values})

    summary_df = pd.DataFrame( summary, columns=df_columns)
    summary_df[numeric_fields] = summary_df[numeric_fields].apply(pd.to_numeric)

    # TODO: for now, ignoring sold and stock and just using the common fields

    return summary_df


if __name__ == 'main':
    pass

