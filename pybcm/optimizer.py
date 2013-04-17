'''
Created on Oct 23, 2012

@author: khooks
'''

#from shoppinglist import ShoppingList
#from bcmdata import BCMData
import numpy as np
import logging

class Optimizer(object):   
    ''' 
    BCMData reference
        self.data = dict()
        self.wanted = dict()
        self.vendors = list()  #this is a working list.  We'll cull this from time to time and rebuild it if neccessary
        self.elementlist = list()
        self.pricearray = None #a numpy array
        self.stockarray = None #a numpy array
        self.wantedarray = None #a numpy array
    '''
    def __init__(self, mode='cheapestpart'):
        
        self.optimizemethod = mode
        self.maxvendorsperitem = 1
        self.wantedarray = None #needed to check feasibilty of solution
        self.result = None
        self.vendorweight = 3.0  #cost to add additional vendors, approximating average per/order shipping & handling cost
        
    def cost(self, pricearray, resultarray):
        #print(resultarray)
        #print(pricearray)       
        product = resultarray * pricearray  #elementwise multiplication
        #count nonzero columns
        nvendors = np.count_nonzero( np.any( product > 0, axis=0 ) )
        #print(product)
        partcost = np.sum(product)#sum all the elments
        ordercost = nvendors * 3.0
        return (partcost, ordercost, nvendors)
        #print(cost)
    
    def orderedsearch(self, elementorder, msorted, bcmdata):
        #pick a starting vendor.  Try and get all the parts this vendor has
        #go to the next vendor and do the same until all quantities wanted are filled
        #create an order of parts implicitly minimizing the number of vendors used
        #evaluate cost
        #change vendors and repeat
        self.wantedarray = bcmdata.wantedarray
        w = bcmdata.wantedarray
        s = bcmdata.stockarray
        m = len( elementorder )
        n = msorted.shape[1]
        dfilled= dict()
        result = np.zeros(shape=(m, n), dtype=np.int)
        for e in elementorder:
            wanted = w[e]
            dfilled[e] = 0.0
            for v in msorted[e].compressed():
                stock = s[e, v]
                need = wanted - dfilled[e]
                if need <= stock: #just buy what we still need
                    trytobuy = need                
                else:
                    trytobuy = stock #buy all they have
                dfilled[e] += trytobuy
                result[e,v] = trytobuy
                print( result[e,v], e, v)
        return result
                
    def simplesearch(self, bcmdata):
        #for each item in the wanted list
        #find the cheapest vendor that contains enough stock to satisfy the wanted quantity
        #return a numpy array n x m containing the quantity purchased from that vendor
        #    n - number of elementlist
        #    m - number of vendors     
        self.wantedarray = bcmdata.wantedarray   
        m = len(bcmdata.elementlist)
        n = len(bcmdata.vendorlist)
        result = np.zeros(shape=(m, n), dtype=np.int)
               
        #indices = bcmdata.wantedarray
        for eindex, wantedqty in np.ndenumerate(bcmdata.wantedarray):  #list of elementlist wanted
            elementindex = eindex[0] #index is a tuple and the first element is the element index.  this is the universal 
            #print(elementindex)
            lowestprice = (100, 0) #price, vendorindex
            #get a list of vendors that meet the minimum qty
            #find the cheapest
            #in result[][], set the purchase qty for that vendor equal to the wantedqty
            vendors = bcmdata.stockarray[elementindex] #this is just a list
            for vendorindex, vendorstock in enumerate(vendors): #this is an integer
                if ( vendorstock >= wantedqty ):
                    price = bcmdata.pricearray[elementindex, vendorindex]
                    if price <= lowestprice[0]:
                        lowestprice = (price, vendorindex)
                #print("VendorID, Index", bcmdata.vendorlist[vendorindex], vendorindex)            
            result[elementindex, lowestprice[1]] = wantedqty
            #print(vendors)
            #print("Element: " + elementindex + " value: " + element )
            #wantedqty = element[0]
            #print("wanted: ", wantedqty)
            #find the lowest price vendor that satisfies the wanted qty        
        self.result = result
        #trim the result array?
        #print(str(result))
        (cost, ordercost, nvendors) = self.cost(bcmdata.pricearray, result)
         
        logging.info("Solution found.  Total part cost is $" + str(cost) + " using " + str(nvendors) + " vendors") 
        logging.info("Shipping costs are ~$" + str(ordercost))
        return result

    def isfeasible(self, result):
        # if total quantities = wantedqty
        partqty = result.sum(axis=1)
        return partqty
        
if __name__ == "__main__":
       
    A = np.array([[.12, .25, .03], [.14, .30, .04], [.11, .45, .035]])
    x = np.array([[0, 65, 15],[0, 15, 0],[25,0,0]])
    print(A)
    print(x)
    C = np.multiply(A,x)
    print(C)
    print(np.sum(C))
    