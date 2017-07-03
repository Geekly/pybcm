import certifi
import requests
import http.cookiejar
from urllib.error import HTTPError, URLError
import logging

import log

logger = log.setup_custom_logger('root')
# Override logging level
logger.setLevel(logging.DEBUG)
logger.debug('Begin BrickBrowser.py')


class BrickBrowser:

    LOGIN_POST_URL = "https://www.bricklink.com/ajax/renovate/loginandout.ajax"
    USER_AGENT_DICT = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    def __init__(self, login_id, password):

        self.url = ''
        self.response = None
        self.data = {}
        self.headers = {}
        self.userid = login_id
        self.password = password
        self.cookies = http.cookiejar.CookieJar
        self.session = None
        self.logged_in = False
        self.default_headers = self.build_headers()
        self.login()

    def build_headers(self):
        self.default_headers = dict(**self.USER_AGENT_DICT)
        return self.default_headers

    def open(self, url):
        if (self.logged_in is False) or (self.session is None):
            # try to log in
            self.login()
        # check if that worked
        if (self.logged_in is True) and (self.session is not None):
            try:
                self.url = url
                response = self.session.get(self.url, headers=self.default_headers)
                # response = self.opener.open(req)
                # response = urllib.request.urlopen(req)
                the_page = response.content
                logging.debug("Opening URL:" + url)
                return the_page
            except HTTPError as e:
                logging.debug("Http Error: ", e.code, url)
            except URLError as e:
                logging.debug("URL Error:", e.reason, url)
        else:
            # try to log in
            logging.debug("Not logged in")
            raise ConnectionError("Cannot open %s. Not logged in" % url)

    def login(self):
        # if succesful, returns a logged-in Session

        payload = {
            "userid": self.userid,
            "password": self.password
        }

        try:

            self.session = requests.session()
            header_response = self.session.head("http://www.brinklink.com")
            if not (200 <= header_response.status_code <= 302):
                raise Exception("Error while getting header, code: %d" % header_response.status_code)

            self.session.verify = certifi.where()
            self.cookies = requests.utils.cookiejar_from_dict(requests.utils.dict_from_cookiejar(self.session.cookies))

            url = self.LOGIN_POST_URL
            self.response = self.session.post(
                url,
                data=payload,
                headers=self.default_headers
            )

            self.response

        except HTTPError as e:
            logging.debug("Http Error: ", e.code, url)
        except URLError as e:
            logging.debug("URL Error:", e.reason, url)

        if not 200 <= self.response.status_code < 300:
            raise ConnectionError("Error while logging in, code: %d" % self.response.status_code)

        self.logged_in = True

        return self.response

if __name__ == "__main__":
    from config import BCMConfig

    logger.info('testSomeBrowser.py started')

    #vendormap = VendorMap()

    config = BCMConfig('../config/bcm.ini')
    bb = BrickBrowser(config.username, config.password)
    bb.open('https://www.bricklink.com/catalogPG.asp?itemType=P&itemNo=3004&itemSeq=1&colorID=85&v=P&priceGroup=Y&prDec=2')

    pass
