"""
Created on Oct 30, 2012

@author: khooks
"""
#from UserDict import UserDict
import vendors
from vendors import VendorStats, vendorMap
import numpy as np
import numpy.ma as ma
import logging
from shoppinglist import ShoppingList
from legoutils import LegoElement
from operator import itemgetter
from collections import defaultdict
from exceptions import Exception


class BCMData():
    # this is a mutable ndarray object that's passed to the optimizer
    def __init__(self, bcmdict, wanteddict, elemdict, vendict):
        
        self.vendorlist = list()  #contains the active list of vendors.  All matrix keys match this list.
        self.elementlist = list()  #contains the list of elements.  All matrix keys match this list.
        self.WANTED = None  #numpy array
        self.PRICES = None  #numpy array
        self.STOCK = None   #numpy array
        self.BCMDICT = bcmdict
        
        self.__initialize_lists(self.BCMDICT) 
        
        self.WANTDICT = wanteddict
        self.ELEMDICT = elemdict
        self.VENDICT = vendict
       
        self.WANTED = self.__buildwantedarray(self.WANTDICT)
        self.STOCK, self.PRICES = self.__buildvendorarrays(self.BCMDICT)
        self.__vs = VendorStats(self) 
        
        self.__update()      
        
        self.__need_rebuild = False 

        #self.VENDSORTLIST = self.__createvendsortinglist(self.BCMDICT)          
 
    def __update(self):
        self.__sortlists()
        self.__updatearrays()
        self.__vs.update(self)
        self.AVGPRICES = self.avgprices(stockweighted=True)
 
    def __initialize_lists(self, bcmdict):
        """ Build the initial elementlist and vendorlist based on bcmdict """ 
        logging.info("Building BCMData lists") 
        #k = [ keytuple for keytuple in bcmdict.keys() ]      
        for keytuple in bcmdict.keys():
            (elementid, vendorid) = keytuple
            self.addtolist(self.vendorlist, vendorid)  #initialize the vendor list
            self.addtolist(self.elementlist, elementid) #initialize the elementlist
            
    def __updatearrays(self):
        logging.info("Forcing array update...")
        self.WANTED = self.__buildwantedarray(self.WANTDICT)
        self.__updatevendorarrays()
        self.__need_rebuild = False      
    
    def __buildvendorarrays(self, bcmdict):
        """ Iterate over element, vendor in the elementlist and vendorlist to create the numpy
            arrays.  Get the data from the bcmdict.  
        """
        shape = ( len(self.elementlist), len(self.vendorlist) )
        pricearray = ma.masked_array(np.zeros(shape, dtype='int'))
        stockarray = ma.masked_array(np.zeros(shape, dtype='int'))
        #wanted doesnt change
        
        for eindex, element in enumerate(self.elementlist):
            for vindex, vendor in enumerate(self.vendorlist):
                if (element, vendor) in self.BCMDICT:
                    stockarray[eindex, vindex] = int(self.BCMDICT[element, vendor][0])
                    pricearray[eindex, vindex] = int(self.BCMDICT[element, vendor][1] * 100)
        
        stockarray = np.minimum(stockarray, self.WANTED.reshape( len(self.elementlist),1)) #clip the max value of stock to the wanted quantity
        
        mask = stockarray <= 0
        stockarray.mask = mask
        pricearray.mask = mask
        
        return stockarray, pricearray
    
    def __updatevendorarrays(self):
        """ Create new arrays in case elementlist and vendorlits have changed size """        
        stockarray, pricearray = self.__buildvendorarrays(self.BCMDICT)
        self.PRICES = pricearray
        self.STOCK = stockarray        
        return stockarray, pricearray
               
    def __buildwantedarray(self, wanteddict):    #returns numpy array of WANTED items
        """ Create a numpy array of wanted quantities """
        logging.info("Building WANTED array...")
        m = len(self.elementlist) #ensure the size of the array is consistent with the others      
        wantedarray = np.ndarray(shape = tuple(m), dtype=np.int)
        for eidx, elementid in enumerate( self.elementlist ):
            wantedarray[eidx] = wanteddict[elementid] 
        return wantedarray   
     
    def __sortlists(self):                    
        self.__elementsort()
        self.__vendorsort()
            
    def __elementsort(self, sortweights=None):
        logging.info("Sorting Element List...")
        if sortweights: weights = sortweights
        else: weights = self.elementweights()
        #resort the elementlist using these weights
        self.elementlist = [y for (x, y) in sorted( zip( weights, self.elementlist ), reverse=True )]

    def __vendorsort(self, sortby='uniqueitems'):
        logging.info("Sorting Vendor List...")
        
        if sortby == 'uniqueitems':
            weights = self.__vs.ITEMSPERVENDOR
        elif sortby == 'totalitems':
            weights = self.__vs.TOTALPERVENDOR
        else:
            return #nothing sorted
            
        self.vendorlist = [y for (x, y) in sorted( zip( weights, self.vendorlist ), reverse=True )]

              
    def __createvendsortinglist(self, bcmdict):
        """ Return list of tuples (vendor index, element index, price)
            
            The element index is the element of the highest weight that the vendor offers in sufficient qty
        """
        factor = 1.0
        k = list()
        for vidx, vcol in enumerate(self.STOCK.T):
            for eidx, stock in enumerate(vcol):
                if stock > self.WANTED[eidx] * factor:
                    price = self.PRICES[eidx, vidx]
                    stock = self.STOCK[eidx, vidx]
                    k.append( (vidx, eidx, price, stock) )
                    break
        # now sort this list on eidx=>ascending, price=>descending, stock->satisfies(eidx)
        
        k = sorted( k, key=itemgetter(1, 2) )
                      
        return k
    
    def vendorsortdict(self):
        """Return a dictionary describing how to sort vendors
        
            k[vendor index] = (elementid to sort on, price, qty)
            Important:  It's assumed that the arrays are already sorted on the
            element weights, meaning the most costly elements are first.  This 
            algorithim uses the first element the vendor stocks in sufficient quantity             
        """
        size = len(self.vendorlist)
        #k = np.zeros(shape=(size), dtype=(int, float))
        k = dict()
        for vidx, vcol in enumerate(self.PRICES.T): #iterate over columns in the price matrix
            for eidx, price in enumerate(vcol):
                if price > 0:
                    qty = self.STOCK[eidx, vidx]
                    k[vidx] = (eidx, price, qty)
                    break
        return k 
    
    def __sufficientqty(self, eidx, vidx, factor=0.5):        
        return self.STOCK[eidx, vidx] >= self.WANTED[eidx] * factor
        
    def removevendor(self, vendorid):
        #doesn't remove it from the .data, only from the list of vendors
        assert vendorid in self.vendorlist, "Vendor %r does not exist in vendorlist" % vendorid
        self.vendorlist.remove(vendorid) 
        self.__need_rebuild = True                    
         
    def removevendors(self, vendorindices):
        #Create a new vendorlist that doesn't include the list of id's passed via vendorindices
        logging.info("Trying to remove " + str(len(vendorindices)) + " vendors.")
        before = len(self.vendorlist)
        newlist = [ vendor for vendor in self.vendorlist if self.vendorlist.index(vendor) not in vendorindices ]       
        self.replacevendorlist(newlist)
        after = len(self.vendorlist)
        logging.info("Removed: " + str(before - after) + " vendors.")
        self.__update()
        return newlist
                    
    def addtolist(self, alist, value):             
        if value not in alist:
            #string = "Adding value: " + str( value) + " to list " + str( alist)
            #logging.(string)
            alist.append(value)
        return True

    def replacevendorlist(self, newvendors):
        self.vendorlist = newvendors
        #remove all items that contain these vendors from the dictionaries?
        self.__update()
    
    
    def avgprices(self, stockweighted=False):
        """Return a masked array of the average price by element"""
        p = ma.array(self.PRICES, mask=self.PRICES <= 0)
                
        if stockweighted:
            s = ma.array(self.STOCK, mask=self.STOCK <= 0)
            avgprices = ma.average( p, weights=s, axis=1 )      
        else:
            #avgprices = p.sum(axis=1)/(p > 0).sum(axis=1) #denominator sums the non-zero values
            avgprices = ma.average( p, axis=1 )
        return avgprices    
    
    def elementweights(self):
        #generate a weight for each element - basically the avg price for that element * WANTED qty, normalized
        weights = self.WANTED * self.avgprices()         
        return weights    
    
    def __itemspervendor(self):
        s = self.STOCK
        itemspervendor = np.ndarray(s > 0).sum(0)
        return itemspervendor  

    def partcount(self):
        """count the number of unique parts and the total number of parts"""
        return len(self.WANTED), self.WANTED.sum()
                 
              
class BCMEngine(object):
    """
    contains a dictionary that allows access via data[elementid, vendorid] = (price, qty)
        """
    #vendormap = VendorMap()

    def __init__(self, bricklink, wanteddict):
        #UserDict.__init__(self)
        #BCMEngine.vendormap = bricklink.vendormap
        #self.data = BCMData() #the mutable data object that's passed to the optimizer

        if not isinstance(vendorMap, vendors.VendorMap):
            raise Exception, "global vendorMap doesn't exist.  Make sure to include Vendor module"

        self.BCMDICT = self.__createbcmdict(bricklink, wanteddict) #self.data[elementid, vendorid] = (price, qty) #essentially a copy of the Bricklink data.  Don't change this once initialized
        # self.WANTED = self.__createwanteddict(bricklink, wanteddict) #don't change this either
        # self.ELEMDICT = self.__createelementdict(self.BCMDICT)
        # self.VENDICT = self.__createvendict(self.BCMDICT)
        #
        self.data = BCMData(self.__createbcmdict(bricklink, wanteddict),
                            self.__createwanteddict(bricklink, wanteddict),
                            self.__createelementdict(self.BCMDICT),
                            self.__createvendict(self.BCMDICT))
                            #self.BCMDICT, self.WANTED, self.ELEMDICT, self.VENDICT)


    #overload the default get function.  If the key combo doesn't exist, return a 0,0 pair
    def __createwanteddict(self, bricklink, wanteddict):
        logging.info("Building Wanted Dictionary")
        wanted = dict()
        for elementid in bricklink.keys(): #bricklink.data only has one key - the elementid
            wanted[elementid] = wanteddict[elementid].wantedqty #populate the WANTED qty dictionary
        return wanted

    def __createbcmdict(self, bricklink, wanteddict):
        #creates a dictionary keyed to the vendor and an element that contains the qty and price for each vendor/element pair
        #PRICES.append([vendorid, vendorname, vendorqty, vendorprice])
        #self.headers.append("Vendor")
        logging.info("Building soln(Element,Vendor) Dictionary")
        bcm = dict()
        #create the price array
        #create the STOCK array
        for elementid in bricklink.keys(): #bricklink.data only has one key - the elementid
            for vendorinfo in bricklink[elementid]:  #iterate over the list of vendors in bricklink[elementid] = (vendorid, qty, price)
                vendorid = str(vendorinfo[0])
                vendorqty = int(vendorinfo[1])
                vendorprice = float(vendorinfo[2])
                bcm[elementid, vendorid] = (vendorqty, vendorprice)
        self.initialized = True
        return bcm

    def __createelementdict(self, bcmdict):
        logging.info("Building Element-wise Dictionary")
        elementdict = defaultdict(list)
        for keys, values in bcmdict.items():
            element, vendor = keys
            qty, price = values
            elementdict[element].append( (vendor, qty, price) )
            #if element in elementdict: elementdict[element].append( (vendor, qty, price ))
            #else: elementdict[element] = [(vendor, qty, price)]

        for element, plist in elementdict.items():
            #sort the list price
            sortedlist = sorted( plist, key=itemgetter(2) )
            elementdict[element] = sortedlist #reassign the sorted list instead
            #print sortedlist
        return elementdict

    def __createvendict(self, bcmdict):
        logging.info("Building Vendor-wise Dictionary")
        vendict = defaultdict(list)
        for keys, values in bcmdict.items():
            element, vendor = keys
            qty, price = values
            vendict[vendor].append( (element, qty, price) )

        return vendict



    def presolve(self):
        self.prunevendorsbyavgprice()

    def describesolution(self, result):
        if result:
            pass
    def describevendors(self):
        #print out some information about the vendors

        print("There are " + str(len(self.vendorlist)) + " in Vendorlist")

    def getqtyandprice(self, elementid, vendorid):
        assert( (elementid, vendorid) in self.BCMDICT.keys() ), "ElementID %r, VendorID %r not found" % (elementid, vendorid)
        (qty, price) = self.BCMDICT[elementid, vendorid]
        return qty, price


    def getvendorlist(self):
        return self.data.vendorlist

    def getelementlist(self):
        return self.data.elementlist



    #prune vendors that are above average in price
    def prunevendorsbyavgprice(self, pricefactor=0.5):
        #prune the vendors that are more greater than pricefactor * average (0.5 keeps average and cheaper)
        logging.info("Removing vendors with above-average pricing")
        data = self.data
        removethese = list()
        p = self.data.PRICES
        avgprices = data.avgprices() #same indices as elementlist

        for element, vendor in self.BCMDICT.keys():
            eindex = data.elementlist.index(element)
            vindex = data.vendorlist.index(vendor)

            if p[eindex][vindex] > avgprices[eindex]:
                if vindex not in removethese:
                    removethese.append(vindex)

        newlist = data.removevendors(removethese)
        #data.update()
        return newlist

    def vendorstats(self):
        """Return a dictionary with an entry containing stats for each vendor

            vdict[vendor] = (num of stocked components, price factor)
        """
    #TODO: make this work
    def cullvendorsbyprice(self):
        #NOT COMPLETE
        cheapvendoridx = self.sortedvendoridx()
        #keep the n cheapest
        #make a new list containing only these vendors
        initial_length = len(self.vendorlist)
        cheapvendors = [ self.vendorlist[i] for i in cheapvendoridx ]
        self.vendorlist = cheapvendors
        self._update()
        finallength = len(self.vendorlist)
        removed = initial_length - finallength
        logging.info("Removed " + str(removed) + " vendors from the list")
        #print(cheapvendors)

    def sortedvendoridx(self):
        #returns a masked array of the sorted vendor indices, masking the 0.0 values
        p = self.data.PRICES
        s = p.argsort(axis=1) # sort array of vendor indices are now sorted by s
        static_indices = np.indices( p.shape )
        psorted = p[static_indices[0], s]
        sortedmask = psorted <= 0.0  #p and pmask share the same indices
        m = ma.array( s, mask=sortedmask ) # a masked array of sorted vendor indices, sorted by price of element
        return m

#compressed, sorted, masked array of vendor indices
    # def hasminquantity(self, elementid, vendorid ):
    #     assert vendorid in vendorMap, "Cannot determine qantity, vendor %r does not exist in vendorlist" % vendorid
    #     #assert vendorid in self.vendormap, "Cannot determine qantity, vendor %r does not exist in vendorlist" % vendorid
    #
    #     if (elementid, vendorid) in self.BCMDICT:
    #         wantedquantity = int(self.WANTED[elementid])
    #         return  (self.BCMDICT[elementid, vendorid][0]) >= wantedquantity
    #     else:
    #         return False

    # def cheapvendorsbyitem(self, nvendors):
    #     #keep the cheapest N vendors for each item
    #     #at most, this leaves us with NumElements x N vendors
    #     #use the pricearray and loop over vendor list
    #     #msorted = self.sortedvendoridx() #this is a list of vendor indices, sorted and masked > 0
    #     cheap = self.data.PRICES
    #     avg = self.data.AVGPRICES
    #     mask = ((cheap.T <= avg) & (cheap.T > 0.0)).T
    #
    #     return cheap, mask


    # def sortedvendorlists(self):
    #     #     data:  bcmdata opbject
    #     #     assign a sorted list of vendor id's for each element
    #     #     sev[elementid] = [ vendorid32, vendorid2, vendorid7, ...]
    #     e = self.data.elementlist
    #     v = self.data.vendorlist
    #
    #     elementvendors = dict()
    #
    #     for keys, values in self.BCMDICT.items():
    #         element, vendor = keys
    #         qty, price = values
    #
    #
    #         #priceidx = [ index for index, price in enumerate(self.data.PRICES[eindex]) if price > 0]
    #         #pairs = sorted( zip(priceidx, v), reverse = True )
    #         #vorder = [ vidy for (x, vidy) in pairs]
    #         #sort the list of vendors by element price
    #         #elementvendors[element] = vorder
    #     return elementvendors
    #
    # def sortedelementidx(self):
    #     #returns a lsit of the indices of self.elementlist sorted by weight (descending)
    #     elementweights = self.data.elementweights()
    #     elementindexlist = [index for index, elementid in enumerate(self.elementlist) ]
    #     pairs = sorted( zip(elementweights, elementindexlist), reverse = True ) # (weight, elementindex) tuples sorted on weight
    #     elementorder = [ eidy for (x, eidy) in pairs] #this is the order to search elements
    #     return elementorder
    #
    # def vendorweights(self):
    #     eleweights = self.data.elementweights()
    #
    #
    #     #for item in self.item
    #
    #
    #
    # def maparray2vendorid(self, array):
    #     d = dict()
    #     #width of array must be equal to length of vendorlist
    #     shape = array.shape
    #     if shape[1] == len(self.vendorlist):
    #         for index, col in enumerate(array.T):
    #             vendorid = self.vendorlist[index]
    #             d[vendorid] = col
    #
    #     return d
    #
    # def rawshoppinglist(self, result):
    #     #for each vendor, item & quantity
    #     #converts result array from Opt into a vendorid, elementid dictionary
    #     rawshoppinglist = dict()       #rawshoppinglist[vendorid, elementid] = qty
    #     if result.any():
    #         r = result
    #         for vindex, vendor in enumerate(r.T):  #iterate over columns in result
    #             if any(val > 0 for val in vendor): #check if any values in column 'vendor' are greater than zero
    #                 eindices = np.nonzero(vendor)
    #                 for eindex in eindices[0]:
    #                 #print (vendor, index)
    #                     vendorid = self.data.vendorlist[vindex]
    #                     elementid = self.data.elementlist[eindex]
    #                     rawshoppinglist[vendorid, elementid] = r[eindex, vindex] #convert back to a column
    #         #print( shoppinglist)
    #
    #         return rawshoppinglist
    #
    #     else:
    #         print("No result set found")
    #         return False
    #
    # def printdata(self):
    #     for item in self.BCMDICT.items():
    #         print (item)

