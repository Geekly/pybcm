from config import BCMConfig
from brickbrowser import *

import log

#logger = log.setup_custom_logger('root')
# Override logging level
##ogger.setLevel(logging.DEBUG)
#logger.debug('Begin TestBrickBrowser.py')

config = BCMConfig('../config/bcm.ini')
logger.debug(dict(username=config.username, password=config.password))
b = BrickBrowser(config.username, config.password)
b.login()
the_page = b.open('https://www.bricklink.com/catalogPG.asp?itemType=P&itemNo=3004&itemSeq=1&colorID=85&v=P&priceGroup=Y&prDec=2')

print(the_page)

