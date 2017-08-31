import logging
from pprint import pprint

import log
from config import BCMConfig
from trowel import Trowel

# get a wanted list
logger = log.setup_custom_logger("pybcm")
logger.setLevel(logging.INFO)
logging.getLogger("pybcm.trowel").setLevel(logging.WARNING)
#logging.getLogger("pybcm.rest").setLevel(logging.WARNING)

config = BCMConfig('../config/bcm.ini')  # create the settings object and load the file
tr = Trowel(config)

# set_summary('3219-1')
# set_summary('75146-16')
tr.set_summary('10182-1')
#tr.set_summary('10185-1')
sets = tr.price_sets(['10182-1', '10185-1', '10190-1', '10197-1', '10246-1', '10251-1', '10255-1'])
pprint(sets)
