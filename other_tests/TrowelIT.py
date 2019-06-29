import logging

from config import BCMConfig
from deprecated import log
from trowel import Trowel

# _get a wanted list
logger = log.setup_custom_logger("pybcm")
logger.setLevel(logging.INFO)
logging.getLogger("pybcm.trowel").setLevel(logging.WARNING)
#logging.getLogger("pybcm.rest").setLevel(logging.WARNING)

config = BCMConfig('../config/bcm.ini')  # create the settings object and load the file
tr = Trowel(config)

inv = tr.get_set_inv('76023-1')
price = tr.get_inv_prices_df(inv)
best = tr.best_prices(price)
print(price)
# set_summary('75146-16')
#tr.set_summary('10182-1')
#tr.set_summary('10185-1')
#sets = tr.price_sets(['10182-1', '10185-1', '10190-1', '10197-1', '10246-1', '10251-1', '10255-1'])
#pprint(sets)
