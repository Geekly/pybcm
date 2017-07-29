import logging
import pprint

import numpy as np
import pandas as pd
from pandas import DataFrame

from brickpile import BrickPile
from legoutils import PriceTuple, Condition

logger = logging.getLogger('pybcm.test.testDataFrame')
pp = pprint.PrettyPrinter(indent=4)

# https://stackoverflow.com/questions/24290495/constructing-3d-pandas-dataframe


NEW = Condition.NEW
USED = Condition.USED

wanted = {
            '3004|20': 5,
            '4005|20': 12
        }


pricelist1 = [
    PriceTuple('3004|20', '214', 'Best Bricks', 0.05, 5, NEW),
    PriceTuple('3004|20', '214', 'Best Bricks', 0.02, 50, USED),
    PriceTuple('3004|20', '098', 'Brick Shithouse', 0.15, 15, NEW),
    PriceTuple('3004|20', '098', 'Brick Shithouse', 0.05, 25, USED),
]

pricelist2 = [
    PriceTuple('4005|20', '214', 'Best Bricks', 0.5, 25, NEW),
    PriceTuple('4005|20', '991', 'Nice Bricks', 0.25, 14, NEW),
    PriceTuple('4005|20', '107', 'Shitting Bricks', 0.03, 50, NEW),
    PriceTuple('4005|20', '215', 'Brick Sucker', 0.03, 50, NEW),
    PriceTuple('4005|20', '215', 'Brick Sucker', 0.53, 2, USED)
]


def dataframe_from_pricelist(element_id, price_list):
    stores = list(set([e.storeid for e in price_list]))
    data_shape = (2, len(stores))
    _data = np.array(data_shape)

    _data = {(d.storeid, param): d.__getattribute__(param) for d in price_list for param in ['price', 'qty']}
    print(_data)
    _index = pd.MultiIndex.from_product([[ '4005|20' ], ['New', 'Used']], names=['elementid', 'condition'])
    _df = DataFrame(_data, index=_index)
    #_df.rename_axis('elemfgfent', axis=1)
    return _df


def flatframe_from_pricelist(price_list):

    _data = [ p._asdict() for p in price_list]

    columns = ['elementid', 'condition', 'storeid', 'price', 'qty']
    _df = pd.DataFrame(_data, columns=columns)
    _df.set_index(['elementid', 'condition', 'storeid'], inplace=True)
    #_df = _df.unstack(level=-1).swaplevel(0, 1, 1)
    print(_df)
    return _df

bp = BrickPile()

    # def __init__(self):
    #
    #     self.df = DataFrame()  # price data
    #     self.vendormap = VendorMap()
    #     self._wanted_dict = None
    #     self._bricklink_initialized = False
    #     self._vendor_initialized = False
    #     logger.debug("BrickPile vendormap id: %s" % id(self.vendormap))
    #     self.webreader = ElementWebReader(self.vendormap)


df1 = dataframe_from_pricelist('3004|20', pricelist1)
df2 = dataframe_from_pricelist('4005|20', pricelist2)

df = pd.concat([df1, df2])

print("\nfd1")
fd1 = flatframe_from_pricelist(pricelist1)
print("\nfd2")
fd2 = flatframe_from_pricelist(pricelist2)
fd = pd.concat([fd1, fd2])

p = fd['price']
print("\naverage prices:\n %s" % p.mean(level=['elementid', 'condition']))

print("fd\n")
pp.pprint(fd)
pass

element_names = p.index