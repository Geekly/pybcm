'''
Created on Feb 6, 2013

@author: khooks
'''

import io
#import twill.commands
import http.cookiejar
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError
import logging



class SomeBrowser:

    def __init__(self):
        
        self.url = ''
        self.response = ''
        self.data = ''
        self.cookies = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
                urllib.request.HTTPRedirectHandler(),
                urllib.request.HTTPHandler(debuglevel=0),
                urllib.request.HTTPSHandler(debuglevel=0),
                urllib.request.HTTPCookieProcessor(self.cookies))
        
    
    def open(self, url):
        try:
            self.url = url
           
            req = urllib.request.Request(self.url)
            #response = urllib.request.urlopen(req)
            response = self.opener.open(req)
            #the_page = response.read().decode('utf-8')
            the_page = response.read()
            
        except HTTPError as e:
            logging.debug("Http Error: ", e.code, url)
        except URLError as e:
            logging.debug("URL Error:", e.reason, url)        
        
        return the_page
    

    def login(self, url, loginName, passwd):
        
        try:            
            self.url = url
            values = { 
                       'frmUserName' : loginName,
                       'frmPassword' : passwd }
    
            data = urllib.parse.urlencode(values).encode('utf-8')
            logging.debug(data)
            req = urllib.request.Request(url, data, method='POST')
            
            logging.info("This is the request")
            logging.debug(req.get_full_url())
            logging.debug(req.data)
   
            the_page = ""
            #response = urllib.request.urlopen(req)
            response = self.opener.open(req)
            logging.debug(response)
            the_page = response.read()
            #the_page = response.read().decode('utf-8')
            #http_headers = response.info()
            logging.debug(the_page)
        except HTTPError as e:
            logging.debug("Http Error: ", e.code, url)
        except URLError as e:
            logging.debug("URL Error:", e.reason, url)
        return the_page
    
    
 
if __name__ == '__main__':    
    logging.basicConfig(level=logging.DEBUG)
    loginurl = "https://www.bricklink.com/login.asp"
    guideurl = 'http://www.bricklink.com/catalogPG.asp?P=3460&colorID=86'
    
    browser = SomeBrowser()
    response = browser.login(loginurl, 'Geekly', 'codybricks')
    
    response = browser.open(guideurl)
    #response = browser.login(url = "https://www.bricklink.com/login.asp", loginName="Geekly", passwd="codybricks")
    f = open ('logintest.html', 'w')
    s = str(response)
    f.write(s)
    print(s)
    
    print("Done!")
    
    