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
from operator import itemgetter, attrgetter
import cProfile

#class BCMDict(dict):
    
#    def __init__(self):
#        dict.__init__(self)
    
    #def __getitem__(self, key):
    #       if key in self.data:
    #            return self.data[key]
    #       if hasattr(self.__class__, "__missing__"):
    #            return self.__class__.__missing__(self, key)
    #        #raise KeyError(key)
    #        return (0.0, 0) 
        
    #def keys(self): return self.data.keys()

class BCMData(object):
    # this is a mutable ndarray object that's passed to the optimizer
    def __init__(self, bcmdict, wanteddict, elemdict):
        
        self.vendorlist = list() #match the indices of soln in the column
        self.elementlist = list() #match the indices of soln in the row
        self.WANTED = None
        self.PRICES = None
        self.STOCK = None
               
        self.soln = None #fancy ndarray that contains the result
        self.BCMDICT = bcmdict
        self.WANTDICT = wanteddict
        self.ELEMDICT = elemdict
        
        self.__buildlists(self.BCMDICT)
                
        self.PRICES = self.__buildpricearray(self.BCMDICT)
        self.WANTED = self.__buildwantedarray(self.WANTDICT)
        self.STOCK = self.__buildstockarray(self.BCMDICT)
        
        self.__elementsort()
        self.__need_rebuild = True 
        #self.__build() #initializes all of the data above
                  
        '''    def __build(self):     
        self.__buildlists(self.BCMDICT)
        self.__buildarrays(self.BCMDICT, self.WANTDICT)
        self.__elementsort()
        '''                      
    def __buildlists(self, bcmdict): 
        logging.info("Building BCMData lists") 
        #k = [ keytuple for keytuple in bcmdict.keys() ]      
        for keytuple in bcmdict.keys():
            (elementid, vendorid) = keytuple
            #print("Adding ", keytuple)
            self.addtolist(self.vendorlist, vendorid)  #initialize the vendor list
            self.addtolist(self.elementlist, elementid) #initialize the elementlist

    def __buildarrays(self, bcmdict, wanteddict):
        logging.info("Building BCMData arrays...")
        self.PRICES = self.__buildpricearray(bcmdict)
        self.STOCK = self.__buildstockarray(bcmdict)
        self.WANTED = self.__buildwantedarray(wanteddict)
        
    def update(self):
        if self.__need_rebuild:
            logging.info("Updating BCMData arrays")
            self.forceupdate()
            self.__need_rebuild = False      
    
    def forceupdate(self):
        logging.info("Forcing array update...")
        self.PRICES = self.__buildpricearray(self.BCMDICT)
        self.STOCK = self.__buildstockarray(self.BCMDICT)
        #self.__initbcm()
        self.__need_rebuild = False      
            
    def __buildpricearray(self, bcmdict): #returns numpy array of the PRICES        
        '''
            n, m = num elements, num vendorlist  
            A = [[item1vendor1price, item1vendor2price, item1vendor3price],
                [item2vendor1price, item2vendor2price, item2vendor3price],...]
                
            A[i,j] = item[i]vendor[j] price    
        '''
        m = len(self.elementlist) #rows (i)
        n = len(self.vendorlist) #columns (j)
        
        #pricearray = np.ndarray(shape = (m, n), dtype=np.float) 
        #pricearray.fill(0)
        pricearray = np.zeros(shape = (m,n), dtype=float)
        bcmkeys = bcmdict.keys()
        for i in range(0, m):
            for j in range(0, n):
                keytuple = (self.elementlist[i], self.vendorlist[j])
                #TODO: Don't call .keys() if possible
                if keytuple in bcmkeys: 
                    pricearray[i,j] = float(bcmdict[self.elementlist[i], self.vendorlist[j]][1])
                else:
                    pricearray[i,j] = 0.0
        #self.pricearray = pricearray
        #mask = pricearray <= 0.0  #p and pmask share the same indices       
        #self.mpricearray = ma.array( pricearray, mask=mask ) # a masked array of sorted vendor indice      
        #self.pprices = pd.DataFrame( pricearray, index=self.elementlist, columns=self.vendorlist )
        
        return pricearray
    
    def __buildstockarray(self, bcmdict): #returns numpy array of vendor STOCK   
        '''
            B = [[item1vendor1stock, item1vendor2stock, item1vendor3stock],
                [item2vendor1stock, item2vendor2stock, item2vendor3stock],...]              
            B[i,j] = item[i]vendor[j] STOCK    
        '''
        m = len(self.elementlist)
        n = len(self.vendorlist)
        #stockarray = np.ndarray(shape = (m, n), dtype=np.int)
        #stockarray.fill(0)
        stockarray = np.zeros(shape=(m,n), dtype=np.int)
        bcmkeys = bcmdict.keys()
        for i in range(0, m):
            for j in range(0, n):
                keytuple = (self.elementlist[i], self.vendorlist[j])
                if keytuple in bcmkeys:
                    stockarray[i,j] = int(bcmdict[self.elementlist[i], self.vendorlist[j]][0])
                else:
                    stockarray[i,j] = 0
        #self.stockarray = stockarray
        #mask = stockarray <= 0.0  #p and pmask share the same indices       
        #self.mstockarray = ma.array( stockarray, mask=mask ) # a masked array of sorted vendor indice      
        #self.pstock = pd.DataFrame( stockarray, index=self.elementlist, columns=self.vendorlist )
        #self.pstock.to_csv('STOCK.csv', sep=',') #cols, header, index, index_label, mode, nanRep, encoding, quoting, line_terminator)
        return stockarray
    
    def __buildwantedarray(self, wanteddict):    #returns numpy array of WANTED items
        m = len(self.elementlist)       
        wantedarray = np.ndarray(shape = (m), dtype=np.int)
        for i in range(0, m):
            elementid = self.elementlist[i]
            wantedarray[i] = wanteddict[elementid]
        #self.wantedarray = wantedarray    
        #self.pwanted = pd.Series( wantedarray, index=self.elementlist )       
        return wantedarray    
                        
    def __elementsort(self, sortby=None):
        logging.info("Sorting Element-wise dictionary...")
        if sortby: weights = sortby
        else: weights = self.elementweights().keys()
        #resort the elementlist using these weights
        #print(self.elementlist)
        self.elementlist = [y for (x, y) in sorted( zip( weights, self.elementlist ), reverse=True )]
        #print(self.elementlist)
        self.forceupdate()
            
    def removevendor(self, vendorid):
        #doesn't remove it from the .data, only from the list of vendors
        assert vendorid in self.vendorlist, "Vendor %r does not exist in vendorlist" % vendorid
        self.vendorlist.remove(vendorid) 
        self.__need_rebuild = True                    
         
    def removevendors(self, vendors):
        #try and remove this list of vendors
        for v in vendors:
            if v in self.vendorlist: self.vendorlist.remove(v)
        self.__need_rebuild = True
                    
    def addtolist(self, alist, value):             
        if value not in alist:
            #string = "Adding value: " + str( value) + " to list " + str( alist)
            #logging.(string)
            alist.append(value)
        return True

    def replacevendorlist(self, newvendors):
        self.vendorlist = newvendors
        self.forceupdate()
    
    
    '''def avgprices(self):
        """Calculate the average price of each element and return it in a dictionary"""
        avgprice = dict()
        for element in self.ELEMDICT:                                       #self.ELEMDICT[element] = (vendor, qty, price)
            runningsum=0.0
            n = 0
            for (vendor, qty, price) in self.ELEMDICT[element]: #this is a list of tuples
                runningsum += price
                n += 1
            avgprice[element] = runningsum/n        
        return avgprice       
    '''        
    
    def avgprices(self):
        #data[elementid, vendorid] = [price, qty]
        p = self.PRICES
        avgprices = p.sum(1)/(p > 0).sum(1) #the 1 causes
        return avgprices    
    
    def elementweights(self):
        #generate a weight for each element - basically the avg price for that element * WANTED qty, normalized
        weights = dict()
        avgprice = self.avgprices() #ndarray
        wanted = self.WANTDICT #dictionary on elementname      
        
        for eidx, element in enumerate(self.elementlist):          
            weights[element] = avgprice[eidx] * wanted[element]      
        return weights    
      
    '''def vendorsort(self, weights):
        #resort the elementlist using these weights
        #print(self.vendorlist)
        self.vendorlist = [y for (x, y) in sorted( zip( weights, self.vendorlist ), reverse=True )]
        print(self.vendorlist)
        self.forceupdate()
      '''
              
class BCMEngine(object):
    '''     
    contains a dictionary that allows access via data[elementid, vendorid] = (price, qty)
        '''
    vendormap = VendorMap()
    
    def __init__(self, bricklink, wanteddict):
        #UserDict.__init__(self)
        BCMEngine.vendormap = bricklink.vendormap
        #self.data = BCMData() #the mutable data object that's passed to the optimizer

        self.BCMDICT = self.__createbcmdict(bricklink, wanteddict) #self.data[elementid, vendorid] = (price, qty) #essentially a copy of the Bricklink data.  Don't change this once initialized
        self.WANTED = self.__createwanteddict(bricklink, wanteddict) #don't change this either
        self.ELEMDICT = self.__createelementdict(self.BCMDICT)
        self.data = BCMData(self.BCMDICT, self.WANTED, self.ELEMDICT)

        
    #overload the default get function.  If the key combo doesn't exist, return a 0,0 pair      
    def __createwanteddict(self, bricklink, wanteddict):        
        logging.info("Building Wanted Dictionary")
        wanted = dict()        
        for elementid in bricklink.keys(): #bricklink.data only has one key - the elementid                      
            wanted[elementid] = wanteddict.getwantedqty(elementid) #populate the WANTED qty dictionary        
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
        elementdict = dict()
        for keys, values in bcmdict.items():
            element, vendor = keys
            qty, price = values
            if element in elementdict: elementdict[element].append( (vendor, qty, price ))
            else: elementdict[element] = [(vendor, qty, price)]

        for element, plist in elementdict.items():
            #sort the list price
            sortedlist = sorted( plist, key=itemgetter(2) )
            elementdict[element] = sortedlist #reassign the sorted list instead
            #print sortedlist              
        return elementdict   
    
    def presolve(self):
        self.prunevendorsbyavgprice()
           
    def describesolution(self, result):
        if self.result:
            pass
    def describevendors(self):
        #print out some information about the vendors
        print("There are " + str(len(self.vendorlist)) + " in Vendorlist")
        
    def getqtyandprice(self, elementid, vendorid):
        assert( (elementid, vendorid) in self.BCMDICT.keys() ), "ElementID %r, VendorID %r not found" % (elementid, vendorid)
        (qty, price) = self.BCMDICT[elementid, vendorid]       
        return (qty, price)
        
  
    def getvendorlist(self):
        return self.data.vendorlist
    
    def getelementlist(self):
        return self.data.elementlist
             
    def hasminquantity(self, elementid, vendorid ):
        assert vendorid in self.vendormap, "Cannot determine qantity, vendor %r does not exist in vendorlist" % vendorid
        
        if (elementid, vendorid) in self.BCMDICT:
            wantedquantity = int(self.WANTED[elementid])
            return ( (self.BCMDICT[elementid, vendorid][0]) >= wantedquantity )
        else: 
            return False
    
    #prune vendors that are above average in price
    def prunevendorsbyavgprice(self, pricefactor=0.5):
        #prune the vendors that are more greater than pricefactor * average (0.5 keeps average and cheaper)
        removethese = list()
        p = self.data.PRICES
        avgprices = self.avgprices() #same indices as elementlist
        for eindex, elementid in enumerate(self.data.elementlist):
            for vindex, vendorid in enumerate(self.data.vendorlist):
                if p[eindex][vindex] > avgprices[eindex]:
                    removethese.append(vendorid) 
        self.data.removevendors(removethese)
        self.data.update()             
                       
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
        logging.info("Removed " + str(removed) + " vendors from the list")
        #print(cheapvendors)
        

 #compressed, sorted, masked array of vendor indices
            
    def cheapvendorsbyitem(self, nvendors):
        #keep the cheapest N vendors for each item
        #at most, this leaves us with NumElements x N vendors
        #use the pricearray and loop over vendor list        
        #msorted = self.sortedvendoridx() #this is a list of vendor indices, sorted and masked > 0
        cheap = self.data.PRICES
        avg = self.avgprices()
        mask = ((cheap.T <= avg) & (cheap.T > 0.0)).T
        
        return cheap, mask
    
    def sortedvendoridx(self):        
        #returns a masked array of the sorted vendor indices, masking the 0.0 values
        p = self.data.PRICES       
        s = p.argsort(axis=1) # sort array of vendor indices are now sorted by s
        static_indices = np.indices( p.shape )
        psorted = p[static_indices[0], s]               
        sortedmask = psorted <= 0.0  #p and pmask share the same indices       
        m = ma.array( s, mask=sortedmask ) # a masked array of sorted vendor indices, sorted by price of element        
        return m
    

    
    
    def sortedvendorlists(self):
        #     data:  bcmdata opbject
        #     assign a sorted list of vendor id's for each element            
        #     sev[elementid] = [ vendorid32, vendorid2, vendorid7, ...] 
        e = self.data.elementlist
        v = self.data.vendorlist
        
        elementvendors = dict()
             
        for keys, values in self.BCMDICT.items():
            element, vendor = keys
            qty, price = values
            
            
            #priceidx = [ index for index, price in enumerate(self.data.PRICES[eindex]) if price > 0]
            #pairs = sorted( zip(priceidx, v), reverse = True )
            #vorder = [ vidy for (x, vidy) in pairs]
            #sort the list of vendors by element price
            #elementvendors[element] = vorder
        return elementvendors
    
    def sortedelementidx(self):
        #returns a lsit of the indices of self.elementlist sorted by weight (descending)
        elementweights = self.elementweights()
        elementindexlist = [index for index, id in enumerate(self.elementlist) ]       
        pairs = sorted( zip(elementweights, elementindexlist), reverse = True ) # (weight, elementindex) tuples sorted on weight
        elementorder = [ eidy for (x, eidy) in pairs] #this is the order to search elements       
        return elementorder
    

    
    def vendorweights(self):
        eleweights = self.elementweights()
        

        #for item in self.item
    
    def itemspervendor(self):
        s = self.data.STOCK
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
        for item in self.BCMDICT.items():
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
            wantedqty = self.WANTED[elementid]  
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
            wantedqty = self.WANTED[elementid]  
                 
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
