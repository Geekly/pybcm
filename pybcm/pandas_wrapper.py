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

"""Wrapper for the Rest client that provides results in pandas format"""

import logging

import pandas as pd

from blrest import RestClient
from config import BCMConfig

logger = logging.getLogger('pybcm.pandas_wrapper')


class PandasClient:
    def __init__(self, config=BCMConfig('../config/bcm.ini')):
        self.rc = RestClient()
        self.config = config

    def get_item(self, itemid, itemtypeid):
        raise NotImplemented

    def get_supersets(self):
        raise NotImplemented

    def get_subsets(self, itemid, itemtypeid):
        raise NotImplemented

    def get_price_guide(self, itemid, colorid, itemtypeid, new_or_used='U', guide_type='sold'):
        """
        :param itemid:
        :param itemtypeid:
        :param colorid:
        :param new_or_used:
        :param guide_type:
        :return:

        DataFrame:
        itemid itemtypeid color new_or_used avg_price max_price min_price qty_avg_price unit_quantity total_quantity age
        itemid color new_or_used

        Create two tables - a single row for the data summary and a second table for the
        price detail
        get_price_guide returns a dictionary of the following format:

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
        color, pg_json = self.rc.get_price_guide(itemid, colorid, itemtypeid, new_or_used, guide_type)
        pg = self.make_pandas_from_json(pg_json, color)
        return pg

    def get_part_price_guide(self, itemid, colorid, new_or_used='U'):
        pg = self.get_price_guide(itemid, 'PART', colorid, new_or_used)
        return pg

    def get_known_colors(self, itemid, itemtypeid):
        raise NotImplemented

    def make_pandas_from_json(self, json_dict, color):
        item_fields = ['no', 'color', 'type']

        summary_pull_fields = ['new_or_used', 'avg_price', 'max_price', 'min_price',
                          'qty_avg_price', 'total_quantity', 'unit_quantity', 'currency_code']
        all_summary_fields = ['item', 'color'] + summary_pull_fields
        stock_detail_fields = ['quantity', 'unit_price', 'shipping_available']
        sold_detail_fields = ['quantity', 'unit_price', 'seller_country_code', 'buyer_country_code', 'date_ordered']
        common_detail_fields = list(set(stock_detail_fields) & set(sold_detail_fields))
        summary = {'item': json_dict['item']['no'],
                   'color': color}
        summary_dict = {key: json_dict[key] for key in summary_pull_fields}
        summary.update(summary_dict)
        summary_series = pd.Series(summary, index=all_summary_fields)


        # make the price details dataframe
        # TODO: for now, ignoring sold and stock and just using the common fields

        return summary_series
