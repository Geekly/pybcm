import log
from config import BCMConfig
from trowel import Trowel

# get a wanted list
logger = log.setup_custom_logger("pybcm")

config = BCMConfig('../config/bcm.ini')  # create the settings object and load the file

tr = Trowel(config)


def estimate_set_prices(set_name=None):
    inv = tr.get_set_inv(set_name)
    prices = tr.get_inv_prices_df(inv)
    #tr.add_prices_to_store(prices)
    cost = tr.estimate_inv_cost(prices)
    logger.info("Estimated cost of set {} is {}".format(set_name, cost))

# theset = '3219-1'
# estimate_set_prices(theset)
# #inv = tr.get_set_inv(theset)  # JSON-formatted inventory
# # #pprint(tr.get_set_inv(theset))
# # prices = tr.get_inv_prices_df(inv)
# #tr.add_prices_to_store(prices)
# #
# # #cost = tr.estimate_inv_cost(prices)
# # logger.info("Estimated cost of set {} is {}".format(theset, cost))
#
# # calculate the average prices
#
# # w = { wanted[element]:qty }
# #

# estimate_set_prices('3219-1')
# estimate_set_prices('75146-16')
estimate_set_prices('75083-1')
