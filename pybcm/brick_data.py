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
import logging
from typing import Dict, List

import pandas as pd

import pybcm.const as const
from pybcm.config import BCMConfig
from pybcm.const import ItemType, GuideType, NewUsed, Region
from pybcm.legoutils import legoColors
from pybcm.rest import RestClient

logger = logging.getLogger(__name__)


class BrickData:
    """Provides a DataFrame wrapper for the RestClient class. Most methods return
        DataFrames based on the Rest responses. Many of them rely on the results from
        the RestClient's get_price_guide results.
     """

    def __init__(self, config: BCMConfig):

        self.config = config
        self.rc = RestClient(config)

        self._color_df = None
        self.load_colors_from_bl()  # load colors into self._category_df
        self._category_df = None
        self.load_categories_from_bl()  # load categories into self._category_df

    def get_brick_price_summary(self, brick, new_used='N', guide_type=GuideType.sold):
        return self.get_price_summary(brick.itemid, brick.itemtype, brick.color,
                                      new_or_used=new_used, guide_type=guide_type)

    # def get_priceguide(self, itemid, itemtypeid, colorid,
    #                    new_or_used=NewUsed.N,
    #                    guide_type=GuideType.stock,
    #                    region=Region.north_america):
    #     """returns a tuple containing (summary df, details df)
    #
    #     """
    #     pg = self.rc.get_price_guide(itemid, itemtypeid, colorid, new_or_used=new_or_used, guide_type=guide_type, region=region)
    #

    def get_price_summary(self, itemid, itemtypeid, colorid,
                          new_or_used=NewUsed.N,
                          guide_type=GuideType.sold,
                          region=Region.north_america)->pd.DataFrame:
        """
        :param itemid: Item id
        :param itemtypeid: Item type
        :param colorid: Color
        :param new_or_used: N or U from NewUsed
        :param guide_type: 'sold' or 'stock' from GuideType
        :param region: various from Region
        :return price_df: DataFrame of the price summary for a specific item (not detailed prices)

        get_price_summary returns a dictionary of the following format:

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
        itemid = str(itemid)
        itemtypeid = str(itemtypeid)
        colorid = str(colorid)

        if not set(new_or_used).issubset(NewUsed):  # each item in new_or_used must appear in NewUsed
            raise ValueError(f"Invalid value for new_or_used: {new_or_used}")

        if type(new_or_used) is not list: # make a single value a list if it isn't already
            new_or_used = [new_or_used]

        pg_json = [
            self.rc.get_price_guide(itemid, itemtypeid, colorid, new_or_used=nu, guide_type=guide_type, region=region)
            for nu in new_or_used
        ]

        if any([pg is None for pg in pg_json]):
            raise ValueError("Problem retrieiving {}: {}".format(itemid, colorid))

        price_df = self._summary_df_from_json(pg_json, colorid, guide_type=guide_type, region=region)  # leave off the detail info
        return price_df

    def get_part_price_summary(self, itemid: str, colorid: str, new_or_used: List[str]=[NewUsed.N],
                               guide_type: str=GuideType.stock)->pd.DataFrame:
        """Shortcuts the get_price_summary with default PART values"""
        df = self.get_price_summary(itemid, ItemType.PART, colorid,
                                    new_or_used=new_or_used, guide_type=guide_type)
        return df

    def get_part_price_details(self, itemid, colorid, new_or_used=NewUsed.N, guide_type=GuideType.stock):
        priceguide = self.rc.get_price_guide(itemid, ItemType.PART, colorid,
                                             new_or_used=new_or_used, guide_type=guide_type)
        if priceguide is None:
            raise ValueError("Problem retrieiving price details for {}: {}".format(itemid, colorid))
        priceguide['item']['color'] = colorid
        df = self._details_df_from_json(priceguide)
        return df

    def get_known_colors(self, itemid, itemtypeid)->pd.DataFrame:
        """Get the available colors for a given item"""
        colors = self.rc.get_known_colors(itemid, itemtypeid)
        df = pd.DataFrame.from_dict(colors, orient="columns")
        df['color_name'] = df['color_id'].apply(lambda x: legoColors[x])
        df = df.set_index(['color_id'])
        return df

    def get_all_colors(self)->pd.DataFrame:
        color_dict = self.rc.get_all_colors()
        df = pd.DataFrame(color_dict)
        return df

    def load_colors_from_bl(self):
        self._color_df = self.get_all_colors()

    def get_categories(self):
        cat_dict = self.rc.get_category_list()
        df = pd.DataFrame(cat_dict)
        return df

    def load_categories_from_bl(self):
        self._category_df = self.get_categories()

    def get_set_inventory(self, itemid: str)->pd.DataFrame:
        """Get the contents of a set from the Rest API and convert it to a pandas DataFrame """
        json_inv = self.rc.get_subsets(itemid, ItemType.SET)
        if self.validate_json_set(json_inv):
            inv_list = self._json_inv_to_dict_list(json_inv)
            df = self._inv_dict_list_to_dataframe(inv_list)
        else:
            raise TypeError("Bricklink inventory must be a set")
        return df

    @staticmethod
    def validate_json_set(json_inv):
        # todo: write this function
        if json_inv:
            return True
        else:
            return False


    @staticmethod
    def _json_inv_to_dict_list(inv: List[dict]) -> List[dict]:
        """
        Convert to a set inventory to a list of dictionaries appropriate for initiliazing a pandas DataFrame
        :param inv: json formatted inventory from BrinkLink
        :return:

        [{'entries': [{'color_id': 86,
                       'extra_quantity': 0,
                       'is_alternate': False,
                       'is_counterpart': False,
                       'item': {'category_id': 5,
                                'name': 'Brick 2 x 2 Corner',
                                'no': '2357',
                                'type': 'PART'},
                       'quantity': 2}],
          'match_no': 0}, ...]

        """
        flat_inv = []
        for price_item in inv:
            d = dict()
            e = price_item['entries'][0]  # could be multiple matches, but use the first one.
            d['item_id'] = str(e['item']['no'])
            d['color_id'] = str(e['color_id'])
            d['name'] = e['item']['name']
            d['itemtype'] = e['item']['type']
            d['category_id'] = str(e['item']['category_id'])
            d['quantity'] = int(e['quantity'])
            flat_inv.append(d)

        return flat_inv

    @staticmethod
    def _inv_dict_list_to_dataframe(inv: list) -> pd.DataFrame:
        """
        Convert a list of elements (see format below) to a DataFrame
            [{'item_id': '2357',
              'color_id': 86,
              'name': 'Brick 2 x 2 Corner',
              'itemtype': 'PART',
              'category_id': 5,
              'quantity': 2}, ...]
        """
        columns = ['item_id', 'color_id', 'name', 'itemtype', 'category_id', 'quantity', ]
        df = pd.DataFrame(inv, columns=columns)
        # Create the element_id column and set as index
        df['element_id'] = df[['item_id', 'color_id']].apply(tuple, axis=1)
        df.set_index('element_id', inplace=True)
        return df

    @staticmethod
    def _summary_df_from_json(price_list: List[Dict], color: int, guide_type=GuideType.sold, region=Region.north_america) -> pd.DataFrame:
        """
        Build a DataFrame of the priceguide for a single part(item + color). Color is added
        since color is not contained in the priceguide information
        :param price_list: = a tuple of ({new_prices}, {used_prices}) where {X_prices} look like:

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

        # define column names for the DataFrame

        common_fields = ['item_id', 'itemtype', 'color_id']
        numeric_fields = ['avg_price', 'max_price', 'min_price', 'qty_avg_price', 'unit_quantity', 'total_quantity']
        string_fields = ['new_or_used', 'currency_code']
        summary_pull_fields = string_fields + numeric_fields
        df_columns = common_fields + summary_pull_fields

        if not set(df_columns) == set(const.PRICEGUIDE_COLUMNS):  # compare the columns above with those defined in const.
            raise ValueError("Wrong column names: {}".format(df_columns))

        # common_values = {'item_id': price_list[0]['item']['no'],
        #                  'itemtype': price_list[0]['item']['type'],
        #                  'color_id': color}

        # will at most be two rows in the list, 'N' and 'U', but doesn't have to be the case
        # create a list of dictionaries with the remainder of the non-common values in price dict for 'N' and 'U'
        # summary = [{key: price_list[idx][key] for key in summary_pull_fields} for idx in (0, 1)]
        # add dictionary entries for the common values
        # for item in summary:
        #     item.update({**common_values})

        summary = [] # list of price ditionaries
        for idx, row in enumerate(price_list):
            item = {key: row[key] for key in summary_pull_fields}
            common_values = {'item_id': row['item']['no'],
                             'itemtype': row['item']['type'],
                             'color_id': color}
            item.update({**common_values})
            summary.append(item)
            logger.debug(f"_summary_df_from_json: adding summary Item: {item}")

        summary_df = pd.DataFrame(summary, columns=df_columns)
        summary_df[numeric_fields] = summary_df[numeric_fields].apply(pd.to_numeric)
        summary_df['sold_or_stock'] = guide_type
        summary_df['region'] = region

        return summary_df

    @staticmethod
    def _details_df_from_json(priceguide: dict)->pd.DataFrame:
        """
        Returns a DataFrame containing the price_details of a single catalog Item.
        :param priceguide: Complete Priceguide Item
        :return: result as DataFrame
        """
        details = priceguide['price_detail']
        details_df = pd.DataFrame(details)  # details is a dictionary
        details_df = details_df.drop('qunatity', axis=1)
        details_df['unit_price'] = details_df['unit_price'].astype(float)
        return details_df
