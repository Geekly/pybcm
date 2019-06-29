from config import BCMConfig
from deprecated import log
from deprecated.brickpile import BrickPile
from legoutils import Condition
from wanted import WantedDict

# _get a wanted list
logger = log.setup_custom_logger('pybcm')
#
config = BCMConfig('../config/bcm.ini')  # create the settings object and load the file
#

update_cache = True

logger.info("Loading wanted dict")
wanted = WantedDict(WantedDict.wantedTypes.BL)
bl_list = '../Sampledata/10030 Star Destroyer.xml'
wanted.read(bl_list)
#
bp = BrickPile()


pricefile = 'price.pickle'
if update_cache:
    logger.info("Reading prices from web")
    bp.readpricesfromweb(wanted, Condition.NEW|Condition.USED)
    bp.price_to_pickle(pricefile)

else:
    logger.info("Reading prices from pickle")
    bp._wanted_dict = wanted
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