"""
Created on Jun 6, 2013

@author: khooks
"""

from ConfigParser import SafeConfigParser


class BCMConfig():
    """ Reads configuration information from bcm.ini.

        Args:
            username (str): bricklink username
            password (str): bricklink password
            wantedfilename (str): path of the wanted list
            pricefilename (str): path of the previously scrubbed price list
            reloadpricesfromweb (bool): if true, download and parse all of the price data again and save it to
                pricefilename.

            _parser (SafeConfigParser): parser that reads the config file
            _configfile (str): relative path of the config file
    """

    def __init__(self):
        #  _parser = SafeConfigParser()
        self._configfile = '../bcm.ini'
        self._parser = SafeConfigParser()

        self._parser.read(self._configfile)
        self.username = self._parser.get('bricklink', 'username')
        self.password = self._parser.get('bricklink', 'password')
        self.wantedfilename = self._parser.get('filenames', 'wanted')
        self.pricefilename = self._parser.get('filenames', 'prices')
        self.reloadpricesfromweb = self._parser.get('options', 'reloadpricesfromweb')


if __name__ == '__main__':
    config = BCMConfig()
    open(config.wantedfilename, 'r')

    wanted = '../Sampledata/Star Destroyer 30056-1.bsx'
    open(wanted, 'r')

    print config.pricefilename
    print config.reloadpricesfromweb
    print config._parser.items('filenames')
    print config._parser.items('options')
    print config._parser.items('bricklink')