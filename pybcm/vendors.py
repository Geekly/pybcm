'''
Created on Oct 23, 2012

@author: khooks
'''
from UserDict import UserDict
from bs4 import BeautifulSoup as Soup

class Vendor(object):
    
    def __init__(self, id, name):
        self.id = id
        self.name = name

class VendorMap(UserDict):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
                
        UserDict.__init__(self)
        self.data = dict()
              
        #print self.data
        
    def __str__(self):
        
        return self.toXML()
        '''    returnstring = "Vendor, Item, Color, Vendor Qty, Cost\n"
        
                for vendor in self.data.keys():
                for items in self.data[vendor]:
                returnstring += str(items) + "\n"'''
                               
    def addvendor(self, vendorid, vendorname):
        if vendorid in self.keys():
            return False
        else:
            self[vendorid] = Vendor(vendorid, vendorname)  
            return True      
        
    def getvendorname(self, vendorid):
        return self[vendorid].name  
  
                           
    def read(self, filename=None):
        assert filename != None, "price List filename required"
        print "Building vendor map from file: " + filename
        self.data = dict()  #clear any existing data
        
        self.soup = Soup(open(filename).read(), "lxml")
        vendorlist = self.soup.findAll("vendor")
        
            # for each item node, recurse over each vendor node      
            
        for vendor in vendorlist:
            vendorid = vendor.find('vendorid').string
            vendorname = vendor.find('vendorname').string
            
            self[vendorid] = Vendor(vendorid, vendorname)
         
        # for now, just save and process the prices structure.  They contain the same data.
        return
    
    def toXML(self):
        
        xml_string = ''
        vendorkeys = self.keys()
        for vendorid in vendorkeys:
            xml_string += '<Vendor>\n'
            xml_string += ' <VendorID>{}</VendorID>\n'.format(vendorid)
            xml_string += ' <VendorName>{}</VendorName>\n'.format(self[vendorid].name)
            xml_string += '</Vendor>\n'
        return xml_string
    
#test code goes here    
if __name__ == '__main__':
    pass
    
    