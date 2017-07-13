"""
Created on Jun 6, 2013

@author: khooks
"""

from configparser import RawConfigParser

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

    def __init__(self, configFileName):
        #  _parser = SafeConfigParser()
        self._configfile = configFileName    # '../config/bcm.ini'
        self.__parser = RawConfigParser()

        _dataset = self.__parser.read(self._configfile)
        if ( len(_dataset) <= 0 ):
            raise(ValueError("Config file not found: " + self._configfile))

        self.username = self.__parser.get('bricklink', 'username')
        self.password = self.__parser.get('bricklink', 'password')
        self.wantedfilename = self.__parser.get('filenames', 'wanted')
        self.pricefilename = self.__parser.get('filenames', 'prices')
        self.reloadpricesfromweb = self.__parser.getboolean('options', 'reloadpricesfromweb')


if __name__ == '__main__':

    config = BCMConfig('../config/bcm.ini')

    print(config.pricefilename)
    print(config.reloadpricesfromweb)
    print(config.__parser.items('filenames'))
    print(config.__parser.items('options'))
    print(config.__parser.items('bricklink'))