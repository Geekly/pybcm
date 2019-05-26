import pandas as pd

from const import GuideType, NewUsed
from pybcm.brick_data import BrickData


def eval_set_price(bd: BrickData, itemid: str, stock_or_sold: str=GuideType.stock, new_or_used: str=NewUsed.N):
    """
    :param elementid:
    :param new_or_used:
    :return:
    """

    # _get the set inventory
    # _get all of the price summaries
    # add price data to inventory dataframe
    pass

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


def add_price_to_inv_df(bd: BrickData, inv_df: pd.DataFrame, price_df, guide=GuideType.stock, )->pd.DataFrame:
    # for each row in inventory, _get price summary and add itadd prices

    def get_prices_for_row(row):
        pass


    pass






