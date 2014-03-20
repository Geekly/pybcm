"""
Created on Oct 23, 2012

@author: khooks
"""
from UserDict import UserDict

import numpy as np


#global vendorMap


class Vendor(object):
    
    def __init__(self, vendorid='', vendorname=''):
        self._id = vendorid
        self._name = vendorname

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    def toXML(self):
        xmlstring = ''
        xmlstring += "<Vendor>\n"
        xmlstring += "<VendorID>" + str(self._id) + "</VendorID>\n"
        xmlstring += "<VendorName>" + str(self._name) + "</VendorName>\n"
        xmlstring += "</Vendor>\n"
        return xmlstring


class VendorMap(UserDict):
    """
    Dict[vendor.id] = Vendor
    """
    def __init__(self):
        UserDict.__init__(self)
        self.data = dict()

    def __str__(self):
        return self.toXML()

    def addvendor(self, vendor):
        if vendor.id in self.data:
            return False
        else:
            #logging.debug("Adding vendor: " + vendor.name)
            self[vendor.id] = vendor  # assign the whole vendor object in case we add to it later
            return True      
    
    def getnumvendors(self):
        return len(self)
        
    def getvendorname(self, vendorid):
        if vendorid in self.keys():
            return self[vendorid].name
        else:
            return ''

#not sure this works                           
    # def read(self, filename=None):
    #     assert filename is not None, "price List filename required"
    #     print( "Building vendor map from file: " + filename)
    #     self.data = dict()  #clear any existing data
    #
    #     soup = Soup( open(filename).read(), "lxml")
    #     vendorlist = soup.findAll("vendor")
    #
    #         # for each item node, recurse over each vendor node
    #
    #     for vendor in vendorlist:
    #         vendorid = vendor.find('vendorid').string
    #         vendorname = vendor.find('vendorname').string
    #
    #         self[vendorid] = vendorname
    #
    #     # for now, just save and process the prices structure.  They contain the same data.
    #     return
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

#Expose a global vendormap
vendorMap = VendorMap() 
    
class VendorStats():
    
    def __init__(self, bcmdata):
        self.data = bcmdata
        self.ELEMWEIGHTS = bcmdata.elementweights() #numpy array
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
        itemspervendor = np.ndarray(s > 0).sum(0)
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
        vendorsperelement = np.ndarray(s > 0).sum(1)
        return vendorsperelement
    
    def stockbywanted(self):
        return self.__stockbywanted()
    
    def __stockbywanted(self):
        """  
        Calculates a sorting helper for vendors.  The more items a vendor can completely fill, the higher its
            value.
        SBW = STOCK / WANTED
        SBW = 1.0 if STOCK/WANTED >= 1.0 ELSE STOCK/WANTED
        """
        S = self.data.STOCK.astype('float')
        W = self.data.WANTED.reshape(self.NUMELEMS, 1).astype('float')
        stockbywant = S/W
        greaterthan1 = stockbywant >= 1.0 #creates a true/false array that will be used in the next line
        stockbywant[greaterthan1] = 2.0 #completely filling an order counts 3X more than a partial fill
        return stockbywant
    
    def vendorstockweights(self):
        return self.__stockbywanted().sum(0)
    
    def vendorpriceweights(self):
        # function of element weight, vendor price, vendor qty (gets credit for how many it has)
        #sort by self.data.elementlist
        sortedweights = self.ELEMWEIGHTS #aligned with elementlist now
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
        avgprices = p.sum(1) / np.ndarray(p > 0).sum(1) #the 1 causes
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
    
    