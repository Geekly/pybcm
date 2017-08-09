from pprint import pprint

from blrest_wrapper import rest_wrapper

pc = rest_wrapper('../config/bcm.ini')

pprint(pc.get_part_price_guide_df('3006', 68, 'N'))
pprint(pc.get_priceguide_df('3006', 'PART', 68, 'stock'))
