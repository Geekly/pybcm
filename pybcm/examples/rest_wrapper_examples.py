from pybcm.brick_data import BrickData
from pybcm.config import BCMConfig

config = BCMConfig(r'../../config/bcm.ini')

rw = BrickData(config=config)

print(rw.get_known_colors('3020', 'PART'))

print(rw.get_part_price_summary('3020', 'PART'))
