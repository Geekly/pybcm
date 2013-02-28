'''
Created on Oct 26, 2012

@author: khooks
'''
from bs4 import BeautifulSoup as Soup
import re
import io
import twill.commands
import unicodedata

class BricklinkReader(object):
    
    def __init__(self, login='', password=''):
        """ Start up..."""

class BricklinkWebReader(BricklinkReader):
    
    def __init__(self, login='', password=''):
        """ Start up..."""
        
        BricklinkReader.__init__(self)
        
        self.login = login
        self.password = password
        
        self.blbrowser = browser()
        self.loginToBricklink()
        
        

    def loginToBricklink(self):
        self.blbrowser.bricklink(self.login, self.password)
      
    def readitemfromurl(self, itemtypeID, itemID, itemColorID):
            
            #extract the info from the site and return it as a dictionary 
            # need to find and return itemID, storeID's, itemQty, itemPrice for each url
            # we also need to extract real vendor names during this search
        
        #    returns [][vendorid, vendorqty, vendorprice]
        
            url = "http://www.bricklink.com/catalogPG.asp?itemType=" + itemtypeID + '&itemNo=' + itemID + '&itemSeq=1&colorID=' + itemColorID + '&v=P&priceGroup=Y&prDec=2'
            #savedpriceguide = '../BrickLink Price Guide - Part 3460 in Dark Bluish Gray Color.htm'
            
            prices = []
            vendorqty = 0.0
            vendorprice = 0.0
            
            
            self.blbrowser.b.go(url)           
            response = self.blbrowser.b.get_html()
                          

            print "Parsing HTTP Response from " + url
            
            s = Soup(response, "lxml", from_encoding="utf-8")
            print "Finished converting to a Soup, now Finding All <A> tags"
                      
            su = re.compile( "store.asp\?sID=(\d+)\&itemID=(\d+)" )  #this matches the correct store link 
      
            
            #find a row that contains a href matching /store.asp?sID=310960&itemID=33779516"
    #        pricetable = s.find('b', "Currently Available")
            
            currentlyavailable = s.find('td', {})
            
            storelinks = s.find_all('a', {'href' : su } )   #grab a list of all <a> tags that include a matching href
                      
            print "Converted to a Soup.  Now extracting price info for vendors"
                       
            for store in storelinks:
        #        print store['href']
        
                #find the href tags within the store <a> and extract the vendorid
                m = su.search(store['href'])       
                vendorid = m.group(1)  
                vendorfulltext = store.img['alt']
                vendorname = re.sub( "Store: ", "", vendorfulltext)#.encode('utf-8')  #this fixed an issue with foreign characters
                
                vendorname = remove_accents(vendorname)
                    
                td = store.parent.parent.findAll('td')  #this gets us to the <TR> containing all of the goodies
    
                vendorqty = int( td[1].string )
                
                pricestring = td[3].string
                
                
                
                #if re.match('US', pricestring):
                    #print "We matched!"
                if re.search('US', pricestring): #this is a us dollar price
                    #print "Matched " + pricestring
                    vendorprice = float( re.sub('[US\$\s\~]', '', pricestring) )     #strips the US, whitespace and $ from the price            
                    prices.append([vendorid, vendorname, vendorqty, vendorprice])
         
            return prices      

class BricklinkFileReader(BricklinkReader):
    
    def __init__(self, filename):
        
        BricklinkReader.__init__(self)
        self.filename = filename
        
        
    def readAllItems(self):
        
        filename = self.filename       
        prices = []
        vendorqty = 0.0
        vendorprice = 0.0
        
        with io.open(filename, 'r') as f:     
            print "Parsing item from file..."
            s = Soup(f, "lxml", from_encoding="utf-8")
        
        with io.open("pricefromfile.txt", mode='w', encoding='utf-8') as file:
            file.write( s.prettify() )

        
        print "Finished converting to a Soup, now Finding All <A> tags"
        
        su = re.compile( "store.asp\?sID=(\d+)\&itemID=(\d+)" )  #this matches the correct store link 
  
        print s.find('td', "")
        
        #find a row that contains a href matching /store.asp?sID=310960&itemID=33779516"
#        pricetable = s.find('b', "Currently Available")
        storelinks = s.find_all('a', {'href' : su } )   #grab a list of all <a> tags that include a matching href
                  
        print "Converted to a Soup.  Now extracting price info for vendors"
        
        for store in storelinks:
    #        print store['href']
    
            #find the href tags within the store <a> and extract the vendorid
            m = su.search(store['href'])       
            vendorid = m.group(1)  
            vendorfulltext = store.img['alt']
            vendorname = re.sub( "Store: ", "", vendorfulltext).encode('utf-8')  #this fixed an issue with foreign characters
            vendorname = remove_accents(vendorname)
                
            td = store.parent.parent.findAll('td')  #this gets us to the <TR> containing all of the goodies

            vendorqty = int( td[1].string )
            vendorprice = float( re.sub('[US\$\s\~]', '', td[2].string) )     #strips the US, whitespace and $ from the price
    
            prices.append([vendorid, vendorname, vendorqty, vendorprice])
     
        return prices     


class browser:
    
    def __init__(self, url="https://www.bricklink.com/login.asp"):
        self.a=twill.commands
        self.a.config("readonly_controls_writeable", 1)
        self.b = self.a.get_browser()
        self.b.set_agent_string("Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14")
        self.b.clear_cookies()
        self.url=url
        
    def bricklink(self, loginName, passwd):
        self.b.go(self.url)
        f = self.b.get_form("3")
        f["frmUsername"] = loginName
        f["frmPassword"] = passwd 
                
        #self.b.showforms()
        self.b.clicked(f, "Login to Bricklink")
        self.b.submit()
        


def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)]) 

        
if __name__ == '__main__':
    #filename = "../BrickLink Price Guide - Part 3070b in Black Color.htm"
    #prices = BricklinkReader.readitemfromfile(filename)
    #print prices  
    
    br = BricklinkWebReader("Geekly", "codybricks")
    
    br.readitemfromurl('P', '3001', '80')
    
    bfr = BricklinkFileReader("../bricklink.xml")
    bfr.readAllItems()

    print "Done!"
    
        