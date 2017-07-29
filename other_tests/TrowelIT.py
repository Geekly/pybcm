from pprint import pprint

import log
from config import BCMConfig
from trowel import Trowel

# get a wanted list
logger = log.setup_custom_logger('pybcm')
#
config = BCMConfig('../config/bcm.ini')  # create the settings object and load the file
#

tr = Trowel(config)

theset = '3219-1'
inv = tr.get_set_inv(theset)
pprint(tr.get_set_inv(theset))
cost = tr.price_inv(inv)
pprint(cost)

# w = { wanted[element]:qty }