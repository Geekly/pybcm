# Copyright (c) 2013-2017, Keith Hooks
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Manage the module configuration settings
"""
import logging
import log
from configparser import RawConfigParser

logger = logging.getLogger('pybcm')


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
        if len(_dataset) <= 0:
            raise(ValueError("Config file not found: " + self._configfile))

        self.username = self.__parser.get('bricklink', 'username')
        self.password = self.__parser.get('bricklink', 'password')
        self.consumer_key = self.__parser.get('bricklink', 'consumer_key')
        self.consumer_secret = self.__parser.get('bricklink', 'consumer_secret')
        self.token_key = self.__parser.get('bricklink', 'token_key')
        self.token_secret = self.__parser.get('bricklink', 'token_secret')

        self.wantedfilename = self.__parser.get('filenames', 'wanted')
        self.pricefilename = self.__parser.get('filenames', 'prices')

        self.reloadpricesfromweb = self.__parser.getboolean('options', 'reloadpricesfromweb')



if __name__ == '__main__':
    log.setup_custom_logger('pybcm.config')
    config = BCMConfig('../config/bcm.ini')

    print(config.pricefilename)
    print(config.reloadpricesfromweb)




