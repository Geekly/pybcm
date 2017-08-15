from pprint import pprint

from dataframe import rest_wrapper

pc = rest_wrapper('../config/bcm.ini')

pprint(pc.get_part_priceguide__summary_df('3006', 68, 'N'))
pprint(pc.get_priceguide_summary_df('3006', 'PART', 68, 'stock'))
