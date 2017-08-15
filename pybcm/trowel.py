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
import log
from dataframe import *


#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("pybcm.{}".format(__name__))


class Trowel:

    """ interacts with the HDFStore, and clients """

    def __init__(self, config):
        self.config = config
        self.rc = RestClient()
        self.pc = rest_wrapper()
        pd.set_option('io.hdf.default_format', 'table')
        self.store = pd.HDFStore("../resources/data/pybcm.hd5")

    def summary(self):
        raise NotImplemented

    #TODO: call the rest wrapper instead
    # create a wanted list from a set
    def get_set_inv(self, lego_set_id):
        inv = self.rc.get_subsets(lego_set_id, 'SET')
        return inv

    def get_item_prices_df(self, itemid, itemtypeid, color):
        pg = self.pc.get_priceguide_summary_df(itemid, itemtypeid, color, guide_type='sold')
        return pg

    def get_inv_prices(self, inv=None):
        """ build a dataframe for the passed Rest inventory

            inv is a list of {'match_no': 0, 'entries': [{'item': {'no': '2540',
                                              'name': 'Plate, Modified 1 x 2 with Handle on Side - Free Ends',
                                              'type': 'PART', 'category_id': 27}, 'color_id': 11, 'quantity': 2,
                                     'extra_quantity': 0, 'is_alternate': False, 'is_counterpart': False}]}
        """
        # TODO: Account for subsititutions and find the cheapest of substitutions

        needed = want_list_from_rest_inv(inv)

        # load existing prices from the db and download the rest

        pull_list, price_df = self.prune_pull_list(needed)
        # download the list of items in pull_list and build the pandas dataframe
        for item in pull_list:  # iterate over list of matches

            # create a pull list of
            # TODO: Check if price already exists in DB and is not older than a particular date before reloading it

            itemid, color, itemtypeid, wanted_qty = item
            # get the dataframe of the price summary
            # TODO use the PriceDataFrame here
            prices = self.get_item_prices_df(itemid, itemtypeid, color)
            if prices is not None:
                prices['wanted_qty'] = item[3]
                # wanted_avg = prices['wanted_qty'] * prices['avg_price']
                #TODO: use a PriceDataFrame here
                price_df = price_df.append(prices)
            else:
                logger.info("No items to pull")
            logger.debug(
                "Item: {}, Color: {}, Qty: {}, Avg Price: {}".format(itemid, color, wanted_qty, prices['avg_price'][0]))

        # add the new prices to the save
        # combine all of the prices and return them

        # merge the wanted list before returning
        price_df = merge_prices_with_want(needed, price_df)
        return price_df

    def add_prices_to_store(self, prices):
        if ~prices.empty:
            prices = prices.reset_index(drop=True).drop('wanted_qty', axis=1)  # flatten prices df and drop the wantedqty
            with self.store as store:
                store.open()
                if 'prices' not in store:
                    store.prices = pd.DataFrame()
                num_orig_rows = store.prices.shape[0]
                merged = store.prices.append(prices)
                merged = merged.set_index(PRICEGUIDE_INDEX)
                merged = merged[~merged.index.duplicated(keep='last')]
                merged = merged.reset_index(drop=True)
                num_new_rows = merged.shape[0]
                self.store.append('prices', merged)
                store.flush()
                logger.info("Added {} rows to store.prices".format(num_new_rows - num_orig_rows))

    @classmethod
    def estimate_inv_cost(cls, prices):
        est_cost = dict({"N": 0.0, "U": 0.0})
        p = prices.reset_index(drop=True)
        p['wanted_avg'] = p['wanted_qty'] * p['avg_price']
        est_cost['N'] = p[p['new_or_used'] == 'N']['wanted_avg'].sum()
        est_cost['U'] = p[p['new_or_used'] == 'U']['wanted_avg'].sum()
        return est_cost

    def prune_pull_list(self, needed):
        with self.store as store:
            store.open()
            if 'prices' in store:
                all_prices_df = store['prices'] #.set_index(PRICEGUIDE_INDEX)
                needed_df = tuplelist_as_df(needed)
                pull_df = dfa_not_in_dfb(needed_df, all_prices_df)
                pull_list = df_to_tuplelist(pull_df)
                already_known_prices_df = dfa_in_dfb(all_prices_df, needed_df)
            else:
                pull_list = needed
                already_known_prices_df = pd.DataFrame()
            return pull_list, already_known_prices_df
            store.close()

if __name__ == "__main__":
    logger = log.setup_custom_logger("pybcm")

    from pprint import pprint

    tr = Trowel('../config/bcm.ini')
    inv = tr.get_set_inv('10030-1')
    pprint(tr.get_inv_prices(inv))

    # price out a set by collecting avg prices from wanted list

    # list substitutes in a wanted list
