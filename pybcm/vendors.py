'''
Created on Oct 23, 2012

@author: khooks
'''
from UserDict import UserDict
import BeautifulSoup as soup


class Vendor(object):
    
    def __init__(self, vendorid='', vendorname=''):
        self.id = vendorid
        self.name = vendorname
        
    def toXML(self):
        xmlstring = ''
        xmlstring += "<Vendor>\n"
        xmlstring += "<VendorID>" + str(self.id) + "</VendorID>\n"
        xmlstring += "<VendorName>" + str(self.name) + "</VendorName>\n"     
        xmlstring += "</Vendor>\n"
        return xmlstring
    
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
        self.soup = None      
        #print self.data
        
    def __str__(self):
        
        return self.toXML()
        '''    returnstring = "Vendor, Item, Color, Vendor Qty, Cost\n"
        
                for vendor in self.data.keys():
                for items in self.data[vendor]:
                returnstring += str(items) + "\n"
        '''
                               
    def addvendor(self, vendor):
        if vendor.id in self.data:
            return False
        else:
            #logging.debug("Adding vendor: " + vendor.name)
            self[vendor.id] = vendor.name
            return True      
    
    def getnumvendors(self):
        return len(self)
        
    def getvendorname(self, vendorid):
        if vendorid in self.keys():
            return self[vendorid] 
        else:
            pass 
    
#not sure this works                           
    def read(self, filename=None):
        assert filename != None, "price List filename required"
        print( "Building vendor map from file: " + filename)
        self.data = dict()  #clear any existing data
        
        self.soup = soup.soup( open(filename).read(), "lxml")
        vendorlist = self.soup.findAll("vendor")
        
            # for each item node, recurse over each vendor node      
            
        for vendor in vendorlist:
            vendorid = vendor.find('vendorid').string
            vendorname = vendor.find('vendorname').string
            
            self[vendorid] = vendorname
         
        # for now, just save and process the prices structure.  They contain the same data.
        return
#not sure this works    
    def toXML(self):
        
        xml_string = ''
        vendorkeys = self.keys()
        for vendorid in vendorkeys:
            vendorname = self[vendorid]
            xml_string += Vendor(vendorid, vendorname).toXML()
            '''
            xml_string += '<Vendor>\n'
            xml_string += ' <VendorID>{}</VendorID>\n'.format(vendorid)
            xml_string += ' <VendorName>{}</VendorName>\n'.format(self[vendorid])
            xml_string += '</Vendor>\n'
            '''
        return xml_string
    
#test code goes here    
if __name__ == '__main__':
    pass
    
    