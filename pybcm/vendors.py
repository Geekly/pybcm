'''
Created on Oct 23, 2012

@author: khooks
'''
from UserDict import UserDict
import BeautifulSoup as soup
import numpy as np

global vendorMap


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

vendorMap = VendorMap() 

    
class VendorStats():
    
    def __init__(self, bcmdata):
        self.data = bcmdata
        self.ELEMWEIGHTS = bcmdata.elementweights() #dictionary
        self.NUMVENDORS = len(self.data.vendorlist)
        self.NUMELEMS = len(self.data.elementlist)
        self.ITEMS = len(self.data.elementlist)
        self.ITEMSPERVENDOR = self.__itemspervendor()
        self.VENDORSPERELEMENT = self.__vendorsperelement()
        self.TOTALPERVENDOR = self.__totalitemspervendor()
        self.VDICT = self.__makedictionary()
    
    def update(self, bcmdata):
        self.data = bcmdata
        self.ELEMWEIGHTS = bcmdata.elementweights() #dictionary
        self.NUMVENDORS = len(self.data.vendorlist)
        self.NUMELEMS = len(self.data.elementlist)
        self.ITEMS = len(self.data.elementlist)
        self.ITEMSPERVENDOR = self.__itemspervendor()
        self.VENDORSPERELEMENT = self.__vendorsperelement()
        self.TOTALPERVENDOR = self.__totalitemspervendor()
        self.VDICT = self.__makedictionary()
        
    def __itemspervendor(self):
        s = self.data.STOCK
        itemspervendor = (s > 0).sum(0)
        return itemspervendor        
    
    def __totalitemspervendor(self):
        # for each vendor
        # sum the min( stock, wanted) for each element
        #vitems = np.zeros(shape=(self.NUMVENDORS), dtype='int')
        S = self.data.STOCK
        W = self.data.WANTED.reshape(len(self.data.elementlist), 1)
        vitems = np.minimum(S,W).sum(0)
        vitems.mask = S.mask
        #print(vitems)
        #print(np.minimum(S,W))
        #print(np.minimum(S,W).sum(0))
        #for vidx, stock in enumerate(S.T): #enumerate over the columns in STOCK
        #    for eidx, wanted in enumerate(W): #enumerate over each element in the wanted list
        #        vitems[vidx] += min( stock[eidx], wanted )
        return vitems
    
    def __vendorsperelement(self):
        s = self.data.STOCK
        vendorsperelement = ( s > 0).sum(1)
        return vendorsperelement
    
    def __stockbywanted(self):
        """  
        SBW = STOCK / WANTED
        SBW = 1.0 if STOCK/WANTED >= 1.0 ELSE STOCK/WANTED
        """
        S = self.data.STOCK.astype('float')
        W = self.data.WANTED.reshape(self.NUMELEMS, 1).astype('float')
        stockbywant = S/W
        greaterthan1 = stockbywant > 1.0
        stockbywant[greaterthan1] = 1.0
        return stockbywant
    
    def vendorstockweights(self):
        return 2.5 * self.__stockbywanted().sum(0)
    
    def vendorpriceweights(self):
        # function of element weight, vendor price, vendor qty (gets credit for how many it has)
        #sort by self.data.elementlist
        sortedweights = [self.ELEMWEIGHTS[element] for element in self.data.elementlist] #aligned with elementlist now
        #print(sortedweights)
        EWD = np.array(sortedweights, dtype='float').reshape((len(self.ELEMWEIGHTS),1))
        P = self.data.PRICES
        S = self.data.STOCK
        AVG = self.avgprices()
        #print(EWD)
        #print(P)
        
        priceweight = EWD/P
        #for vindex, vendor in enumerate(self.data.vendorlist):
        #    totalweight = 0
        #    for eindex, element in enumerate(self.data.elementlist):
        #        pricew = ewd[element]/p[eindex, vindex]
        #        totalweight += pricew  
        #    costweights[vindex] = totalweight
        #return costweights
        # define some weight based on elementweights and qty
        return priceweight
    
    def avgprices(self):
        #data[elementid, vendorid] = [price, qty]
        p = self.data.PRICES
        avgprices = p.sum(1)/(p > 0).sum(1) #the 1 causes
        return avgprices 
    
    def vendorweights(self):
        #Use nd arrays
        
        vendorstockweights = self.__stockbywanted().sum(0) * 2.5
        vendorpriceweights = self.vendorpriceweights().sum(0)
        
        print( vendorstockweights)
        print( vendorpriceweights)
        
    
    def __makedictionary(self):
        vdict = dict()
        avgprices = self.data.avgprices()
        for vindex, vendor in enumerate(self.data.vendorlist):
            vdict[vendor] = ( self.ITEMSPERVENDOR[vindex], self.TOTALPERVENDOR[vindex])
        return vdict    
    
               
        
    def report(self):
        print("There are %d items to purchase" % self.ITEMS)
        print("%d vendors have the following number distinct items available:" % self.NUMVENDORS)
        print("Vendors per element", self.ITEMSPERVENDOR)
        print("Elements per vendor", self.VENDORSPERELEMENT)
        print(self.VDICT)
        #vlist = self.data.vendorlist
#test code goes here    
if __name__ == '__main__':
    pass
    
    