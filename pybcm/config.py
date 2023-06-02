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
import os
# import pybcm.log
from configparser import RawConfigParser

logger = logging.getLogger(__name__)


class BCMConfig:
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
        print(f"Initializing {__class__} {configFileName}")
        #self._configfile = configFileName    # '../config/bcm.ini'
        self.__parser = RawConfigParser()
        self._configfile = os.path.abspath(configFileName)

        self.__parser.read(self._configfile)
        if len(self.__parser.sections()) == 0:
            raise(ValueError("Config file not found: " + self._configfile))
        else:
            if self.__parser.has_section('bricklink'):
                self.username = self.__parser.get('bricklink', 'username')
                self.password = self.__parser.get('bricklink', 'password')
                self.consumer_key = self.__parser.get('bricklink', 'consumer_key')
                self.consumer_secret = self.__parser.get('bricklink', 'consumer_secret')
                self.token_key = self.__parser.get('bricklink', 'token_key')
                self.token_secret = self.__parser.get('bricklink', 'token_secret')
            else:
                raise(ValueError("Bricklink section must be configured."))

        #TODO: handle when these sections/values are missing
            if self.__parser.has_section('filenames'):
                self.wantedfilename = self.__parser.get('filenames', 'wanted', fallback=None)
                self.pricefilename = self.__parser.get('filenames', 'prices', fallback=None)
            else:
                self.wantedfilename = None
                self.pricefilename = "../default_prices.xml"


            if self.__parser.has_section('options'):
                self.reloadpricesfromweb = self.__parser.getboolean('options', 'reloadpricesfromweb', fallback=True)
            else:
                self.reloadpricesfromweb = True

    def __str__(self):
        return f"Configured: {__class__} {self._configfile}"

    def __repr__(self):
        class_name = self.__class__.__name__
        attributes = vars(self)
        attribute_str = ', '.join(f'{key}={value}' for key, value in attributes.items())
        return f'{class_name}({attribute_str})'



if __name__ == '__main__':
    #log.setup_custom_logger('pybcm.config')
    config = BCMConfig('../config/bcm.ini')

    print(config.pricefilename)
    print(config.reloadpricesfromweb)




