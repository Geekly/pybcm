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
Manage the store inventory data in a pandas dataframe



"""

# TODO: add prices of used parts to the system
# TODO: add ability to limit vendor search area

import logging
import pickle

import numpy as np
import pandas as pd
from pandas import DataFrame

import log
from elementreader import ElementWebReader, NEW, USED
from vendors import VendorMap

logger = logging.getLogger('pybcm.brickpile')


def dataframe_from_pricelist(price_list):
    _data = [ p._asdict() for p in price_list]

    columns = ['elementid', 'condition', 'storeid', 'price', 'qty']
    _df = pd.DataFrame(_data, columns=columns)
    _df.set_index(['elementid', 'condition', 'storeid'], inplace=True)

    return _df


class BrickPile:
    """Processes a wanted list and build a datafram from it.
    The price information is stored in a pandas dataframe of the following format
    
                        store1			store2
                n/u     price   qty		price	qty
    ______________________________________________
    '1754|34'	new 	0.04	3		27      2.8
                used    0.03    4       15      5          
    '3004|20'	new	    0.3		2.8		20		2   

    Indexing examples
     
        df.loc[:, ('100058', 'price') ]
        Out[39]: 
        30363|86    0.56
        3004|2      0.00
        3004|86     0.08
        75c12|86    0.00
        75c08|86    0.60
        Name: (100058, price), dtype: float64

        this class also works on the vendor_map, which maps vendor ID to vendor name
        
    To select only price, or qty data:
        df.xs('price', level=1, axis=1)

                  98960  99732  99841  
        30363|86   0.00   0.00   0.00  
        3004|2     0.14   0.08   0.09  
        3004|86    0.00   0.08   0.09  
        75c12|86   0.00   0.00   0.00  
        75c08|86   0.00   0.00   0.00  

    """

    # TODO: change data format to a pandas table

    def __init__(self):

        self.df = DataFrame()  # price data
        self.vendormap = VendorMap()
        self._wanted_dict = None
        self._bricklink_initialized = False
        self._vendor_initialized = False
        logger.debug("BrickPile vendormap id: %s" % id(self.vendormap))
        self.webreader = ElementWebReader(self.vendormap)

    @property
    def wanted(self):
        return self._wanted_dict

    @wanted.setter
    def wanted(self, wanted_dict):
        self._wanted_dict = wanted_dict

    @property
    def vendormap(self):
        return self._vendormap

    @vendormap.setter
    def vendormap(self, vendormap_):
        self._vendormap = vendormap_

    def __str__(self):
        assert self._bricklink_initialized, "bricklink not initialized, cannot convert to string"
        return self.xmlvendordata()

    def add_pricelist(self, elementid, pricelist):
        # pricelist : array of PriceTuple's
        # There could be multiple price/qty entries per vendor, but these need to be pruned
        # to a single Pricetuple per vendor
        logging.debug("Adding pricelist to df")
        if pricelist:
            # remove duplicate vendor columns from pricelist
            _df = dataframe_from_pricelist(pricelist)
            # print(_df)
            self.merge_frame(_df)
        else:
            raise ValueError("No Price Information found for %s" % elementid)
        return

        self.df.fillna(0, inplace=True)

    def merge_frame(self, df_):
        if not self.df.empty:
            # logger.debug("self.df, id(self.df)", self.df, id(self.df))
            # logger.debug("df_", pprint.pformat(df_.__repr__()))
            try:
                self.df = pd.concat([df_, self.df])
            except AssertionError:
                logger.info("Assertion error in concat")
        else:
            self.df = df_.copy()
        return

    def readpricesfromweb(self, wanted_dict, price_options=NEW | USED):
        """Build a dictionary of price info from the Bricklink website
            Attributes:
                wanted_dict(WantedDict): wanted[elementid] = WantedElement
        """
        self.wanted = wanted_dict
        numitems = len(wanted_dict)
        logging.info("Loading " + str(numitems) + " items from the web")
        for elementid in list(wanted_dict.keys()):
            # added wanted item to dataframe
            logging.info("Loading element " + str(elementid))
            itemid = wanted_dict[elementid].itemid
            itemtypeid = wanted_dict[elementid].itemtypeid
            itemcolorid = wanted_dict[elementid].colorid
            _elementid, pricelist = self.webreader.web_price_list(itemtypeid, itemid, itemcolorid, price_options)
            self.add_pricelist(elementid, pricelist)

        self._bricklink_initialized = True
        # convert NaN's to zeros

    # TODO: Initialize from a file as well
    def read_prices_from_file(self, filename):
        # needs to be defined
        raise NotImplementedError

    def price_to_pickle(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.df, file=f)
        pass

    def price_from_pickle(self, filename):

        df_ = pd.read_pickle(filename)
        if self.df is not None:
            self.df = df_
            self._bricklink_initialized = True
            return True
        else:
            raise ValueError("price frame is empty")

        return False

    @property
    def price_frame(self):
        # TODO: fix this
        return self.df['price']

    @property
    def qty_frame(self):
        # TODO: fix this
        return self.df['qty']

    @property
    def avg_prices(self):
        return self.price_frame.mean(level=['elementid', 'condition'])

    def summary(self):
        """Return a summary string of the bricklink data."""
        assert self._bricklink_initialized == True, "bricklink not initialized, cannot report dataquality"
        items, vendors = self.df.shape
        s = ''.join(["Price list includes:\n"
                     "Total Elements: %s\n" % items,
                     "Total Vendors: %s\n" % vendors]
                    )
        return s


if __name__ == '__main__':
    logger = log.setup_custom_logger(__name__)
    pass
