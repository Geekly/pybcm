'''
Created on Oct 26, 2012

@author: khooks
'''

from lxml import etree

import re
import io

import http.cookiejar
import urllib
from urllib.error import HTTPError, URLError
import logging

class BricklinkReader(object):
    '''
    The BricklinkReader will read the information about a single Bricklink Item from the Price Catalog
    the color and type are not handled except in the URL of the webreader, which are passed in.
    '''
    vendormap = dict()
    
    def __init__(self):
        """ Start up..."""
        

    def getStoreElements(self, datatree):
        #print(etree.tostring(datatree))        
        topparents = datatree.xpath("//td[table/tr/td/font/b[text()[contains(.,'Currently Available')]]]") #contains all the info we want

        currentroot = topparents[0]#this table contains the Currently Available text and all of the other information
        #drill down to the table containing store entry tr's
        stores = currentroot.xpath("./table/tr/td/table/tr[td/a]") #find all the rows that contain links
        #for store in stores:
            #print(etree.tostring(store))
              
        return stores  
    
    def readItemFromTree(self, datatree):
        prices = []   
        stores = self.getStoreElements(datatree) #all store tr's
        suLink = re.compile( "sID=(\d+).*itemID=(\d+)" )#\&itemID=(\d+)
        suStore = re.compile( "Store:.(.*)\".title")
        suPrice = re.compile("[US\$\s\~]") 
        for store in stores:
            #print(etree.tostring(store))
            td = store.xpath('./td')
            #td[0] contains the Store name
            linktext = etree.tostring(td[0]).decode()
            #print( linktext)
            storematch = re.search(suLink, linktext)
            if storematch:
                storeID = storematch.group(1)
                itemID = storematch.group(2)
                storenamematch = re.search(suStore, linktext)
                storename = storenamematch.group(1)
                #print("Storename: " + storename)
                BricklinkReader.vendormap[storeID] = storename
            #td[1] contains the Quantity
                quantity = td[1].text
            #td[3] contains the price
                pricestring = td[3].text
                price = re.sub(suPrice, '', pricestring)
                prices.append([itemID, storeID, quantity, price])
                #print([itemID, storeID, quantity, price])

        return prices  
               

class BricklinkWebReader(BricklinkReader):
    
    def __init__(self, login='', password=''):
        """ Start up..."""
        
        BricklinkReader.__init__(self)
        
        self.login = login
        self.password = password
        
        #self.blbrowser = twillbrowser()
        url = "https://www.bricklink.com/login.asp"
        self.blbrowser = SomeBrowser()
        self.blbrowser.login(url, self.login, self.password)
     
     
    def readitemfromurl(self, itemtypeID, itemID, itemColorID):
            
            #extract the info from the site and return it as a dictionary 
            # need to find and return itemID, storeID's, itemQty, itemPrice for each url
            # we also need to extract real vendor names during this search
            #returns prices[] =([itemid, vendorid, vendorqty, vendorprice)

            url = "http://www.bricklink.com/catalogPG.asp?itemType=" + itemtypeID + '&itemNo=' + itemID + '&itemSeq=1&colorID=' + itemColorID + '&v=P&priceGroup=Y&prDec=2'
                        
            prices = []
            page = self.blbrowser.open(url)
            parser = etree.HTMLParser(remove_blank_text=True, remove_comments=True, encoding='utf-8')      
            datatree = etree.HTML(page, parser)        
            prices = self.readItemFromTree(datatree)     
            return prices    
          
class BricklinkFileReader(BricklinkReader):
    ''' A Bricklink 'File' is a single html page in file format which represents a single part.  It's mainly for testing purposes.'''    
    def __init__(self):       
        BricklinkReader.__init__(self)
        
        #page is androgenous
    def readItemFromFile(self, filename):
        prices = []        
        parser = etree.HTMLParser(remove_blank_text=True, remove_comments=True, encoding='utf-8')      
        with io.open(filename, 'r') as f:     
            #print( "Parsing item from file..." )
            datatree = etree.HTML(f.read(), parser)
            #print( etree.tostring(datatree))
        prices = self.readItemFromTree(datatree)
        return prices
        

class SomeBrowser:

    def __init__(self):
        
        self.url = ''
        self.response = ''
        self.data = ''
        self.cookies = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPRedirectHandler(),
            urllib.request.HTTPSHandler(debuglevel=0),
            urllib.request.HTTPCookieProcessor(self.cookies))
            
    def open(self, url):
        try:
            self.url = url          
            req = urllib.request.Request(self.url)
            response = self.opener.open(req)
            #response = urllib.request.urlopen(req)            
            the_page = response.read()
            logging.debug("Opening URL:" + url)
        except HTTPError as e:
            logging.debug("Http Error: ", e.code, url)
        except URLError as e:
            logging.debug("URL Error:", e.reason, url)        
        
        return the_page
    
    def login(self, url, loginName, passwd):
        
        try:            
            self.url = url
            values = {
                       'a':'a',
                       'logFrmFlag':'Y',
                       'frmUserName' : loginName,
                       'frmPassword' : passwd }
    
            data = urllib.parse.urlencode(values).encode('utf-8')           
            req = urllib.request.Request(url, data, method='POST')
            response = self.opener.open(req)
            the_page = response.read().decode('utf-8')

        except HTTPError as e:
            logging.debug("Http Error: ", e.code, url)
        except URLError as e:
            logging.debug("URL Error:", e.reason, url)
        return the_page
                
        
#def remove_accents(input_str):
    
    #nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    #return u"".join([c for c in nkfd_form if not unicodedata.combining(c)]) 

        
if __name__ == '__main__':
    #filename = "../BrickLink Price Guide - Part 3070b in Black Color.htm"
    #prices = BricklinkFileReader(filename)
    #print prices.readAllItems() 
    
    logging.basicConfig(level=logging.DEBUG)
    logging.info('Started')
    
    br = BricklinkWebReader("Geekly", "codybricks")
    
    br.readitemfromurl('P', '3001', '80')
    br.readitemfromurl('P', '3001', '80')
    br.readitemfromurl('P', '3001', '80')
    
    
    #bfr = BricklinkFileReader()
    #bfr.readItemFromFile("../BrickLink Price Guide - Part 3001 in Dark Green Color.htm")

    
    logging.info('Done!')    
        