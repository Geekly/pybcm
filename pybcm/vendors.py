"""
Created on Oct 23, 2012

@author: khooks
"""
from collections import UserDict
import numpy as np


class Vendor(object):
    """Vendor represented by id and name and can be output to XML.
        Args:
            vendorid (str):  Bricklink id of the vendor
            vendorname (str):  Name of the vendor store
        Attributes:
            vendorid (str):  Bricklink id of the vendor
            vendorname (str):  Name of the vendor store
    """
    
    def __init__(self, vendorid='', vendorname=''):
        self._id = vendorid
        self._name = vendorname

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    def toxml(self):
        """Return an XML string of the Vendor."""

        xmlstring = ''
        xmlstring += "<Vendor>\n"
        xmlstring += "<VendorID>" + str(self._id) + "</VendorID>\n"
        xmlstring += "<VendorName>" + str(self._name) + "</VendorName>\n"
        xmlstring += "</Vendor>\n"
        return xmlstring


class VendorMap(UserDict):
    """ Map of Bricklink vendor id to Vendor object as extracted from the Bricklink item page

        Attributes:
            data(dict): dict[vendor.id] = Vendor
    """
    def __init__(self):
        UserDict.__init__(self)
        self.data = dict()

    def __str__(self):
        """ Return an XML formatted vendor map. """
        return self.toxml()

    def addvendor(self, vendor):
        """Add a vendor to the vendor map.
            If the vendor id is not present yet, add it.

            Args:
                vendor (Vendor): the Vendor object to be added
            Returns:
                false if the vendor id is already present, true otherwise
        """
        if vendor.id in self.data:
            return False
        else:
            #logging.debug("Adding vendor: " + vendor.name)
            self[vendor.id] = vendor  # assign the whole vendor object in case we add to it later
            return True      
    
    def getnumvendors(self):
        """Get the length of the vendor map."""
        return len(self)
        
    def getvendorname(self, vendorid):
        """Get the name of the vendor for a given id."""
        if vendorid in list(self.keys()):
            return self[vendorid].name
        else:
            return ''

    def toxml(self):
        """Return an XML string of the VendorMap."""

        vendorkeys = list(self.keys())
        xml_string = '<VendorMap>'
        for vendorid in vendorkeys:
            vendor = self[vendorid]
            xml_string += vendor.toxml()
        xml_string += '</VendorMap>'
        return xml_string

#not sure this works                           
    # def read(self, filename=None):
    #     assert filename is not None, "price List filename required"
    #     print( "Building vendor map from file: " + filename)
    #     self.data = dict()  #clear any existing data
    #
    #     soup = stockarrayoup( open(filename).read(), "lxml")
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


class VendorStats():
    """Process bcmdata and organize stats.

        Attributes:
            data(BCMData): the BCMData object
            ELEMWEIGHTS(ndarray): numpy array of element weights
            NUMVENDORS(int): number of vendors in vendorlist
            NUMELEMS(int): number of elements in elementlist
            ITEMS(ndarray): points to elementlist
            ITEMSPERVENDOR(ndarray): ITEMSPERVENDOR[vendorid] = num different items stocked by vendorid
            VENDORSPERELEMENT(ndarray): VENDORSPERELEMENT[elementid] = num vendors stocking elementid
            TOTALPERVENDOR(ndarray): TOTALPERVENDOR[
    """
    def __init__(self, bcmdata):
        self.update(bcmdata)

        self.data = bcmdata
        self.elemweights = bcmdata.elementweights()  # numpy array
        self.numvendors = len(self.data.vendorlist)
        self.numelems = len(self.data.elementlist)
        self.items = len(self.data.elementlist)
        self.itemspervendor = self.__itemspervendor()
        self.vendorsperelement = self.__vendorsperelement()
        self.totalvendor = self.__totalitemspervendor()
        self.vdict = self.__makedictionary()

    def update(self, bcmdata):
        self.data = bcmdata
        self.elemweights = bcmdata.elementweights()  # dictionary
        self.numvendors = len(self.data.vendorlist)
        self.numelems = len(self.data.elementlist)
        self.items = len(self.data.elementlist)
        self.itemspervendor = self.__itemspervendor()
        self.vendorsperelement = self.__vendorsperelement()
        self.totalvendor = self.__totalitemspervendor()
        self.vdict = self.__makedictionary()
        
    def __itemspervendor(self):
        s = self.data.stock
        itemspervendor = np.ndarray(s > 0).sum(0)
        return itemspervendor        
    
    def __totalitemspervendor(self):
        # for each vendor
        # sum the min( stock, wanted) for each element
        #vitems = np.zeros(shape=(self.NUMVENDORS), dtype='int')
        stockarray = self.data.stock
        wantedarray = self.data.wanted.reshape(len(self.data.elementlist), 1)
        vitems = np.minimum(stockarray, wantedarray).sum(0)
        vitems.mask = stockarray.mask
        #print(vitems)
        #print(np.minimum(stockarray,wantedarray))
        #print(np.minimum(stockarray,wantedarray).sum(0))
        #for vidx, stock in enumerate(stockarray.T): #enumerate over the columns in stock
        #    for eidx, wanted in enumerate(wantedarray): #enumerate over each element in the wanted list
        #        vitems[vidx] += min( stock[eidx], wanted )
        return vitems
    
    def __vendorsperelement(self):
        s = self.data.stock
        vendorsperelement = np.ndarray(s > 0).sum(1)
        return vendorsperelement
    
    def stockbywanted(self):
        return self.__stockbywanted()
    
    def __stockbywanted(self):
        """  
        Calculates a sorting helper for vendors.  The more items a vendor can completely fill, the higher its
            value.
        SBW = stock / wanted
        SBW = 1.0 if stock/wanted >= 1.0 ELSE stock/wanted
        """
        stockarray = self.data.stock.astype('float')
        wantedarray = self.data.wanted.reshape(self.numelems, 1).astype('float')
        stockbywant = stockarray/wantedarray
        greaterthan1 = stockbywant >= 1.0  # creates a true/false array that will be used in the next line
        stockbywant[greaterthan1] = 2.0  # completely filling an order counts 3X more than a partial fill
        return stockbywant
    
    def vendorstockweights(self):
        return self.__stockbywanted().sum(0)
    
    def vendorpriceweights(self):
        # function of element weight, vendor price, vendor qty (gets credit for how many it has)
        #sort by self.data.elementlist
        sortedweights = self.elemweights  # aligned with elementlist now
        #print(sortedweights)
        elemweight = np.array(sortedweights, dtype='float').reshape((len(self.elemweights), 1))
        pricearray = self.data.prices
        stockarray = self.data.stock
        avgpricearray = self.avgprices()
        #print(elemweight)
        #print(pricearray)
        
        priceweight = elemweight/pricearray
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
        p = self.data.prices
        avgprices = p.sum(1) / np.ndarray(p > 0).sum(1) # the 1 causes
        return avgprices 
    
    def vendorweights(self):
        #Use nd arrays
        
        vendorstockweights = self.__stockbywanted().sum(0) * 2.5
        vendorpriceweights = self.vendorpriceweights().sum(0)
        
        print(vendorstockweights)
        print(vendorpriceweights)

    def __makedictionary(self):
        vdict = dict()
        #avgprices = self.data.avgprices()
        for vindex, vendor in enumerate(self.data.vendorlist):
            vdict[vendor] = (self.itemspervendor[vindex], self.totalvendor[vindex])
        return vdict

    def report(self):
        print("There are %d items to purchase" % self.items)
        print("%d vendors have the following number distinct items available:" % self.numvendors)
        print("Vendors per element", self.itemspervendor)
        print("Elements per vendor", self.vendorsperelement)
        print(self.vdict)
        #vlist = self.data.vendorlist

#test code goes here
if __name__ == '__main__':
    pass
    
    