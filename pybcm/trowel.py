# Copyright (c) 2012-2019, Keith Hooks
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
    Manage bricklink data through the pandas wrapper api. This is a high level user interface for gathering and
    operating on price lists and inventories.

"""
import logging
from typing import List

import pandas as pd

from pybcm.brick_data import BrickData

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(f"pybcm.{__name__}")


class Trowel:

    """ interacts with the HDFStore and rest clients to build and operate on datasets """

    def __init__(self, config):
        self.config = config
        #self.rc = RestClient()  #TODO: really shouldn't have to manage both a RestClient and a BrickData at this level
        self.bd = BrickData(config)
        # self.bp = BrickInfo(self.rc, self.bd)
        # pd.set_option('io.hdf.default_format', 'table')
        self.prices_key = 'prices'
        # self._store = pd.HDFStore("../resources/data/pybcm.hd5")

    def summary(self):
        raise NotImplemented

    #TODO: call the rest wrapper instead
    # create a wanted list from a set
    def price_sets(self, set_list: List[str]):
        """
        Get prices for a list of sets, by set name
        :param set_list: ex. ['10182-1', '10185-1', '10190-1'
        :return prices: dictionary of prices with set names as keys
        """
        prices = dict()
        for _set in set_list:
            prices[_set] = self.set_summary(_set)
        return prices

    def get_set_inv(self, lego_set_id):
        """Retrieve a JSON-formatted inventory from the string formatted lego_set_id"""
        inv = self.rc.get_subsets(lego_set_id, 'SET')
        return inv

    def get_item_prices_df(self, itemid, itemtypeid, color, guide_type='sold'):
        """
        Retrieve a priceguide DataFrame from the BrickData and add it to the store.
        :param itemid:
        :param itemtypeid:
        :param color:
        :param guide_type: 'sold' or 'stock'
        :return Price guide DataFrame:
        """
        pg = self.bp.get_item_prices_df(itemid, itemtypeid, color, guide_type=guide_type)
        # whenever new data is pulled, add it to the store
        logger.debug("Adding {} to store".format(pg))
        with self._store as store:
            store.open()
            store.append(self.prices_key, pg, data_columns=True,   # const.HDF_PRICE_COLUMNS
                         min_itemsize={'item': 16, 'color': 5, 'new_or_used': 5, 'itemtype': 8, 'currency_code': 6})
        return pg

    def get_item_prices_from_details_df(self, itemid, itemtypeid, color, guide_type='sold'):
        pg = None
        return pg

    def get_inv_prices_df(self, inv):
        """ build a dataframe for the passed Rest inventory

        :param inv:    A list of JSON-formatted items like {'match_no': 0, 'entries': [{'item': {'no': '2540',
                                              'name': 'Plate, Modified 1 x 2 with Handle on Side - Free Ends',
                                              'type': 'PART', 'category_id': 27}, 'color_id': 11, 'quantity': 2,
                                     'extra_quantity': 0, 'is_alternate': False, 'is_counterpart': False}]}

        :return price_df:  A data frame of the prices where:
                        index = ['item', 'color', 'new_or_used'] and
                        columns = ['itemtype', 'wanted_qty', 'currency_code', 'avg_price', 'max_price',
                                    'min_price', 'qty_avg_price', 'total_quantity', 'unit_quantity']
        """
        # TODO: Account for subsititutions and find the cheapest of substitutions

        needed = want_list_from_rest_inv(inv)
        # load existing prices from the db and download the rest

        pull_list, price_df = self.remove_known_from_pull_list(needed)
        adding = len(pull_list)
        logger.info("Pulling data for {:.0f} new items".format(adding))
        # download the list of items in pull_list and build the pandas dataframe
        for index, item in enumerate(pull_list):  # iterate over list of match tuples
            logger.info("Pulling item {:.0f} of {:.0f}".format(index+1, len(pull_list)))
            itemid, color, itemtypeid, wanted_qty = item
            prices = self.get_item_prices_df(itemid, itemtypeid, color)
            if prices is not None:
                price_df = price_df.append(prices)
            else:
                logger.info("No items to pull")
            logger.debug(
                "Item: {}, Color: {}, Qty: {}, Avg Price: {}".format(itemid, color, wanted_qty, prices['avg_price'][0]))

        # add the new prices to the save
        # combine all of the prices and return them

        # add wanted_qty to the price_df
        price_df = self.add_wanted_column(needed, price_df)
        return price_df

    # def add_prices_to_store(self, prices):
    #     """
    #     Add prices to the HDFStore based on the columns of const.HDF_PRICE_COLUMNS and ignoring the rest.
    #     :param prices: Price summary DataFrame of multiple parts
    #     :return added: Number of rows added to the storage
    #     """
    #     raise NotImplemented # don't use this anymore
    #
    #     if not isinstance(prices, pd.DataFrame):
    #         raise TypeError("DataFrame required")
    #     added = 0
    #     if not prices.empty:
    #         price_df = prices.reset_index().drop('wanted_qty', axis=1)  # flatten prices df and drop the wantedqty
    #
    #         with self.store as store:
    #             store.open()
    #             if '/prices' not in store.keys():
    #                 store.put('prices', price_df, format='table', data_columns=True)
    #             else:
    #                 num_orig_rows = store.prices.shape[0]
    #                 store.append('prices', price_df, data_columns=list(const.HDF_PRICE_COLUMNS))
    #                 store_df = store.prices
    #                 merged = store_df.set_index(PRICEGUIDE_INDEX)
    #                 merged = merged[~merged.index.duplicated(keep='last')]
    #                 merged = merged.reset_index()
    #                 num_new_rows = merged.shape[0]
    #                 store['prices'] = merged
    #                 store.flush()
    #                 added = num_new_rows - num_orig_rows
    #                 logger.info("Added {} rows to store.prices".format(added))
    #     return added

    @classmethod
    def best_prices(cls, price_df):
        """
        Find the best price among 'N' or 'U' for a given item and return the corresponding
        price dataframe
        :param price_df:
        :return best_price_df:
        """
        df = price_df.reset_index().set_index(['item', 'color', 'new_or_used'])
        df = df.sort_index() # most efficient indexing if sorted
        # find the set of unique indexes for the first two index levels
        two_level_idx = set(zip(df.index.get_level_values(0), df.index.get_level_values(1)))
        # loop over rows with the same index at level 0 and 1 finding the min 'avg_price'
        best_idx = [(*idx, df.loc[idx]['avg_price'].idxmin()) for idx in two_level_idx]
        best_price_df = df.loc[best_idx]
        return best_price_df.reset_index()

    @classmethod
    def estimate_inv_cost(cls, prices):
        """
        Calculate estimated prices based on the lowest prices between New and Used price catalogs
        :param prices:
        :return dictionary of costs:
        """
        est_cost = dict({"best": 0.0, "N": 0.0, "U": 0.0})
        b = cls.best_prices(prices)
        p = prices.reset_index()

        p['wanted_avg'] = p['wanted_qty'] * p['avg_price']
        est_cost['best'] = (b['wanted_qty']*b['avg_price']).sum()
        est_cost['N'] = p[p['new_or_used'] == 'N']['wanted_avg'].sum()
        est_cost['U'] = p[p['new_or_used'] == 'U']['wanted_avg'].sum()
        #logger.debug("")
        return est_cost


    @classmethod
    def first_two_level_index_pairs(cls, df):
        return list(zip(df.index.get_level_values(0), df.index.get_level_values(1)))

    #TODO: write a test for this method
    #TODO: add ability to date check
    def remove_known_from_pull_list(self, needed):
        """Compare needed to prices already contained in the Store.
        :param needed: original pull list of needed items typles as [(item1, color1, itemtypdid1, wanted_qty),...]
        :return pull_list: Updated list of tuples to be pulled [(item1, color1, itemtypdid1, wanted_qty),...]
        :return already_known_prices_df: price DataFrame containing prices already persisted in the store
        """
        logger.info("Pruning needed list of {} items".format(len(needed)))
        if isinstance(needed, pd.DataFrame):
            raise TypeError("needed should be a list of tuples")
        with self._store as store:
            store.open()
            if '/prices' in store.keys():
                all_prices_df = store['prices'] #.set_index(PRICEGUIDE_INDEX)
                needed_df = wanted_df_from_tuplelist(needed)
                pull_list = self.pull_list_from_known_and_needed(all_prices_df, needed_df)
                already_known_prices_df = all_prices_df.in_dfb(needed_df)
            else:
                pull_list = needed
                already_known_prices_df = pd.DataFrame()
        #store.close()
        return pull_list, already_known_prices_df

    @classmethod
    def pull_list_from_known_and_needed(cls, all_prices_df, needed_df):
        pull_df = needed_df.not_in_dfb(all_prices_df)
        pull_list = pull_df.to_tuplelist()  # build the wanted list as tuples
        logger.info("Pruned pull list contains {} elements".format(len(pull_list)))
        return pull_list

    def set_summary(self, set_name):
        """
        Estimate prices for the given set_name by reading prices and performing the summary calculations
        :param set_name:
        :return item: Dictionary of item with of estimated cost under 'cost' key
        """
        item = self.rc.get_item(set_name, 'SET')
        cost = self.summarize_set_cost(set_name)
        item['cost'] = cost
        return item

    def summarize_set_cost(self, set_name):
        _inv = self.get_set_inv(set_name)
        prices = self.get_inv_prices_df(_inv)
        cost = self.estimate_inv_cost(prices)
        logger.info("Estimated cost of set {} is {}".format(set_name, cost))
        return cost

    def add_wanted_column(self, want_tuplelist, prices_df):
        """
        Add wanted_qty from want_tuplelist to the prices DataFrame
        :param want_tuplelist: ('item', 'color', 'itemtype', 'wanted_qty')
        :param prices_df: Typcal prices DataFrame
        :return prices DataFrame with new 'wanted_qty' column:
        """
        prices_df = prices_df.reset_index(drop=True)
        want_df = pd.DataFrame(want_tuplelist, columns=['item', 'color', 'itemtype', 'wanted_qty'])
        full_df = pd.merge(want_df, prices_df, on=['item', 'color', 'itemtype'])
        full_df = full_df.set_index(PRICEGUIDE_INDEX)
        if 'wanted_qty' not in full_df.columns:
            raise KeyError("Prices missing wanted_qty")
        return full_df


if __name__ == "__main__":
    logger = log.setup_custom_logger("pybcm")

    from pprint import pprint

    tr = Trowel('../config/bcm.ini')
    inv = tr.get_set_inv('10030-1')
    pprint(tr.get_inv_prices_df(inv))

    # price out a set by collecting avg prices from wanted list

    # list substitutes in a wanted list
