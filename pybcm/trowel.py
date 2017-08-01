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
    Manage bricklink data using the rest api

"""
import pandas as pd
from pandas import HDFStore

from blrest import RestClient
from db import *
from pandas_wrapper import PandasClient

logger = logging.getLogger('pybcm.trowel')


class Trowel:
    def __init__(self, config):
        self.config = config
        self.rc = RestClient()
        self.pc = PandasClient()
        self.store = HDFStore("../data/pybcm.hd5")

    # create a wanted list from a set
    def get_set_inv(self, lego_set_id):
        inv = self.rc.get_subsets(lego_set_id, 'SET')
        return inv

    def get_part_prices_df(self, itemid, color):
        pg = self.pc.get_price_guide_df(itemid, 'PART', color, 'N', guide_type='sold')
        return pg

    def price_inv(self, inv):
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

        def needed_items(__inv):
            # returns list(itemid, color, new_or_used) tuples without new_or_used
            __need_list = [(__item['item']['no'], str(__item['color_id']), __item['quantity']) for __item \
                           in [match['entries'][0] for match in __inv]]
            # double the list with both 'N' and 'U'
            # __need_list = [(*item, new_or_used) for item in items_only for new_or_used in ['N', 'U']]
            return __need_list

        needed = needed_items(inv)

        # load existing prices from the db and download the rest

        pull_list, known_prices = self.prune_pull_list(needed)
        # download the list of items in pull_list and build the pandas dataframe
        for item in pull_list:  # iterate over list of matches

            # create a pull list of
            # TODO: Check if price already exists in DB and is not older than a particular date before reloading it

            itemid, color, wanted_qty = item
            # get the dataframe of the price summary
            prices = self.get_part_prices_df(itemid, color)
            if prices is not None:
                prices['wanted_qty'] = item[2]
                # wanted_avg = prices['wanted_qty'] * prices['avg_price']
                price_df = price_df.append(prices)
                pass
            else:
                raise ValueError
            logger.debug(
                "Item: {}, Color: {}, Qty: {}, Avg Price: {}".format(itemid, color, wanted_qty, prices['avg_price'][0]))

        # add the new prices to the save
        # combine all of the prices and return them

        return price_df

    @staticmethod
    def estimate_inv_cost(p):
        est_cost = dict({"N": 0.0, "U": 0.0})
        p['wanted_avg'] = p['wanted_qty']*p['avg_price']
        est_cost['N'] = p[p['new_or_used'] == 'N']['wanted_avg'].sum()
        est_cost['U'] = p[p['new_or_used'] == 'U']['wanted_avg'].sum()
        return est_cost

    def prune_pull_list(self, needed):
        # TODO: implement some culling by comparing against what's already serialized or in memory
        needed_set = set([(a, b) for a, b, _ in needed])
        existing_prices = self.store['prices']
        existing_set = set(map(tuple, existing_prices[['item', 'color']].values))
        pull_set = needed_set - existing_set
        known_prices_df = existing_prices.reset_index()
        known_prices_df = known_prices_df.set_index(['item', 'color'])
        known_prices_df = known_prices_df[ known_prices_df.index.isin(needed_set)]
        return list(pull_set), known_prices_df


if __name__ == "__main__":
    logger = log.setup_custom_logger('pybcm')

    from pprint import pprint

    tr = Trowel()
    inv = tr.get_set_inv('10030-1')
    pprint(tr.price_inv(inv))

    # price out a set by collecting avg prices from wanted list

    # list substitutes in a wanted list
