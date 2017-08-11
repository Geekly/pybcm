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
    Mason manages the solution and results of the optimization

"""
import pandas as pd

from rest import RestClient


class Mason:

    def __init__(self, brickpile):
        # required data
        # TODO: change to reference individual price and qty dataframes
        self.__prices = brickpile.df
        self.__price_df = brickpile.price_frame
        self.__qty_df = brickpile.qty_frame
        self.__wanted = brickpile.wanted
        self.__vendormap = brickpile.vendormap
        self.rest_client = RestClient()

        # working data
        self.shipping_cost = 3.00
        #self._simple_wanted = {e: self._wanted.get_wanted_qty(e) for e in self._wanted }
        #self.current_stock = dict.fromkeys(self._wanted.keys(), 0)
        #self.remaining = None
        #self.stock = DataFrame() # includes original wanted qty, current stock, amt remaining to buy

        # solution data
        # solution data is a table of elements vs. vendors with qty only as the value
        self.solution = pd.DataFrame(columns=self.__price_df.columns, index=self.__price_df.index, data=None)



    #TODO: calculate the part cost of a solution

    #TODO: calculate the total cost of a solution