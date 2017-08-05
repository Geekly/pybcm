# Copyright (c) 2012-2017, Keith Hooks
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

"""
    Manage bricklink data through the pandas wrapper api

"""
import logging
import log
import pandas as pd
from pandas import HDFStore
from bc_rest import RestClient
# from db import *
from blrest_wrapper import rest_wrapper

logger = logging.getLogger(__name__)


# Dataframe helper functions

def tuplelist_as_df(needed):
    """ Converts a list of (itemid, color, qty) tuple values to a dataframe"""
    df = pd.DataFrame(needed, columns=['item', 'color', 'itemtype', 'qty'])
    df = df.set_index(['item', 'color'])
    return df


def df_not_in_prices_df(dfa, prices_df):
    """ Returns the elements of DataFrame dfa that are NOT in DataFrame dfb
        DataFrames have index = ['item', 'color']
    """

    common_i = dfa.index.isin(prices_df.reset_index().set_index(['item', 'color']).index)
    return dfa[~common_i]


def prices_in_df(prices_df, dfb):
    """ Returns the rows of DataFrame dfa that are in DataFrame dfb
        DataFrames have index = ['item', 'color']
    """
    common_i = prices_df.reset_index().set_index(['item', 'color']).index.isin(dfb.index)
    return prices_df[common_i]


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
    full_df = full_df.set_index(PRICE_INDEX)
    return full_df

PRICE_INDEX = ['item', 'color', 'new_or_used']


class Trowel:

    """ interacts with the HDFStore, and clients """

    def __init__(self, config):
        self.config = config
        self.rc = RestClient()
        self.pc = rest_wrapper()
        pd.set_option('io.hdf.default_format', 'table')
        self.store = HDFStore("../data/pybcm.hd5")

    def summary(self):
        raise NotImplemented

    # create a wanted list from a set
    def get_set_inv(self, lego_set_id):
        inv = self.rc.get_subsets(lego_set_id, 'SET')
        return inv

    def get_item_prices_df(self, itemid, itemtypeid, color):
        pg = self.pc.get_price_guide_df(itemid, itemtypeid, color, 'N', guide_type='sold')
        return pg

    def get_inv_prices(self, inv):
        """ build a dataframe for the passed Rest inventory

            inv is a list of {'match_no': 0, 'entries': [{'item': {'no': '2540',
                                              'name': 'Plate, Modified 1 x 2 with Handle on Side - Free Ends',
                                              'type': 'PART', 'category_id': 27}, 'color_id': 11, 'quantity': 2,
                                     'extra_quantity': 0, 'is_alternate': False, 'is_counterpart': False}]}
        """
        # TODO: Account for subsititutions and find the cheapest of substitutions

        price_df = pd.DataFrame()

        # {'item': {'no': '3020', 'name': 'Plate 2 x 4', 'type': 'PART', 'category_id': 26}, 'color_id': 11,
        # 'quantity': 2, 'extra_quantity': 0, 'is_alternate': False, 'is_counterpart': False}
        # extract list of (itemid, color, new_or_used) tuples from need_elements

        needed = want_list_from_rest_inv(inv)

        # load existing prices from the db and download the rest

        pull_list, price_df = self.prune_pull_list(needed)
        # download the list of items in pull_list and build the pandas dataframe
        for item in pull_list:  # iterate over list of matches

            # create a pull list of
            # TODO: Check if price already exists in DB and is not older than a particular date before reloading it

            itemid, color, itemtypeid, wanted_qty = item
            # get the dataframe of the price summary
            prices = self.get_item_prices_df(itemid, itemtypeid, color)
            if prices is not None:
                prices['wanted_qty'] = item[3]
                # wanted_avg = prices['wanted_qty'] * prices['avg_price']
                price_df = price_df.append(prices)
                pass
            else:
                raise ValueError
            logger.debug(
                "Item: {}, Color: {}, Qty: {}, Avg Price: {}".format(itemid, color, wanted_qty, prices['avg_price'][0]))

        # add the new prices to the save
        # combine all of the prices and return them

        # merge the wanted list before returning
        price_df = merge_prices_with_want(needed, price_df)
        return price_df

    def add_prices_to_store(self, prices):
        with self.store as store:
            store.open()
            orig_rows = store.prices.shape[0]
            merged = store.prices.append(prices.reset_index())
            merged = merged.set_index(PRICE_INDEX)
            merged = merged[~merged.index.duplicated(keep='last')]
            merged = merged.reset_index()
            new_rows = merged.shape[0]
            store.prices = merged
            logger.info("Added {} rows to store.prices".format(new_rows - orig_rows))

    @classmethod
    def estimate_inv_cost(cls, prices):
        est_cost = dict({"N": 0.0, "U": 0.0})
        p = prices.reset_index()
        p['wanted_avg'] = p['wanted_qty'] * p['avg_price']
        est_cost['N'] = p[p['new_or_used'] == 'N']['wanted_avg'].sum()
        est_cost['U'] = p[p['new_or_used'] == 'U']['wanted_avg'].sum()
        return est_cost

    def prune_pull_list(self, needed):
        with self.store as store:
            store.open()
            all_prices_df = store['prices'].set_index(PRICE_INDEX)
            needed_df = tuplelist_as_df(needed)

            pull_df = df_not_in_prices_df(needed_df, all_prices_df)
            pull_list = df_to_tuplelist(pull_df)
            already_known_prices_df = prices_in_df(all_prices_df, needed_df)

            return pull_list, already_known_prices_df



if __name__ == "__main__":
    logger = log.setup_custom_logger('pybcm')

    from pprint import pprint

    tr = Trowel()
    inv = tr.get_set_inv('10030-1')
    pprint(tr.get_inv_prices(inv))

    # price out a set by collecting avg prices from wanted list

    # list substitutes in a wanted list
