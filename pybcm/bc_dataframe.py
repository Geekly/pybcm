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

from bc_rest import RestClient
from config import BCMConfig

logger = logging.getLogger("pybcm.{}".format(__name__))

PRICEGUIDE_INDEX = ['item', 'color', 'new_or_used']
PRICEGUIDE_COLUMNS = ['avg_price', 'max_price', 'min_price', 'qty_avg_price',
                      'total_quantity', 'unit_quantity', 'currency_code']


class BcmDataFrame:
    """
    A pandas composition class that know how to fill itself from the rest api
    and is friendly with tuples and other dataframes
    """
    def __init__(self, data):

        if data:
            self.df = pd.DataFrame(data)
        else:
            self.df = None


class PriceDataFrame(BcmDataFrame):

    def __init__(self, data):
        super.__init__(data)


class WantedDataFrame(BcmDataFrame):

    def __init__(self, data):
        super.__init__(data)


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
        based on the index idx
    """
    a = dfa.reset_index(drop=True).set_index(idx)
    b = dfb.reset_index(drop=True).set_index(idx)
    common_i = a.index.isin(b.index)
    a = a[~common_i]
    return a.reset_index()


def dfa_in_dfb(dfa, dfb, idx=['item', 'color']):
    """ Returns the rows of DataFrame dfa that are in DataFrame dfb
        based on index idx
    """
    dfb = remove_duplicates_by_index(dfb)
    #prices_df = remove_duplicates_by_index(prices_df)
    common_i = dfa.reset_index(drop=True).set_index(idx).index.isin(dfb.index)
    return dfa[common_i]


def df_to_tuplelist(df):
    """Converts the rows of DataFrame df to a list of tuples"""
    return list(map(tuple, df.reset_index(drop=True).values))


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
    prices_df = prices_df.reset_index(drop=True)
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
        pg = self.make_pandas_from_json(pg_json, colorid)
        return pg

    def get_part_price_guide_df(self, itemid, colorid, new_or_used='U'):
        pg = self.get_priceguide_df(itemid, 'PART', colorid)
        return pg

    def get_known_colors(self, itemid, itemtypeid):
        raise NotImplemented

    def make_pandas_from_json(self, dict_tuple, color):
        #TODO: improve this garbage function and use the CONST PRICEGUIDE_COLUMNS
        item_fields = ['no', 'color', 'type']
        numeric_fields = ['avg_price', 'max_price', 'min_price', 'qty_avg_price', 'total_quantity', 'unit_quantity']
        summary_pull_fields = ['new_or_used', 'avg_price', 'max_price', 'min_price',
                               'qty_avg_price', 'total_quantity', 'unit_quantity', 'currency_code']
        all_summary_fields = ['item', 'color'] + summary_pull_fields
        stock_detail_fields = ['quantity', 'unit_price', 'shipping_available']
        sold_detail_fields = ['quantity', 'unit_price', 'seller_country_code', 'buyer_country_code', 'date_ordered']
        common_detail_fields = list(set(stock_detail_fields) & set(sold_detail_fields))
        summary_common = {'item': dict_tuple[0]['item']['no'],
                   'color': color}
        summary_new = {key: dict_tuple[0][key] for key in summary_pull_fields}
        summary_new.update({**summary_common, **summary_new, 'new_or_used': 'N'})
        summary_used = {key: dict_tuple[1][key] for key in summary_pull_fields}
        summary_used.update({**summary_common, **summary_used, 'new_or_used': 'U'})
        summary = [summary_new, summary_used]
        summary_df = pd.DataFrame(summary, columns=all_summary_fields)
        summary_df[numeric_fields] = summary_df[numeric_fields].apply(pd.to_numeric)

        # make the price details dataframe
        # TODO: for now, ignoring sold and stock and just using the common fields

        return summary_df
