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
import shelve
from urllib.parse import urlencode

import requests
from requests_oauthlib import OAuth1
from uritemplate import URITemplate

from pybcm.config import BCMConfig
from pybcm.const import ItemType, GuideType, Vats, Region, NewUsed
from pybcm.legoutils import legoColors

logger = logging.getLogger(__name__)


API_PATH = {

    "base": 'https://api.bricklink.com/api/store/v1',
    # item interface
    "get_item": '/items/{type}/{no}',
    "get_item_image": '/items/{type}/{no}/images/{color_id}',
    "get_supersets": '/items/{type}/{no}/supersets',
    "get_subsets": '/items/{type}/{no}/subsets',
    "get_priceguide": '/items/{type}/{no}/price',
    "get_known_colors": '/items/{type}/{no}/colors',
    # color interface
    "get_all_colors": '/colors',
    "get_color": '/colors/{color_id}',
    # category interface
    "get_category_list": '/categories',
    "get_category": '/categories/{category_id}',


}


class RestException(Exception):
    pass


def build_uri_template(url_key: str) -> URITemplate:
    """Build a URI template using the url_key and constants from the API definition found
    in const.py
    """
    _skeleton = ''.join([API_PATH['base'], API_PATH[url_key]])
    _template = URITemplate(_skeleton)
    return _template


def memoize_rc(func):
    """Used for wrapping functions in the RestClient class that take the arguments
        itemid, itemtypeid, colorid, new_or_used, guide_type, vat, region
    """
    shelf_file = '/Users/Keith/Projects/pybcm_proj/resources/rccache'

    def wrapper(*args, **kwargs):

        key = '_'.join([func.__name__, *args[1:], *kwargs.values()])

        with shelve.open(shelf_file) as shelf:
            if key in shelf:
                # if key in shelf and it's not too old
                logger.debug(f"Retrieving <{func.__name__}, {args}, {kwargs}> from Shelf")
                data = shelf[key]
                return data

            else:
                # call the function and cache
                logger.debug(f"Caching <{func.__name__}, {args}, {kwargs}> to Shelf")
                data = func(*args, **kwargs)
                shelf[key] = data
                return data

    return wrapper


class RestClient:
    """Rest Client for Bricklink website"""

    def __init__(self, config: BCMConfig):
        self.__consumer_key = config.consumer_key
        self.__consumer_secret = config.consumer_secret
        self.__token_key = config.token_key
        self.__token_secret = config.token_secret

        self.auth = OAuth1(self.__consumer_key, self.__consumer_secret, self.__token_key, self.__token_secret)

    @staticmethod
    def __validate(itemid: str = None,
                   itemtype: str = None,
                   color: int = None,
                   vat: str = None,
                   region: str = None,
                   new_or_used: str = None,
                   guide_type: str = None)->bool:
        """
        Validate some of the identities used in the Bricklink REST api. Items are optional
        passing on the ones to validate. Errors are raised on invalid.
        """
        # todo: add better validation for itemid
        if itemid is None:
            raise ValueError(f"Item Id is not valid.")

        if new_or_used is not None and new_or_used not in NewUsed:
            raise ValueError(f"New or Used {new_or_used} is not valid")

        if color is not None and int(color) not in legoColors:
            raise ValueError(f"Color {color} is not a valid color")

        if itemtype is not None and itemtype not in ItemType:
            raise ValueError(f"Item Type {itemtype} is not valid")

        if guide_type is not None and guide_type not in GuideType:
            raise ValueError(f"Guide type {guide_type} is not valid")

        if vat is not None and vat not in Vats:
            raise ValueError(f"Vat type {vat} is not valid")

        if region is not None and region not in Region:
            raise ValueError(f"Region {region} is not valid")

        return True

    def _get(self, url: str) -> requests.Response:
        """Create request and _get it for the passed url
        :param url: URL to retrieve
        :return response: The response
        """
        # todo: do some error checking here
        if url.startswith(API_PATH['base']):
            try:
                # logger.debug(f"RestClient._get(): {url}") # log in calling function
                response = requests.get(url, auth=self.auth)
                rest_code = response.json()['meta']['code']
                if rest_code not in [200, 201, 204]:
                    raise RestException(f"REST API Error: {rest_code}. {response.content}")
            except RestException as e:
                logger.error(e)
                return None
            return response
        else:
            raise ValueError(f"URL is invalid: {url}")

    def _get_data(self, url: str)->dict:
        """
        Get data from rest response @ url
        :param url:
        :return:
        """
        data = None
        resp = self._get(url)
        if resp:
            data = resp.json()['data']
        return data

    @memoize_rc
    def get_item(self, itemid: str, itemtypeid: str):
        """
        /items/{type}/{no}
        (see Bricklink API)
        """
        self.__validate(itemid=itemid, itemtype=itemtypeid)
        url = build_uri_template('get_item').expand(type=itemtypeid, no=itemid)
        logger.info("Getting Item from: {}".format(url))

        data = self._get_data(url)
        return data

    def get_item_image(self, itemid: str, itemtypeid: str, colorid: int):
        """
        /items/{type}/{no}
        (see Bricklink API)
        """
        self.__validate(itemid=itemid, itemtype=itemtypeid, color=colorid)
        url = build_uri_template('get_item_image').expand(type=itemtypeid, no=itemid, color_id=colorid)
        logger.info("Getting image from: {}".format(url))
        data = self._get_data(url)
        return data

    def get_supersets(self, itemid: str, itemtypeid: str)->dict:
        """
        /items/{type}/{no}/supersets
        (see Bricklink API)
        """
        self.__validate(itemid=itemid, itemtype=itemtypeid)
        url = build_uri_template('get_supersets').expand(type=itemtypeid, no=itemid)
        logger.info("Getting supersets: {}".format(url))
        data = self._get_data(url)
        return data

    @memoize_rc
    def get_subsets(self, itemid: str, itemtypeid: str)->list:
        """
        This is used to _get a set inventory
        /items/{type}/{no}/subsets
        (see Bricklink API)
        """
        self.__validate(itemid=itemid, itemtype=itemtypeid)
        url = build_uri_template('get_subsets').expand(type=itemtypeid, no=itemid)
        logger.info("Getting subsets: {}".format(url))
        data = self._get_data(url)
        return data

    @memoize_rc
    def get_price_guide(self, itemid: str, itemtypeid: str, colorid: str, new_or_used: str=NewUsed.N,
                        guide_type: str=GuideType.sold, vat: str='N', region: str=Region.north_america)->dict:
        """
        /items/{type}/{no}/price
        :param itemid:
        :param itemtypeid:
        :param colorid:
        :param new_or_used: 'N' or 'U' from NewUsed
        :param guide_type: 'sold' or 'stock from Guidetype
        :param vat: 'Y' or 'N'
        :param region: region type from Region
        :return data: JSON formatted price data (see Bricklink API)
        """

        self.__validate(itemid=itemid, itemtype=itemtypeid, color=colorid, new_or_used=new_or_used, guide_type=guide_type)
        endpoint = build_uri_template('get_priceguide').expand(type=itemtypeid, no=itemid)
        params = {
            'color': str(colorid),
            'guide_type': guide_type,
            'new_or_used': new_or_used,
            # 'country_code': 'US',
            'region': region,
            # 'currency_code':,s
            'vat': vat
        }
        args = urlencode(params)
        url = '?'.join([endpoint, args])
        logger.debug("Get Price Guide: {}".format(url))
        try:
            response = self._get(url)
            data = response.json()['data']
        except KeyError:
            logger.info("Data not found for itemid {}".format(itemid))
            data = None
        return data

    def get_part_price_guide(self, itemid: str, colorid: int, new_or_used: str)->dict:
        """
        Get the price guide from the catalog
        /items/{type}/{no}/price
        :param itemid:
        :param colorid:
        :param new_or_used: 'N' or 'U'
        :return data: JSON-formatted price guide (see Bricklink API)
        """
        self.__validate(itemid=itemid, color=colorid, new_or_used=new_or_used)
        data = self.get_price_guide(itemid, ItemType.PART, colorid, new_or_used=new_or_used)
        return data

    def get_known_colors(self, itemid: str, itemtypeid: str)->dict:
        """
        http://apidev.bricklink.com/redmine/projects/bricklink-api/wiki/CatalogMethod#Get-Known-Colors

        Get the list of known colors for a given item
        /items/{type}/{no}/colors
        :param itemid:
        :param itemtypeid:
        :return data: JSON-formatted color list (see Bricklink API)
        """
        self.__validate(itemid=itemid, itemtype=itemtypeid)
        url = build_uri_template('get_known_colors').expand(type=itemtypeid, no=itemid)
        logger.info(f"Getting Known Colors: {url}")
        data = self._get_data(url)
        return data

    def get_all_colors(self)->dict:

        url = build_uri_template('get_all_colors').expand()
        logger.debug(f"Getting complete list of colors: {url}")
        data = self._get(url)
        return data.json()['data']

    def get_category_list(self)->dict:
        url = build_uri_template('get_category_list').expand()
        logger.debug(f"Getting list of categories: {url}")
        data = self._get(url)
        return data.json()['data']


if __name__ == "__main__":
    logging.basicConfig(logging.INFO)
    pass
