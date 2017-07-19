import log
from brickpile import BrickPile
from config import BCMConfig
from wanted import WantedDict

# get a wanted list
logger = log.setup_custom_logger('pybcm')
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

print(bp.price_frame)

print(bp.qty_frame)

print(bp.wanted_frame)

print("\n\n************ Element weights ************")
print(bp.weighted_price)

print(bp.price_quantiles())


# w = { wanted[element]:qty }