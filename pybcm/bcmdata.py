'''
Created on Oct 30, 2012

@author: khooks
'''
from collections import UserDict
from vendors import VendorMap
import copy
import numpy as np
import numpy.ma as ma
import logging
from shoppinglist import ShoppingList
from legoutils import LegoElement


class BCMData(UserDict):
    '''     
    contains a dictionary that allows access via data[elementid, vendorid] = (price, qty)
        '''
    vendormap = VendorMap()
    
    def __init__(self, bricklink, wanteddict):
        UserDict.__init__(self)
        self.data = dict() #self.data[elementid, vendorid] = (price, qty) #essentially a copy of the Bricklink data.  Don't change this once initialized
        self.wanted = dict() #don't change this either
        
        self.vendorlist = list()  #this is a working list.  We'll cull this from time to time and rebuild it if neccessary.
        #                          it's important that these lists are kept current, since they're used as keys for interating over data[elementid, vendorid]
        self.elementlist = list() #this is also a working list, but it won't likely be modified
        
        self.pricearray = None #a numpy array
        self.stockarray = None #a numpy array
        self.wantedarray = None #a numpy array
        
        #self.items = dict() # itemdescription[elementid] = [avgprice, #vendors, stddev]
        self.buildfrombricklink(bricklink, wanteddict) #initialize all of the above lists/arrays
        
        self.result = None  #will use this calculated array result[i,j] = 'quantity to buy', where i = elementindex, j = vendorindex
                            #indexes i, j need to match indexes in elementlist[i] and vendorlist[j] for successful remapping
        self.initialized = False
        
    def buildfrombricklink(self, bricklink, wanteddict): 
        #creates a dictionary keyed to the vendor and an element that contains the qty and price for each vendor/element pair
        #prices.append([vendorid, vendorname, vendorqty, vendorprice])                
        #self.headers.append("Vendor")
        logging.info("Building BCM data")
        self.vendormap = bricklink.vendormap
        
        #create the price array
        #create the stock array        
        for elementid in bricklink.keys(): #bricklink.data only has one key - the elementid
            
          
            self.wanted[elementid] = wanteddict.getwantedqty(elementid) #populate the wanted qty dictionary
                         
            for vendorinfo in bricklink[elementid]:  #iterate over the list of vendors in bricklink[elementid] = (vendorid, qty, price)

                vendorid = str(vendorinfo[0])
                vendorqty = int(vendorinfo[1])
                vendorprice = float(vendorinfo[2]) 
                
                self.addtolist(self.vendorlist, vendorid)  #initialize the vendor list
                self.addtolist(self.elementlist, elementid) #initialize the elementlist
                
                self[elementid, vendorid] = (vendorqty, vendorprice)  

        self.buildarrays()
        self.initialized = True    
        
    def createpricearray(self): #returns numpy array of the prices        
        '''
            n, m = num elements, num vendorlist  
            A = [[item1vendor1price, item1vendor2price, item1vendor3price],
                [item2vendor1price, item2vendor2price, item2vendor3price],...]
                
            A[i,j] = item[i]vendor[j] price    
        '''
        m = len(self.elementlist) #rows
        n = len(self.vendorlist) #columns
        
        pricearray = np.ndarray(shape = (m, n), dtype=np.float) #I used the wrong matrix notation, should I change it now?
        
        for i in range(0, m):
            for j in range(0, n):
                keytuple = (self.elementlist[i], self.vendorlist[j])
                if keytuple in self.keys():
                    pricearray[i,j] = float(self[self.elementlist[i], self.vendorlist[j]][1])
                else:
                    pricearray[i,j] = 0.0
        self.pricearray = pricearray
        
        return pricearray
    
    def createstockarray(self): #returns numpy array of vendor stock   
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
                if keytuple in self.keys():
                    stockarray[i,j] = int(self[self.elementlist[i], self.vendorlist[j]][0])
                else:
                    stockarray[i,j] = 0
        self.stockarray = stockarray
        
        return stockarray
    
    def createwantedarray(self):    #returns numpy array of wanted items
        m = len(self.elementlist)
        
        wantedarray = np.ndarray(shape = (m), dtype=np.int)
        for i in range(0, m):
            elementid = self.elementlist[i]
            wantedarray[i] = self.wanted[elementid]
        self.wantedarray = wantedarray    
        return wantedarray    
    
    def buildarrays(self):
        logging.info("Rebuilding arrays...")
        self.createpricearray()
        self.createstockarray()
        self.createwantedarray()
              
    def describesolution(self, result):
        if self.result:
            pass
    def describevendors(self):
        #print out some information about the vendors
        print("There are " + str(len(self.vendorlist)) + " in Vendorlist")
        
    def getqtyandprice(self, elementid, vendorid):
        assert( (elementid, vendorid) in self.data.keys() ), "ElementID %r, VendorID %r not found" % (elementid, vendorid)
        (qty, price) = self[elementid, vendorid]       
        return (qty, price)
        
    def addtolist(self, alist, value):             
        if value not in alist:
            #string = "Adding value: " + str( value) + " to list " + str( alist)
            #logging.debug(string)
            alist.append(value)
        return True
    

        
    
    def getvendorlist(self):
        return self.vendorlist
    
    def getelementlist(self):
        return self.elementlist
             
    def hasminquantity(self, elementid, vendorid ):
        assert vendorid in self.vendormap, "Cannot determine qantity, vendor %r does not exist in vendorlist" % vendorid
        
        if (elementid, vendorid) in self.data:
            wantedquantity = int(self.wanted[elementid])
            return ( (self[elementid, vendorid][0]) >= wantedquantity )
        else: 
            return False
          
    def removevendor(self, vendorid):
        #doesn't remove it from the .data, only from the list of vendors
        assert vendorid in self.vendorlist, "Vendor %r does not exist in vendorlist" % vendorid
        self.vendorlist.remove(vendorid)
                      
    '''
    def vendorcostmetric(self):
        vendorcostmetric = dict()
        for vendorid in self.vendorlist:
            vendorcostmetric[vendorid] = 0.0        
        for vindex, vendorqty in enumerate(self.stockarray.T):
            vendorid = self.vendorlist[vindex]
            metric = float(0.0)
            itemcount = int(0)
            partcost = float(0.0)
            for eindex, wantedqty in enumerate(self.wantedarray):
                price = self.pricearray[eindex, vindex]
                partcost += price * wantedqty
                itemcount += wantedqty
            metric = partcost/wantedqty
            vendorcostmetric[vendorid] = metric
        
        return vendorcostmetric   
        #define a metric for vendor pricing to weigh relative cost
        #use items on the wanted list and weight them by total cost or something
        #cost if I bought all the items a vendor offers / # of items vendor offers

        
        return vendorcostmetric
    '''
    '''                  
    def cullvendors(self):
        logging.info( "Searching for vendors to cull")
        initialcount = len(self.vendorlist)
        #consider implementing some kind of cull threshhold
        
        vendorcopy = copy.deepcopy(self.vendorlist)
        for vendor in vendorcopy:
            #if the vendor doesnt have min quantity of at least one item, remove them
            gonnaremovevendor = True
            for element in self.elementlist:               
                if self.hasminquantity(element, vendor): 
                    gonnaremovevendor = False
                    break
            if( gonnaremovevendor ):
                #print( "Removing vendor: " + vendor)
                self.removevendor(vendor)
                #self.removeelementvendor(element, vendor)
        finalcount = len(self.vendorlist)
        vendorsremoved = initialcount - finalcount
        self.buildarrays()
        logging.info( "Removed " + str(vendorsremoved) + " vendors from the working list.")
    ''' 
       
    def cullvendorsbyprice(self):
        cheapvendoridx = self.cheapvendorsbyitem()
        #make a new list containing only these vendors
        initial_length = len(self.vendorlist)
        cheapvendors = [ self.vendorlist[i] for i in cheapvendoridx ]
        self.vendorlist = cheapvendors
        self.buildarrays()
        finallength = len(self.vendorlist)
        removed = initial_length - finallength
        print("Removed " + str(removed) + " vendors from the list")
        #print(cheapvendors)
        
    def ma_sortedvendorindices(self):        
        #returns a masked array of the sorted vendor indices, masking the 0.0 values

        p = self.pricearray       
        s = p.argsort(axis=1) # sort array of vendor indices are now sorted by s

        static_indices = np.indices( p.shape )
        psorted = p[static_indices[0], s]     
           
        sortedmask = psorted <= 0.0  #p and pmask share the same indices
        
        m = ma.array( s, mask=sortedmask ) # a masked array of sorted vendor indice
        
        csm = [ ma.compressed( m[i] ) for i in range(0, len(m)) ]
        return csm
 #compressed, sorted, masked array of vendor indices
            
    def cheapvendorsbyitem(self):
        #this is returning seemingly random results
        #keep the cheapest N vendors for each item
        #at most, this leaves us with NumElements x N vendors
        #use the pricearray and loop over vendor list
        nvendors = int(20)
        #v = self.vendorlist
        csm = self.ma_sortedvendorindices() #this is a list of vendor indices, sorted
        
        #trim this array, but shape is no longer m x n because the number of vendors per item won't be to be the same
        vendorindices = list()
        for rowindex, row in enumerate(csm):
            p = self.pricearray
            colindex = row[nvendors]
            lowprice = p[rowindex, colindex] 
            print("Lowprice " + str(lowprice) )
            #get all the vendor indices that are equal to or lower than the low price
            indices = [ vidx for vidx in row if p[rowindex, vidx] <= lowprice ]
            vendorindices.append( indices )
            #print( indices)
        print(vendorindices)
        return vendorindices
        '''
        e = self.elementlist
        tempv = np.ndarray(shape=(0), dtype='int') #running list of vendor indices to keep
        for eindex, element in enumerate(e):
            #for this element, find the N cheapest vendors
            row = self.pricearray[eindex] #slices out a row of the pricearray containing prices
            indexlist = np.nonzero( row ) #gets indices of the non-zero elements
            sortedvals = np.sort(row[indexlist]) #sort the non-zero values
            lowestprice = sortedvals[nvendors] #get the nth lowest price
            indexlist = np.nonzero( (row > 0) & (row <= lowestprice) )

            tempv = np.append(tempv, indexlist) 
            #tempv += keepv

        #flatten, sort, and remove duplicates from tempvarray    
        
        flatv = np.unique( tempv )
        '''

    '''
    def elementweights(self):
        
        avgprices = self.calculateavgprices()
        wanted = self.wantedarray
        
        weights = (avgprices * wanted)/(avgprices * wanted).max()
        
        return weights
    
    def dropifsingle(self):
        #if a vendor only has sufficient qty of one part and it's not the cheapest, drop it
        #find the vendors with quantity in only one part
        #count the rows per vendor that are > wanted qty
        #wanted = self.wantedarray
        ipv = self.itemspervendor()
        avgprices = self.calculateavgprices()
        onepartindexlist = list()
        vendorswithonepart = (ipv <= 1)
        indexlist = np.where(ipv <= 1) #this should be indices
        #print(indexlist)
        for index in indexlist[0]:
            # true means this vendor has only one part            
            vendorprices = self.pricearray.T[index]
            thisprice = vendorprices[np.nonzero(vendorprices)] 
            # get the price of the nonzero element
            print(thisprice)    
                #if self.pricearray[index] 
               
    def cullbymetric(self):
        #remove vendors that are above average price
        initialcount = len(self.vendorlist)
        avgprices = self.calculateavgprices()
        vendorcopy = copy.deepcopy(self.vendorlist)
        for vindex, vendorid in enumerate(vendorcopy):
            prices = self.pricearray.T[vindex]
            if all(prices > avgprices):               
                self.removevendor(vendorid)
                break;
            
        self.buildarrays()
        finalcount = len(self.vendorlist)
        vendorsremoved = initialcount - finalcount
        logging.info( "Removed " + str(vendorsremoved) + " vendors from the working list.")
        
        return 
    
    def describevendors(self):
        
        print( "There are " + str(len(self.vendormap)) + " vendors with sufficient quantity of at least one element in our list.")
        
        for v in self.vendormap.keys():
            assert v in self.vendorcountsitems, "Vendor does not exist in counting dictionary"
            #print self.vendormap[v] + " has enough quantity of " + str(self.vendorcountsitems[v]) + " elementlist"
    '''
    def calculateavgprices(self):
        #data[elementid, vendorid] = [price, qty]
        p = self.pricearray
        avgprices = p.sum(1)/(p > 0).sum(1) #the 1 causes
        return avgprices
        #for item in self.item
    
    def itemspervendor(self):
        s = self.stockarray
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
        for item in self.data.items():
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
            thiselement = self[e]
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
            for e in self.data.keys():
                thiselement = self[e]
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
