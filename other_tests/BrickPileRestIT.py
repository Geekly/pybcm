import log
from brickpile import BrickPile
from config import BCMConfig
from legoutils import Condition
from wanted import WantedDict

# get a wanted list
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
    bp.readpricesfromrest(wanted, Condition.NEW|Condition.USED)
    #bp.price_to_pickle(pricefile)

else:
    logger.info("Reading prices from pickle")
    bp._wanted_dict = wanted
    bp.price_from_pickle(pricefile)

print(bp.summary())

print(bp.price_frame)

print(bp.qty_frame)

print(bp.wanted_frame)

print("\n\n************ Element weights ************")
print(bp.weighted_price)

print(bp.price_quantiles())


# w = { wanted[element]:qty }