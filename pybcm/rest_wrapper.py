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


import pybcm.const as const
from pybcm.dataframe import *  # get monkey-patched version of DataFrame
from pybcm.rest import RestClient


class RestWrapper:
    """Provides a DataFrame wrapper for the RestClient class. Most methods return
        DataFrames based on the Rest responses. Many of them rely on the results from
        the RestClient's get_price_guide results.
     """
    def __init__(self, config):

        self.config = config
        self.rc = RestClient(config)

    def get_priceguide_summary_df(self, itemid, itemtypeid, colorid, guide_type='sold', details=False):
        """
        :param itemid: Item id
        :param itemtypeid: Item type
        :param colorid: Color
        :param guide_type: 'sold' or 'stock'
        :param details: boolean whether to collect price details as well
        :return price_df: DataFrame of the price summary for a specific item (not detailed prices)

        get_priceguide_summary_df returns a dictionary of the following format:

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
        price_df = _summary_df_from_json(pg_json, colorid)
        return price_df

    def get_part_priceguide_summary_df(self, itemid, colorid):
        """Shortcuts the get_priceguide_summary_df with default PART values"""
        df = self.get_priceguide_summary_df(itemid, 'PART', colorid)
        return df

    def get_part_priceguide_details_df(self, itemid, colorid, new_or_used='U', guide_type='stock'):
        pg = self.rc.get_price_guide(itemid, 'PART', colorid, new_or_used, guide_type)
        if pg is None:
            raise ValueError("Problem retrieiving price details for {}: {}".format(itemid, colorid))
        pg['item']['color'] = colorid
        df = _details_df_from_json(pg)
        return df

    def get_known_colors(self, itemid, itemtypeid):
        """Get the available colors for a given item"""
        colors = self.rc.get_known_colors(itemid, itemtypeid)
        df = pd.DataFrame.from_dict(colors, orient="columns").set_index(['color_id'])
        return df


#TODO: this function needs to be reworked
def _summary_df_from_json(dict_tuple, color, sold_or_stock='sold'):
    """
    Build a DataFrame of the priceguide for a single part(item + color). Color is
    required since color is not contained in the priceguide information
    :param dict_tuple: = a tuple of ({new_prices}, {used_prices}) where {X_prices} look like:

    {
      "item": {
        "no": "3006",
        "type": "PART"
      },
      "new_or_used": "N",
      "currency_code": "USD",
      "min_price": "0.0525",
      "max_price": "3.4290",
      "avg_price": "0.5332",
      "qty_avg_price": "0.3653",
      "unit_quantity": 978,
      "total_quantity": 14810,
      "price_detail": [
        {
          "quantity": 1,
          "unit_price": "0.6384",
          "seller_country_code": "US",
          "buyer_country_code": "US",
          "date_ordered": "2017-02-16T23:58:22.797Z",
          "qunatity": 1
        },
        {
          "quantity": 1,
          "unit_price": "0.5925",
          "seller_country_code": "US",
          "buyer_country_code": "US",
          "date_ordered": "2017-02-18T05:42:10.397Z",
          "qunatity": 1
        }
      ]
    }
    :param color: Color isn't contained in the JSON results, so we track it as well
    :param sold_or_stock: Flag whether the prices are sold or stock prices
    :return summary_df:
    """

    # define table fields
    common_fields = ['item', 'itemtype', 'color']
    #common_fields = const.
    numeric_fields = ['avg_price', 'max_price', 'min_price', 'qty_avg_price', 'total_quantity', 'unit_quantity']
    summary_pull_fields = ['new_or_used', 'currency_code'] + numeric_fields
    df_columns = common_fields + summary_pull_fields

    if not set(df_columns) == set(const.PRICEGUIDE_COLUMNS):
        raise ValueError("Wrong column names: {}".format(df_columns))

    common_values = {'item': dict_tuple[0]['item']['no'],
                     'itemtype': dict_tuple[0]['item']['type'],
                     'color': color}

    # create a dictionary with the remainder of the values in dict_tuple for 'N' and 'U'
    summary = [{key: dict_tuple[idx][key] for key in summary_pull_fields} for idx in (0, 1)]
    for item in summary:
        item.update({**common_values})

    summary_df = pd.DataFrame(summary, columns=df_columns)
    summary_df[numeric_fields] = summary_df[numeric_fields].apply(pd.to_numeric)
    summary_df['sold_or_stock'] = sold_or_stock

    return summary_df


def _details_df_from_json(price_dict):
    """
    Returns a DataFrame containing the price_details of a single catalog Item.
    :param price_dict: One Item entry of the JSON data
    :return: result as DataFrame
    """
    details = price_dict['price_detail']
    details_df = pd.DataFrame(details)
    details_df = details_df.drop('qunatity', axis=1)
    return details_df
