'''
Created on Oct 30, 2012

@author: khooks
'''
from UserDict import UserDict
from vendors import VendorMap
import numpy as np
import numpy.ma as ma
import pandas as pd
import logging
from shoppinglist import ShoppingList
from legoutils import LegoElement

class BCMDict(UserDict):
    
    def __init__(self):
        UserDict.__init__(self)
    
    def __getitem__(self, key):
            if key in self.data:
                return self.data[key]
            if hasattr(self.__class__, "__missing__"):
                return self.__class__.__missing__(self, key)
            #raise KeyError(key)
            return (0.0, 0) 

class BCMData(object):
    # this is a mutable ndarray object that's passed to the optimizer
    def __init__(self, bcmdict, wanteddict):
        
        self.vendorlist = list() #match the indices of BCM in the column
        self.elementlist = list() #match the indices of BCM in the row
        self.wanted = None
        self.prices = None
        self.stock = None
        
        self.BCM = None #fancy ndarray
         
        self.build(bcmdict, wanteddict) #initializes all of the data above
          
    def build(self, bcmdict, wanteddict):
        logging.info("Rebuilding arrays...")
        self.buildlists(bcmdict)
        self.buildarrays(bcmdict, wanteddict)
        self.initbcm()
        
    def buildlists(self, bcmdict):        
        for keytuple in bcmdict:
            (elementid, vendorid) = keytuple
            self.addtolist(self.vendorlist, vendorid)  #initialize the vendor list
            self.addtolist(self.elementlist, elementid) #initialize the elementlist

    def buildarrays(self, bcmdict, wanteddict):
        self.prices = self.buildpricearray(bcmdict)
        self.stock = self.buildstockarray(bcmdict)
        self.wanted = self.buildwantedarray(wanteddict)
        
    def buildpricearray(self, bcmdict): #returns numpy array of the prices        
        '''
            n, m = num elements, num vendorlist  
            A = [[item1vendor1price, item1vendor2price, item1vendor3price],
                [item2vendor1price, item2vendor2price, item2vendor3price],...]
                
            A[i,j] = item[i]vendor[j] price    
        '''
        m = len(self.elementlist) #rows (i)
        n = len(self.vendorlist) #columns (j)
        
        pricearray = np.ndarray(shape = (m, n), dtype=np.float) 
        pricearray.fill(0)
        for i in range(0, m):
            for j in range(0, n):
                keytuple = (self.elementlist[i], self.vendorlist[j])
                if keytuple in bcmdict.keys():
                    pricearray[i,j] = float(bcmdict[self.elementlist[i], self.vendorlist[j]][1])
                else:
                    pricearray[i,j] = 0.0
        #self.pricearray = pricearray
        mask = pricearray <= 0.0  #p and pmask share the same indices       
        #self.mpricearray = ma.array( pricearray, mask=mask ) # a masked array of sorted vendor indice      
        #self.pprices = pd.DataFrame( pricearray, index=self.elementlist, columns=self.vendorlist )
        
        return pricearray
    
    def buildstockarray(self, bcmdict): #returns numpy array of vendor stock   
        '''
            B = [[item1vendor1stock, item1vendor2stock, item1vendor3stock],
                [item2vendor1stock, item2vendor2stock, item2vendor3stock],...]              
            B[i,j] = item[i]vendor[j] stock    
        '''
        m = len(self.elementlist)
        n = len(self.vendorlist)
        stockarray = np.ndarray(shape = (m, n), dtype=np.int)
        stockarray.fill(0)
        for i in range(0, m):
            for j in range(0, n):
                keytuple = (self.elementlist[i], self.vendorlist[j])
                if keytuple in bcmdict.keys():
                    stockarray[i,j] = int(bcmdict[self.elementlist[i], self.vendorlist[j]][0])
                else:
                    stockarray[i,j] = 0
        #self.stockarray = stockarray
        mask = stockarray <= 0.0  #p and pmask share the same indices       
        #self.mstockarray = ma.array( stockarray, mask=mask ) # a masked array of sorted vendor indice      
        #self.pstock = pd.DataFrame( stockarray, index=self.elementlist, columns=self.vendorlist )
        #self.pstock.to_csv('stock.csv', sep=',') #cols, header, index, index_label, mode, nanRep, encoding, quoting, line_terminator)
        return stockarray
    
    def buildwantedarray(self, wanteddict):    #returns numpy array of wanted items
        m = len(self.elementlist)       
        wantedarray = np.ndarray(shape = (m), dtype=np.int)
        for i in range(0, m):
            elementid = self.elementlist[i]
            wantedarray[i] = wanteddict[elementid]
        #self.wantedarray = wantedarray    
        #self.pwanted = pd.Series( wantedarray, index=self.elementlist )       
        return wantedarray    
             
    def initbcm(self):
        m = len(self.elementlist) #rows (i)
        n = len(self.vendorlist) #columns (j)
        self.BCM = np.ndarray(shape = (m, n), dtype=np.int)
        self.BCM.fill(0)
                   
    def addtolist(self, alist, value):             
        if value not in alist:
            #string = "Adding value: " + str( value) + " to list " + str( alist)
            #logging.(string)
            alist.append(value)
        return True
        
class BCMEngine(object):
    '''     
    contains a dictionary that allows access via data[elementid, vendorid] = (price, qty)
        '''
    vendormap = VendorMap()
    
    def __init__(self, bricklink, wanteddict):
        #UserDict.__init__(self)
        BCMEngine.vendormap = bricklink.vendormap
        #self.data = BCMData() #the mutable data object that's passed to the optimizer

        self.bcmdict = self.createbcmdict(bricklink, wanteddict) #self.data[elementid, vendorid] = (price, qty) #essentially a copy of the Bricklink data.  Don't change this once initialized
        self.wanted = self.createwanteddict(bricklink, wanteddict) #don't change this either
        
        self.data = BCMData(self.bcmdict, self.wanted)
        
        '''#this is a working list.  We'll cull this from time to time and rebuild it if neccessary.
        self.svendors = None                          #it's important that these lists are kept current, since they're used as keys for interating over data[elementid, vendorid]
 #this is also a working list, but it won't likely be modified
        self.selements = None
        
        self.pricearray = None #a numpy array
        self.mpricearray = None #masked price array (mask by the stock mask)
        self.pprices = None     #a pandas dataframe
        
        self.stockarray = None 
        self.mstockarray = None #a masked numpy array
        self.pstock = None      #a pandas dataframe
        
        self.wantedarray = None #a numpy array
        self.pwanted = None #a pandas series

        self.result = None  #will use this calculated array result[i,j] = 'quantity to buy', where i = elementindex, j = vendorindex
                            #indexes i, j need to match indexes in elementlist[i] and vendorlist[j] for successful remapping
        self.initialized = False
        '''
        
    #overload the default get function.  If the key combo doesn't exist, return a 0,0 pair      
    def createwanteddict(self, bricklink, wanteddict):        
        wanted = dict()        
        for elementid in bricklink.keys(): #bricklink.data only has one key - the elementid                      
            wanted[elementid] = wanteddict.getwantedqty(elementid) #populate the wanted qty dictionary        
        return wanted

          
    def createbcmdict(self, bricklink, wanteddict): 
        #creates a dictionary keyed to the vendor and an element that contains the qty and price for each vendor/element pair
        #prices.append([vendorid, vendorname, vendorqty, vendorprice])                
        #self.headers.append("Vendor")
        logging.info("Building BCM data")
        bcm = dict()
        #create the price array
        #create the stock array        
        for elementid in bricklink.keys(): #bricklink.data only has one key - the elementid
            for vendorinfo in bricklink[elementid]:  #iterate over the list of vendors in bricklink[elementid] = (vendorid, qty, price)
                vendorid = str(vendorinfo[0])
                vendorqty = int(vendorinfo[1])
                vendorprice = float(vendorinfo[2])  
                bcm[elementid, vendorid] = (vendorqty, vendorprice)  
        self.initialized = True    
        return bcm
           
    def describesolution(self, result):
        if self.result:
            pass
    def describevendors(self):
        #print out some information about the vendors
        print("There are " + str(len(self.vendorlist)) + " in Vendorlist")
        
    def getqtyandprice(self, elementid, vendorid):
        assert( (elementid, vendorid) in self.bcmdict.keys() ), "ElementID %r, VendorID %r not found" % (elementid, vendorid)
        (qty, price) = self.bcmdict[elementid, vendorid]       
        return (qty, price)
        
  
    def getvendorlist(self):
        return self.data.vendorlist
    
    def getelementlist(self):
        return self.data.elementlist
             
    def hasminquantity(self, elementid, vendorid ):
        assert vendorid in self.vendormap, "Cannot determine qantity, vendor %r does not exist in vendorlist" % vendorid
        
        if (elementid, vendorid) in self.bcmdict:
            wantedquantity = int(self.wanted[elementid])
            return ( (self.bcmdict[elementid, vendorid][0]) >= wantedquantity )
        else: 
            return False
          
    def removevendor(self, vendorid):
        #doesn't remove it from the .data, only from the list of vendors
        assert vendorid in self.vendorlist, "Vendor %r does not exist in vendorlist" % vendorid
        self.vendorlist.remove(vendorid)
                            
    #TODO: make this work
    def cullvendorsbyprice(self):
        #NOT COMPLETE
        cheapvendoridx = self.sortedvendoridx()
        #keep the n cheapest
        #make a new list containing only these vendors
        initial_length = len(self.vendorlist)
        cheapvendors = [ self.vendorlist[i] for i in cheapvendoridx ]
        self.vendorlist = cheapvendors
        self.buildarrays()
        finallength = len(self.vendorlist)
        removed = initial_length - finallength
        logging.INFO("Removed " + str(removed) + " vendors from the list")
        #print(cheapvendors)
        

 #compressed, sorted, masked array of vendor indices
            
    def cheapvendorsbyitem(self, nvendors):
        #keep the cheapest N vendors for each item
        #at most, this leaves us with NumElements x N vendors
        #use the pricearray and loop over vendor list        
        #msorted = self.sortedvendoridx() #this is a list of vendor indices, sorted and masked > 0
        cheap = self.data.prices
        avg = self.avgprices()
        mask = ((cheap.T <= avg) & (cheap.T > 0.0)).T
        
        return cheap, mask
    
    def sortedvendoridx(self):        
        #returns a masked array of the sorted vendor indices, masking the 0.0 values
        p = self.data.prices       
        s = p.argsort(axis=1) # sort array of vendor indices are now sorted by s
        static_indices = np.indices( p.shape )
        psorted = p[static_indices[0], s]               
        sortedmask = psorted <= 0.0  #p and pmask share the same indices       
        m = ma.array( s, mask=sortedmask ) # a masked array of sorted vendor indices, sorted by price of element        
        return m
    
    def sortedelementidx(self):
        #returns a lsit of the indices of self.elementlist sorted by weight (descending)
        elementweights = self.elementweights()
        elementindexlist = [index for index, id in enumerate(self.elementlist) ]       
        pairs = sorted( zip(elementweights, elementindexlist), reverse = True ) # (weight, elementindex) tuples sorted on weight
        elementorder = [ eidy for (x, eidy) in pairs] #this is the order to search elements       
        return elementorder
    
    def elementweights(self):
        #generate a weight for each element - basically the avg price for that element * wanted qty, normalized
        avgprices = self.avgprices()
        wanted = self.data.wanted       
        weights = (avgprices * wanted)/(avgprices * wanted).max()       
        return weights
  
    def avgprices(self):
        #data[elementid, vendorid] = [price, qty]
        p = self.data.prices
        avgprices = p.sum(1)/(p > 0).sum(1) #the 1 causes
        return avgprices
        #for item in self.item
    
    def itemspervendor(self):
        s = self.data.stock
        itemspervendor = (s > 0).sum(0)
        return itemspervendor
    
    def maparray2vendorid(self, array):
        d = dict()
        #width of array must be equal to length of vendorlist
        shape = array.shape
        if shape[1] == len(self.vendorlist):
            for index, col in enumerate(array.T):
                vendorid = self.vendorlist[index]
                d[vendorid] = col
        
        return d
        
    def rawshoppinglist(self, result):
        #for each vendor, item & quantity
        #converts result array from Opt into a vendorid, elementid dictionary
        rawshoppinglist = dict()       #rawshoppinglist[vendorid, elementid] = qty
        if result.any():
            r = result
            for vindex, vendor in enumerate(r.T):  #iterate over columns in result
                if any(val > 0 for val in vendor): #check if any values in column 'vendor' are greater than zero
                    eindices = np.nonzero(vendor)
                    for eindex in eindices[0]:
                    #print (vendor, index)
                        vendorid = self.vendorlist[vindex]
                        elementid = self.elementlist[eindex]
                        rawshoppinglist[vendorid, elementid] = r[eindex, vindex] #convert back to a column
            #print( shoppinglist)
            
            return rawshoppinglist
        
        else:
            print("No result set found")
            return False
        
    def printdata(self):
        for item in self.bcmdict.items():
            print (item)

    def shoppinglist(self, result):
        rsl = self.rawshoppinglist(result) #this is a dictionary keyed on vendorid 
        #print(rawshoppinglist)
        #additem(self, itemid, colorid, wantedqty, vendorid, vendorname, vendorqty, vendorprice
        shoppinglist = ShoppingList()
        #self.printdata()
        for vendorid, elementid in rsl:  #vendorindex is the key           
            #print( rawshoppinglist[vendorid] )
            vendorqty = rsl[vendorid, elementid]
            vendorname = self.vendormap[vendorid]                
            (stockqty, vendorprice) = self.getqtyandprice(elementid, vendorid)
            (itemid, colorid) = LegoElement.splitelement(elementid)  
            wantedqty = self.wanted[elementid]  
            shoppinglist.additem(itemid, colorid, wantedqty, vendorid, vendorname, vendorqty, vendorprice)
        return shoppinglist       
    
    def resultsummary(self, result):
        #found items from X vendors
        rsl = self.rawshoppinglist(result)
        keytuples = rsl.keys()
        #sort the keys on vendor (first element)
        for vendorid, elementid in rsl:  #vendorindex is the key           
            #print( rawshoppinglist[vendorid] )
            vendorqty = rsl[vendorid, elementid]
            vendorname = self.vendormap[vendorid]                
            (stockqty, vendorprice) = self.getqtyandprice(elementid, vendorid)
            (itemid, colorid) = LegoElement.splitelement(elementid)  
            wantedqty = self.wanted[elementid]  
                 
        return
        
    '''
            
    def vendorcount(self):     
        return len(self.vendormap)
    
    def dataquality(self):
        assert self.initialized == True, "data not initialized, cannot report dataquality"
        
        print( "The data looks like this:")
        print( str( len(self.itemlist) ) + " Total Items")
        print( str( len(self.vendorlist) ) + " Total Vendors" )                        
                  
    def display(self):
        
        assert self.initialized == True, "bcmdata not initialized"
        
        print( self.headers)
        #print self.wantedqty
        for e in self.keys(): #vendors
            thiselement = self.bcm[e]
            row = list()
            row.append(thiselement.id)
            for v in self.vendormap.keys():
                try:
                    row.append(thiselement.vendorstock[v].quantity) 
                    row.append(thiselement.vendorstock[v].price)  
                except KeyError:
                    row.append('')
            print( row )
               
    def toCSV(self):
            
        assert self.initialized == True, "bcmdata not initialized"
        
        csvstring = ''
        for val in self.headers:
            csvstring += val
            csvstring += ','
        csvstring += '\n'
        for v in self.vendormap.keys(): #vendors
            csvstring += self.vendormap[v].name + ','
            for e in self.bcm.keys():
                thiselement = self.bcm[e]
                try:
                    csvstring += str(thiselement.vendorstock[v].quantity) + ',' + str(thiselement.vendorstock[v].price) 
                    csvstring += ','   
                except KeyError:
                    csvstring += ", 0,"
            csvstring += "\n"
      
        return csvstring
    '''         
if __name__ == '__main__':
    pass
