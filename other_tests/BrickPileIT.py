import log
from brickpile import BrickPile
from config import BCMConfig
from wanted import WantedDict

# get a wanted list
logger = log.setup_custom_logger(__name__)

config = BCMConfig('../config/bcm.ini')  # create the settings object and load the file

logger.info("Loading wanted dict")
wanted = WantedDict()
wanted.read(config.wantedfilename)

bp = BrickPile()
logger.info("Reading prices from web")
bp.readpricesfromweb(wanted)

