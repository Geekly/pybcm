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
from db import *
from rest import RestClient

logger = logging.getLogger('pybcm.trowel')


class Trowel:
    def __init__(self):
        self.rc = RestClient()

    # create a wanted list from a set
    def get_set_inv(self, lego_set_id):
        inv = self.rc.get_subsets(lego_set_id, 'SET')
        return inv

    def get_part_prices(self, itemid, color):
        pg = self.rc.get_price_guide(itemid, 'PART', color, 'N', guide_type='sold')
        color, prices = pg
        return prices

    def price_inv(self, inv):
        """ get estimated price for a given inventory """
        """inv is a list of {'match_no': 0, 'entries': [{'item': {'no': '2540',
                                              'name': 'Plate, Modified 1 x 2 with Handle on Side - Free Ends',
                                              'type': 'PART', 'category_id': 27}, 'color_id': 11, 'quantity': 2,
                                     'extra_quantity': 0, 'is_alternate': False, 'is_counterpart': False}]}
        """
        # TODO: Account for subsititutions and find the cheapest of substitutions
        est_cost = 0.0
        # get a list of items from the first item in matches
        # TODO: get all of the items in matches (alternates)
        need_items = [ match['entries'][0] for match in inv]
        # create a set of itemid|color elements to compare to existing prices
        need_elements = {( item['item']['no'], str(item['color_id'])) for item in need_items }
        # get the list of exisiting elements from the db

        for match in inv:  # iterate over list of matches

            #TODO: Check if price already exists in DB and is not older than a particular date before reloading it

            # make a set of itemid, color tuples that are already in the db
            # get prices for the negative set
            # retrieve_set = wanted_set - db_set
            item = match['entries'][0]
            itemid = item['item']['no']
            color = item['color_id']
            element = '|'.join([itemid, color])
            qty = int(item['quantity'])
            prices = self.get_part_prices(itemid, color)
            if prices:

                avg_price, min_price, max_price, qty_avg_price = \
                    (
                        float(prices['avg_price']), \
                        float(prices['min_price']), \
                        float(prices['max_price']), \
                        float(prices['qty_avg_price'])
                    )
                aprices = {}
                aprices['avg_price'], aprices['min_price'], aprices['max_price'], aprices['qty_avg_price'] = \
                    avg_price, min_price, max_price, qty_avg_price
                aprices['itemid'] = itemid
                aprices['color'] = color
                aprices['new_or_used'] = prices['new_or_used']
                aprices['unit_quantity'] = prices['unit_quantity']
                aprices['total_quantity'] = prices['total_quantity']

                with conn:
                    result = serialize_part_prices(aprices)

            else:
                avg_price, min_price, max_price, qty_avg_price = (0, 0, 0, 0)

            est_cost += avg_price * qty
            logger.debug("Item:{}, Color:{}, Qty:{}, Avg Price:{}".format(itemid, color, qty, avg_price))
            logger.debug("Price of {} up to ${:0.2f}".format(itemid, est_cost))

        return est_cost


if __name__ == "__main__":
    logger = log.setup_custom_logger('pybcm')

    from pprint import pprint

    tr = Trowel()
    inv = tr.get_set_inv('10030-1')
    pprint(tr.price_inv(inv))

    # price out a set by collecting avg prices from wanted list

    # list substitutes in a wanted list
