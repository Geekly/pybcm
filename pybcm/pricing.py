import logging

import pandas as pd

from pybcm.brick_data import BrickData
from pybcm.config import BCMConfig
from pybcm.const import ItemType, GuideType, NewUsed

logger = logging.getLogger(__name__)

def eval_set_price(bd: BrickData, itemid: str, new_or_used: str, guide_type: str)->pd.DataFrame:
    """
    :param bd:
    :param itemid:
    :param new_or_used:
    :param guide_type:
    :return:
    """

    # get the set inventory
    inv = bd.get_set_inventory(itemid)

    # get all of the price summaries
    prices = get_price_summaries(bd, inv, new_or_used=new_or_used, guide_type=guide_type)

    # add price data to inventory dataframe
    inv = add_price_to_inv_df(inv, prices)

    return inv


def get_price_summaries(bd: BrickData, inv_df: pd.DataFrame, new_or_used=NewUsed.N, guide_type=GuideType.stock):
    """
    Get a dataframe of prices for the entire set
    :param bd:
    :param inv_df:
    :param new_or_used:
    :param guide_type:
    :return:
    """
    PARTSONLY = True

    # get price summaries for each part
    price_df = pd.DataFrame()
    for index, item in inv_df.iterrows():
        if item['itemtype'] == ItemType.PART:
            logger.debug(f"Getting {item['item_id'], item['color_id']}")
            lineitem = bd.get_part_price_summary(str(item['item_id']), str(item['color_id']),
                                                 new_or_used=new_or_used,
                                                 guide_type=guide_type)
            price_df = price_df.append(lineitem)

    return price_df


def add_price_to_inv_df(inv_df: pd.DataFrame, price_df: pd.DataFrame)->pd.DataFrame:

    # for each row in inventory, _get price summary and add itadd prices
    expanded_df = inv_df.reset_index().merge(price_df, on=['item_id', 'color_id']).set_index('element_id')
    expanded_df['min_avg_price'] = expanded_df[['avg_price', 'qty_avg_price']].min(axis=1)
    expanded_df['total_part_cost'] = expanded_df['quantity'] * expanded_df['min_avg_price']
    return expanded_df


def filter_lowest_prices(price_df: pd.DataFrame, min_quantity: int=10, quantile: float=0.1)->pd.DataFrame:
    """Select the lowest price values from the price details up to a given percentage of the total
    available. We're not going to pay higher than we need to for a given part, so it's useful to look
    at the cheapest parts at once.

    :param price_df: dataframe with 'quantity' and 'unit_price' fields
    :param min_quantity: int
    :param quantile: float between [0.0... 1.0]
    :return:  filtered dataframe
    """
    if not {'unit_price', 'quantity'}.issubset(price_df):
        raise KeyError("quantity and/or unit_price are missing from price data.")
    if not(min_quantity >= 0):
        raise ValueError
    if not(0.0 <= quantile <= 1.0):
        raise ValueError

    price_df = price_df[price_df['quantity'] >= min_quantity]
    price_df = price_df.sort_values('unit_price', ascending=True)
    price_df['cumsum'] = price_df['quantity'].cumsum()

    sum_limit = int(quantile * price_df['quantity'].sum())

    price_df = price_df[price_df['cumsum']<sum_limit].drop(columns=['cumsum'])
    return price_df


if __name__ == '__main__':
    bd = BrickData(BCMConfig('../config/bcm.ini'))

    set_list = ['561410-1', '561408-1', '561409-1']

    prices = {}
    for lego_set in set_list:
        set_price = eval_set_price(bd, lego_set, 'N', 'stock')
        prices[lego_set] = set_price
        print(f"{lego_set}: ${set_price['total_part_cost'].sum():.2f}")



