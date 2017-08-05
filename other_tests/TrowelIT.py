import logging
import log

from trowel import Trowel
from config import BCMConfig

# get a wanted list
logger = log.setup_custom_logger(__name__)#.getLogger() #.setup_custom_logger('pybcm')
#logger.setLevel(logging.INFO)
#
config = BCMConfig('../config/bcm.ini')  # create the settings object and load the file
#

tr = Trowel(config)

theset = '3219-1'
inv = tr.get_set_inv(theset)
#pprint(tr.get_set_inv(theset))
prices = tr.get_inv_prices(inv)
tr.add_prices_to_store(prices)

cost = tr.estimate_inv_cost(prices)
logger.info("Estimated cost of set {} is {}".format(theset, cost))

# calculate the average prices

# w = { wanted[element]:qty }
#
theotherset = '30056-1'
inv = tr.get_set_inv(theotherset)
#pprint(inv)
prices = tr.get_inv_prices(inv)
tr.add_prices_to_store(prices)
cost = tr.estimate_inv_cost(prices)
logger.info("Estimated cost of set {} is {}".format(theotherset, cost))