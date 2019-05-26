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
    Get prices for individual PARTS

"""
from deprecated import log
from deprecated.dataframe import *
from pybcm.brick_data import BrickData

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("pybcm.{}".format(__name__))


class BrickInfo:

    """ Retrieves information about individual parts """

    def __init__(self, rw: BrickData):
        #self.rc = rc
        self.rw = rw
        #pd.set_option('io.hdf.default_format', 'table')
        #self.prices_key = 'prices'
        #self.store = pd.HDFStore("../resources/data/pybcm.hd5")


    def get_item_summary_prices_df(self, itemid, itemtypeid, color, guide_type='sold'):
        """
        Retrieve a priceguide DataFrame from the BrickData
        :param itemid:
        :param itemtypeid:
        :param color:
        :param guide_type: 'sold' or 'stock'
        :return Price guide DataFrame:
        """
        pg = self.rw.get_price_summary(itemid, itemtypeid, color, guide_type=guide_type)
        # do some stuff to this data before returning it
        return pg

    def get_item_detail_prices_df(self, itemid, itemtypeid, color, guide_type='sold'):
        pg = self.rw.get_part_price_details(itemid, itemtypeid, color, guide_type)
        return pg




if __name__ == "__main__":
    logger = log.setup_custom_logger("pybcm")

    from pprint import pprint

    tr = Trowel('../config/bcm.ini')
    inv = tr.get_set_inv('10030-1')
    pprint(tr.get_inv_prices_df(inv))

    # price out a set by collecting avg prices from wanted list

    # list substitutes in a wanted list
