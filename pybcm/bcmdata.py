'''
Created on Oct 30, 2012

@author: khooks
'''
from collections import UserDict
from legoutils import LegoElement
from vendors import VendorMap
import numpy as np
import logging

class Stock(object):
    def __init__(self, quantity, price):
        self.quantity = int(quantity)
        self.price = float(price)

class BCMElement(object):
    
    def __init__(self, element):
        
        #self.element = element #reuse the elements from the wanted list      
        #copy the attributes from passed in element
        attributes = dir(element)
        for attr in attributes:
            if (hasattr(self, attr)):
                continue
            value = getattr(element, attr)
            setattr(self, attr, value)
            
        #itemid=None, colorid=None, itemname=None, itemtypeid=None, itemtypename=None, colorname=None, wantedqty=0
        
        self.vendorstock = dict()  #so we can say element.vendorstock[vendor] = Stock(quantity, price)     
        self.averageprice = float(0.0)
        self.availablevendors = int(0)  #number of vendors that have this part above a certain threshold to be defined on assignment

        

class BCMData(UserDict):
    ''' combines the wanteddict with the bricklink data in an easily manipulable object
    
    really want a dictionary that allows access via data[elementid, vendorid] = [price, qty]
    
    '''
    vendormap = VendorMap()
    def __init__(self, bricklink, wanteddict):
        UserDict.__init__(self)
        self.wanted = dict()
        self.vendors = list()  #this is a working list.  We'll cull this from time to time and rebuild it if neccessary
        self.elements = list()
        self.pricearray = None
        self.stockarray = None
        self.buildfrombricklink(bricklink, wanteddict)
        self.initialized = False
    
    def pricenumpy(self): #returns numpy array of the prices
        
        '''
            n, m = num elements, num vendors
    
            A = [[item1vendor1price, item1vendor2price, item1vendor3price],
                [item2vendor1price, item2vendor2price, item2vendor3price],...]
                
            A[i,j] = item[i]vendor[j] price    
        '''
        n = len(self.elements)
        m = len(self.vendors)
        
        pricearray = np.ndarray(shape = (n, m))
        
        for i in range(0, n):
            for j in range(0, m):
                keytuple = (self.elements[i], self.vendors[j])
                if keytuple in self.keys():
                    pricearray[i,j] = float(self[self.elements[i], self.vendors[j]][1])
                else:
                    pricearray[i,j] = 0.0
        self.pricearray = pricearray
        
        return pricearray
    
    def stocknumpy(self):    
        '''
            B = [[item1vendor1stock, item1vendor2stock, item1vendor3stock],
                [item2vendor1stock, item2vendor2stock, item2vendor3stock],...]
                
            B[i,j] = item[i]vendor[j] stock    
        '''
        n = len(self.elements)
        m = len(self.vendors)
        stockarray = np.ndarray(shape = (n, m))
        for i in range(0, n):
            for j in range(0, m):
                keytuple = (self.elements[i], self.vendors[j])
                if keytuple in self.keys():
                    stockarray[i,j] = float(self[self.elements[i], self.vendors[j]][2])
                else:
                    stockarray[i,j] = 0.0
        self.pricearray = stockarray
        
        return stockarray
    
    def buildstockdata(self, bricklink):
        #loop through elements and build A[i,j]
        pass   
    
    def getpriceandqty(self, elementid, vendorid):
        
        (qty, price) = self[elementid, vendorid]
        
        return (qty, price)
     
    def buildfrombricklink(self, bricklink, wanteddict): 
        #creates a dictionary keyed to the vendor and an element that contains the qty and price for each vendor/element pair
        #prices.append([vendorid, vendorname, vendorqty, vendorprice])                
        #self.headers.append("Vendor")
        logging.info("Building BCM dictionary")
        self.vendormap = bricklink.vendormap
        
        #create the price array
        #create the stock array        
        for elementid in bricklink.keys():
            
            #self[elementid] = BCMElement( wanteddict[elementid] )  #make a super element from the elements stored in wanteddict
                         
            for vendorinfo in bricklink[elementid]:  #this is a list
                print(vendorinfo)
                vendorid = vendorinfo[0]
                #vendorname = vendorinfo[1]
                vendorqty = vendorinfo[1]
                vendorprice = vendorinfo[2] 
                
                #self.headers.append(vendorname)
                self.addtolist(self.vendors, vendorid)
                self.addtolist(self.elements, elementid)
                
                self[elementid, vendorid] = (vendorqty, vendorprice)  
        
        self.initialized = True    
        
    def addtolist(self, alist, value):
        if value not in alist:
            alist.append(value)
        return True
    
    def getvendors(self):
        return self.vendors
    
    def getelements(self):
        return self.elements
            
    
    
    
    '''                        
       
    
    def hasminquantity(self, vendorid, elementid ):
        assert vendorid in self.vendormap, "Cannot determine qantity, vendor %r does not exist in vendorlist" % vendorid
        
        if (elementid) in self.data:
            if (vendorid) in self[elementid].vendorstock.keys():
                wantedquantity = self[elementid].wantedqty
                return ( self[elementid].vendorstock[vendorid].quantity >= wantedquantity )
        else: 
            return False
         
        
    def removevendor(self, vendorid):
        #doesn't remove it from the .data, only from the list of vendors
        assert vendorid in self.vendormap.keys(), "Vendor %r does not exist in vendorlist" % vendorid
        del self.vendormap[vendorid]
                
    def cullvendors(self):
        print( "Searching for vendors to cull")
        initialcount = len(self.vendormap)
        #consider implementing some kind of cull threshhold
        for v in self.vendormap.keys():
            #if the vendor doesnt have min quantity of at least one item, remove them
            gonnaremovevendor = True
            for e in self.keys():
                if self.hasminquantity(v, e): 
                    gonnaremovevendor = False  #keep the vendor
                    break
            if( gonnaremovevendor == True ):
                #print "Removing vendor: " + v
                self.removevendor(v)

        finalcount = len(self.vendormap)
        vendorsremoved = initialcount - finalcount
        print( "Removed " + str(vendorsremoved) + " vendors.")

    def describevendors(self):
        
        print( "There are " + str(len(self.vendormap)) + " vendors with sufficient quantity of at least one element in our list.")
        
        for v in self.vendormap.keys():
            assert v in self.vendorcountsitems, "Vendor does not exist in counting dictionary"
            #print self.vendormap[v] + " has enough quantity of " + str(self.vendorcountsitems[v]) + " elements"
    
    def calculateavgprices(self):
        
        self.avgpricesinitialized = True
        
        for elementid in self.keys():
            
            e = self[elementid]
            
            e.averageprice = 0.0
                           
            vendorswith = 0.00001
            sum = 0.0
            for vendor in e.vendorstock.keys():    #returns a tuple (vendorid, qty, price)
                (vendorid, qty, cost) = ( vendor, int(e.vendorstock[vendor].quantity), float(e.vendorstock[vendor].price) )  
                
                if (qty >= e.wantedqty):
                    sum += float(cost)
                    vendorswith += 1      #how many vendors have this quantity? 
                    
            if (vendorswith >= 1):
                e.averageprice = sum / vendorswith
                       
                print( "LegoElement " + str(e.id) + " has an average price of " + str(e.averageprice))
            
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
    
    
    tryelement = LegoElement('3006', '88', '2x4 brick', 'P', 'brick', 'Blue', 100)
    print( tryelement)
    print( tryelement.itemid)
    test = BCMElement(tryelement)
    print( test.itemid)
    print( test.colorid)

    
    pass