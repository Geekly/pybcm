'''
Created on Oct 30, 2012

@author: khooks
'''
from collections import UserDict
from legoutils import Element
from vendors import VendorMap

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
    '''
    
    def __init__(self):
        UserDict.__init__(self)
        self.data = dict()           #dictionary of elements (see BCMElement) keyed on elementid#  
        #self.wanted = dict()
        self.vendormap = VendorMap()      #replace this with a class.... somehow
        #self.averageprices = dict()  #self.averageprices[elementid] = { avgprice, numsellers }
        
        self.headers = list()
        #self.vendorlist = list()
        #self.elementlist = list() replace with the .data
        
        self.vendorcountsitems = dict()
        
        #self.width = 0
        #self.height = 0
        #self.cullthreshold = 2
        #self.expensivevendor = 1.5 #get rid of vendors priced at this factor above average
        #self.avgpricesinitialized = False
        self.initialized = False
        
    def buildfrombricklink(self, bricklink, wanteddict): 
        #creates a dictionary keyed to the vendor and an element that contains the qty and price for each vendor/element pair
        #prices.append([vendorid, vendorname, vendorqty, vendorprice])                
        self.headers.append("Vendor")
        self.vendormap = bricklink.vendormap
        
                
        for elementid in bricklink.keys():
            
            self[elementid] = BCMElement( wanteddict[elementid] )  #make a super element from the elements stored in wanteddict
            
            
               
            for vendorinfo in bricklink[elementid]:  #this is a list
                
                vendorid = vendorinfo[0]
                vendorname = vendorinfo[1]
                vendorqty = vendorinfo[2]
                vendorprice = vendorinfo[3] 
                
                self.headers.append(vendorname)
                
                self[elementid].vendorstock[vendorid] = Stock(vendorqty, vendorprice)  
            
        self.width = len(self.headers)
        self.height = (1 + len(self.vendormap) )
        
        #print self.headers
        for vendorid in self.vendormap.keys():
            #print vendorid
            #self.vendorlist.append(vendorid)
            
            self.vendorcountsitems[vendorid] = 0
            
            '''
            for row in bricklink.vendordata[vendorid]:
                elementid = row[0] 
                quantity = row[1]
                cost = row[2]
                self[vendorid, elementid] = (quantity, cost)
                
                if self.hasminquantity(vendorid, elementid):
                    #increment the dict entry
                    self.vendorcountsitems[vendorid] += 1 
            '''                        
        self.initialized = True
    
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
                       
                print( "Element " + str(e.id) + " has an average price of " + str(e.averageprice))
            
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
          
if __name__ == '__main__':
    
    
    tryelement = Element('3006', '88', '2x4 brick', 'P', 'brick', 'Blue', 100)
    print( tryelement)
    print( tryelement.itemid)
    test = BCMElement(tryelement)
    print( test.itemid)
    print( test.colorid)

    
    pass