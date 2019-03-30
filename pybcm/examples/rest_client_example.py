
from pybcm.config import BCMConfig
from pybcm.rest import RestClient
#from const import *


config = BCMConfig(r'../../config/bcm.ini')
print(config._configfile)
#print(config._configfile)

rc = RestClient(config)

print(rc.get_known_colors('3020', 'DOG'))

print(rc.get_item('3020', 'PART'))
print(rc.get_item('3020', 'SET'))
