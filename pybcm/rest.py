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

logger = logging.getLogger('pybcm.rest')


class RestClient():

    BASE_URL = 'https://api.bricklink.com/api/store/v1/'

    def __init__(self, config=BCMConfig('../config/bcm.ini')):

        __consumer_key = config.consumer_key
        __consumer_secret = config.consumer_secret
        __token_key = config.token_key
        __token_secret = config.token_secret

        self.auth = OAuth1(__consumer_key, __consumer_secret, __token_key, __token_secret)

    def get(self, url):
        return requests.get(url, auth=self.auth)

    __item_url = ''.join([BASE_URL, 'items/{type}/{no}'])
    __item_url_template = URITemplate(__item_url)

    def get_item(self, itemid, itemtypeid):
        """
        /items/{type}/{no}
        """
        url = self.__item_url_template.expand(type=itemtypeid, no=itemid)
        logger.debug("Getting Item from: {}".format(url))
        return self.get(url).json()['data']

    __item_image_url = ''.join([BASE_URL, 'items/{type}/{no}'])
    __item_image_url_template = URITemplate(__item_image_url)

    def get_item_image(self, itemid, itemtypeid):
        """
        /items/{type}/{no}
        """
        url = self.__item_image_url_template.expand(type=itemtypeid, no=itemid)
        logger.debug("Getting Known Colors from: {}".format(url))
        return self.get(url).json()['data']

    def get_supersets(self):
        raise NotImplemented("Not written yet")

    __subsets_url = ''.join([BASE_URL, 'items/{type}/{no}/subsets'])
    __subsets_url_template = URITemplate(__subsets_url)

    def get_subsets(self, itemid, itemtypeid):
        """
        /items/{type}/{no}/subsets
        """
        url = self.__subsets_url_template.expand(type=itemtypeid, no=itemid)
        logger.debug("Getting Known Colors from: {}".format(url))
        return self.get(url).json()['data']

    __price_guide_url = ''.join([BASE_URL, 'items/{type}/{no}/price'])
    __price_guide_url_template = URITemplate(__price_guide_url)

    def get_price_guide(self, itemid, itemtypeid, colorid, new_or_used='U', guide_type='sold'):

        endpoint = self.__price_guide_url_template.expand(type=itemtypeid, no=itemid)
        params = {
            'color': colorid,
            'guide_type': guide_type,
            'new_or_used': new_or_used,
            # 'country_code': 'US',
            'region': 'north_america',
            # 'currency_code':,
            'vat': 'N'
        }
        args = urlencode(params)
        url = '?'.join([endpoint, args])
        logger.debug("Getting Price Guide from: {}".format(url))
        try:
            response = self.get(url)
            data = response.json()['data']
        except KeyError:
            logger.info("Data not found for itemid {}".format(itemid))
            data = None
        return colorid, data

    __known_colors_url = ''.join([BASE_URL, 'items/{type}/{no}/colors'])
    __known_colors_url_template = URITemplate(__known_colors_url)

    def get_known_colors(self, itemid, itemtypeid):
        """
            GET	/items/{type}/{no}/colors
        """
        url = self.__known_colors_url_template.expand(type=itemtypeid, no=itemid)
        logger.debug("Getting Known Colors from: {}".format(url))
        return self.get(url).json()['data']

if __name__ == "__main__":
    logger = log.setup_custom_logger('pybcm')
    pass
