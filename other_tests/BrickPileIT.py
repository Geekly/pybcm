import logging
import log
from brickpile import BrickPile
from mason import Mason
from config import BCMConfig
from wanted import WantedDict
import pandas as pd
import numpy as np

# get a wanted list
logger = log.setup_custom_logger('root')
#
config = BCMConfig('../config/bcm.ini')  # create the settings object and load the file
#
logger.info("Loading wanted dict")
wanted = WantedDict()
wanted.read(config.wantedfilename)
#
bp = BrickPile()
bp.wanted = wanted
logger.info("Reading prices from pickle")
# bp.readpricesfromweb(wanted)

pricefile = 'price.pickle'
# bp.price_to_pickle(pricefile)

bp.price_from_pickle(pricefile)

mason = Mason(bp)
#df = mason._price

df = bp.df

#logger.info(df.xs('price', level=1, axis=1))
print(df.xs('price', level=1, axis=1))
print('nothin')

price_df = bp.price_frame
qty_df =  bp.qty_frame
print(price_df)
print(qty_df)

print(price_df.mean(axis=1))

s = pd.Series(wanted)
print(s)

w = { wanted[element]:qty }