import logging
import log
from brickpile import BrickPile
from mason import Mason
from config import BCMConfig
from wanted import WantedDict
from legoutils import Condition
import pandas as pd
import numpy as np

# get a wanted list
logger = log.setup_custom_logger('pybcm.test.brickpile')
#
config = BCMConfig('../config/bcm.ini')  # create the settings object and load the file
#
logger.info("Loading wanted dict")
wanted = WantedDict()
wanted.read(config.wantedfilename)
#
bp = BrickPile()
bp._wanted_dict = wanted
logger.info("Reading prices from pickle")
#bp.readpricesfromweb(wanted, Condition.NEW|Condition.USED)

pricefile = 'price.pickle'
#bp.price_to_pickle(pricefile)

bp.price_from_pickle(pricefile)
print(bp.summary())

logger.info(bp.df)
# mason = Mason(bp)
#df = mason._price

df = bp.df

# logger.info(df.xs('price', level=1, axis=1))
# print(df.xs('price', level=1, axis=1))

price_df = bp.price_frame
qty_df =  bp.qty_frame
# print(price_df)
# print(qty_df)

# print(price_df.mean(axis=1))
print("\n\n************ Element totals ************")
print(bp.element_totals)

print(bp.avg_prices)

# w = { wanted[element]:qty }