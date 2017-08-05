# Copyright (c) 2017, Keith Hooks
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

import logging
from urllib.parse import urlencode

import requests
from requests_oauthlib import OAuth1
from uritemplate import URITemplate

import log
from config import BCMConfig
from const import *

logger = logging.getLogger(__name__)


def build_uri_template(url_key):
    __skeleton = ''.join([API_PATH['base'], API_PATH[url_key]])
    __template = URITemplate(__skeleton)
    return __template


class RestClient:
    """Rest Client for Bricklink website"""

    def __init__(self, config=BCMConfig('../config/bcm.ini')):

        __consumer_key = config.consumer_key
        __consumer_secret = config.consumer_secret
        __token_key = config.token_key
        __token_secret = config.token_secret

        self.auth = OAuth1(__consumer_key, __consumer_secret, __token_key, __token_secret)

    def __validate(self, itemtype=None, color=None, guidetype=None):

        if itemtype is not None and itemtype not in ITEM_TYPES:
            raise ValueError("Item Type {} is not valid".format(itemtype))
        if guidetype is not None and guidetype not in GUIDE_TYPES:
            raise ValueError("Guide type {} is not valid".format(guidetype))
        if color is not None and color not in []:
            # TODO: make some color validation that doesn't require calling the Known Colors api
            pass

    def get(self, url):
        response = requests.get(url, auth=self.auth)
        return response

    def get_item(self, itemid, itemtypeid):
        """
        /items/{type}/{no}
        """
        self.__validate(itemtype=itemtypeid)
        url = build_uri_template('item').expand(type=itemtypeid, no=itemid)
        logger.info("Getting Item from: {}".format(url))
        return self.get(url).json()['data']

    def get_item_image(self, itemid, itemtypeid, color):
        """
        /items/{type}/{no}
        """
        self.__validate(itemtype=itemtypeid)
        url = build_uri_template('item_image').expand(type=itemtypeid, no=itemid, color_id=color)
        logger.info("Getting image from: {}".format(url))
        return self.get(url).json()['data']

    def get_supersets(self, itemid, itemtypeid):
        self.__validate(itemtype=itemtypeid)
        url = build_uri_template('supersets').expand(type=itemtypeid, no=itemid)
        logger.info("Getting supersets from: {}".format(url))
        return self.get(url).json()['data']

    def get_subsets(self, itemid, itemtypeid):
        """
        /items/{type}/{no}/subsets
        """
        self.__validate(itemtype=itemtypeid)
        url = build_uri_template('subsets').expand(type=itemtypeid, no=itemid)
        logger.info("Getting Known Colors from: {}".format(url))
        return self.get(url).json()['data']

    def get_price_guide(self, itemid, itemtypeid, colorid, new_or_used='U', guide_type='sold'):

        self.__validate(itemtype=itemtypeid, guidetype=guide_type)
        endpoint = build_uri_template('priceguide').expand(type=itemtypeid, no=itemid)
        params = {
            'color': str(colorid),
            'guide_type': str(guide_type),
            'new_or_used': str(new_or_used),
            # 'country_code': 'US',
            'region': 'north_america',
            # 'currency_code':,
            'vat': 'N'
        }
        args = urlencode(params)
        url = '?'.join([endpoint, args])
        logger.info("Getting Price Guide from: {}".format(url))
        try:
            response = self.get(url)
            data = response.json()['data']
        except KeyError:
            logger.info("Data not found for itemid {}".format(itemid))
            data = None
        return data

    def get_part_price_guide(self, itemid, colorid, new_or_used):
        self.__validate(color=colorid)
        data = self.get_price_guide(itemid, 'PART', colorid, new_or_used=new_or_used)
        return data

    def get_known_colors(self, itemid, itemtypeid):
        """
            GET	/items/{type}/{no}/colors
        """
        url = build_uri_template('known_colors').expand(type=itemtypeid, no=itemid)
        logger.debug("Getting Known Colors from: {}".format(url))
        return self.get(url).json()['data']


if __name__ == "__main__":
    logger = log.setup_custom_logger('pybcm')
    pass