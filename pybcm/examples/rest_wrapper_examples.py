from pybcm.config import BCMConfig
from pybcm.rest_wrapper import RestWrapper

config = BCMConfig(r'../../config/bcm.ini')

rw = RestWrapper(config=config)

print(rw.get_known_colors('3020', 'PART'))

print(rw.get_part_priceguide_summary_df('3020', 'PART'))
