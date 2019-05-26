
import logging

import pandas as pd

from pybcm.brick_data import BrickData
from pybcm.config import BCMConfig
from pybcm.const import *

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logging.getLogger('requests_oauthlib').setLevel(logging.WARNING)
logging.getLogger('oauthlib').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

config = BCMConfig('../../config/bcm.ini')  # create the settings object and load the file

bd = BrickData(config)

inv = bd.get_set_inventory('9492-1')[0:3]

price_summary = pd.DataFrame()

for index, row in inv.iterrows():
    if row['itemtype'] == ItemType.PART:
        lineitem = bd.get_part_price_summary(row['item_id'], row['color_id'],
                                             new_or_used=[NewUsed.N, NewUsed.U],
                                             guide_type=GuideType.sold)
        price_summary = price_summary.append(lineitem)
        lineitem = bd.get_part_price_summary(row['item_id'], row['color_id'],
                                             guide_type=GuideType.stock)
        price_summary = price_summary.append(lineitem)


print(price_summary)


