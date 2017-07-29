from pprint import pprint

from pandas_wrapper import PandasClient

pc = PandasClient('../config/bcm.ini')

pprint( pc.get_part_price_guide('3006', 68, 'N'))
pprint( pc.get_price_guide('3006', 'PART', 68, 'N', 'stock'))
