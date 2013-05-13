'''
Created on Oct 23, 2012

@author: khooks
'''

#from shoppinglist import ShoppingList
#from bcmdata import BCMData
from __future__ import division
import numpy as np
import logging
from itertools import permutations

from coopr.pyomo import *
from coopr.opt import SolverFactory

class Optimizer(object):   
    """
    Perform optimization on a BCMData object
    
    """

    def __init__(self, bcmdata, mode='cheapestpart'):
        
        #self.data = bcmdata
        self.optimizemethod = mode
        self.maxvendorsperitem = 1
        self.wantedarray = None #needed to check feasibilty of solution
        self.result = dict()  #bcm dict on quantity
        self.vendorweight = 3.0  #cost to add additional vendors, approximating average per/order shipping & handling cost
        
    def cost(self, pricearray, resultarray):
        """Return partcost, shippingcost, and numvendors based on pricearray and resultarray"""
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
    
    def numvendors(self, pricearray, resultarray):
        """Count the number of vendors with a non-zero result"""
        product = resultarray * pricearray
        nvendors = np.count_nonzero( np.any( product > 0, axis=0 ) )
        return nvendors
    
    def bucketsearch(self, data ):
        '''assumptions:
                the elementlist is sorted by price*qty weights
                the vendors in each dict[element] are sorted by price from lowest to highest
        '''
        #elist = data.elementlist
        elems = data.ELEMDICT #keyed on elementid and contains sorted list of
        want = data.WANTDICT  
        bcm = data.BCMDICT
        filled = dict() #number of the given element that's been filled
        #needed = wanted by filled
        r = Result()
        print want
        unfilled = data.elementlist  #once an element is filled, remove it from this list
        fulfilled = dict()
        need = dict()
        
        for element in elems: 
            fulfilled[element] = 0 #initialize.  we haven't bought any yet
            need[element] = want[element]
            
        for eidx, element in enumerate(unfilled): #list of unfilled elements.  Initially contains all of the elements
            #start filling orders/needed
            print("Filling element: " + element)
            for (vendor, qty, price) in elems[element]: #elems[element] is a list of vendors, qty, prices
                need = want[element] - fulfilled[element] #still need to fill this many
                stock = bcm[element, vendor][0] #this is where the stock qty is stored
                buyit = self.trytobuy(need, stock)
                if buyit > 0:
                    print("     Buying " + str(buyit) + " from vendor " + str(vendor))
                    #add this purchase to our results
                    if vendor in r: r[vendor].append( (element, buyit, price) )
                    else: r[vendor] = [ (element, buyit, price) ]
                    #now I've found a vendor of interest.  Buy the current element and every other element they have
                    fulfilled[element] += buyit
                    for eidx2, element2 in enumerate(unfilled[eidx+1:]):
                        if (element2, vendor) in bcm:
                            need = want[element2] - fulfilled[element2] #still need to fill this many
                            stock = bcm[element2, vendor][0] #this is where the stock qty is stored
                            buyit = self.trytobuy(need, stock)
                            if buyit >= 0:
                                print("     Also Buying " + str(buyit) + " of Element " + element2 + " from vendor " + str(vendor))
                                #add this purchase to our results
                                if vendor in r: r[vendor].append( (element2, buyit, price) )
                                else: r[vendor] = [ (element2, buyit, price) ]
                                #now I've found a vendor of interest.  Buy the current element and every other element they have
                                fulfilled[element2] += buyit
                                if fulfilled[element2] >= want[element2]: break
                if fulfilled[element] >= want[element]: break #move on to the next element
            # if more of the element are needed, go to the next vendor and buy all they have
            # update the needed amount
            #print element
               
        return r
    
    def trytobuy(self, need, stock, threshold=1):
        """Compare needed and available(stock) and return amount to buy
        
        Keyword arguments:
        need -- number of items that need to be bought
        stock -- number of available items from the vendor
        threshold - percentage of need that determines whether a vendor is used
            1:  only buy all of what we need, don't settle for less
            0.5: don't buy less than half of what we need
            0:  no influence, buy whatever they have
            
        """
        
        buyit = -1
        threshold = .5
        
        #determine the minimum buy
        if threshold <= 0.0: minbuy = 1
        elif threshold >= 1: minbuy = need
        else: minbuy = int(need * threshold) # when factor = 1, we must by all
        
        if stock <= minbuy: buyit = -1  #skip this vendor
        # stock >= need * factor or we don't buy from this vendor
        else: buyit = min(need, stock) 
        
        return buyit
        
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
        n = msorted.shape[1] #element rows in msorted
        dfilled= dict()
        result = np.zeros(shape=(m, n), dtype=np.int)
        for e in elementorder:
            wanted = w[e]
            dfilled[e] = 0.0
            for v in msorted[e].compressed():
                stock = s[e, v]
                need = int( wanted - dfilled[e])
                if (need <= 0.0 ):
                    break
                elif need <= stock: #just buy what we still need                   
                    trytobuy = need                
                else:
                    trytobuy = stock #buy all they have
                #logging.debug(" Needed: " + str(need) + " and bought " + str(trytobuy) + " of element " + str(e) + " from vendor " + str(v) )
                dfilled[e] += trytobuy
                result[e,v] = trytobuy
                #print( result[e,v], e, v)
        print( self.cost( bcmdata.pricearray, result ))
        self.result = result
        return result
    
    def allfeasible(self, data):
        #search for all feasible solutions in the list of vendors
        #a solution is a dictionary of entries S[element, vendor] = qty
        logging.info("Finding all feasible solutions") 
        
        w = data.wanted
        s = data.stock
        e = data.elementlist
        v = data.vendorlist        
        m = len(data.elementlist)
        n = len(data.vendorlist)
        svl = self.data.sortedvendorlists(data)
        #seperate solutions for each element
        elist = list()
        print svl
        for eidx, element in enumerate(data.elementlist):
            edict = dict()
            for vendor in svl[element]:
                vidx = v.index(vendor)
                if s[eidx][vidx] >= w[eidx]: 
                    edict[element, vendor] = w[eidx] 
                    print edict[element, vendor],
                print s[eidx][vidx] >= w[eidx]
            
            elist.append(edict)
        #print( elist )
        #print( len(elist) )
        return elist
                           
    def simplesearch(self, data):
        #for each item in the wanted list
        #find the cheapest vendor that contains enough stock to satisfy the wanted quantity
        #return a numpy array n x m containing the quantity purchased from that vendor
        #    n - number of elementlist
        #    m - number of vendors  
           
        self.wantedarray = data.wanted   
        m = len(data.elementlist)
        n = len(data.vendorlist)
        resultarray = np.zeros(shape=(m, n), dtype=np.int)
        result = dict()       
        #indices = bcmdata.wantedarray
        for eindex, wantedqty in enumerate(data.wanted):  #list of elementlist wanted
            elementindex = eindex #index is a tuple and the first element is the element index.  this is the universal 
            #print(elementindex)
            lowestprice = (100, 0) #price, vendorindex
            #get a list of vendors that meet the minimum qty
            #find the cheapest
            #in result[][], set the purchase qty for that vendor equal to the wantedqty
            vendors = data.stock[elementindex] #this is just a list
            for vendorindex, vendorstock in enumerate(vendors): #this is an integer
                if ( vendorstock >= wantedqty ):
                    price = data.prices[elementindex, vendorindex]
                    if price <= lowestprice[0]:
                        lowestprice = (price, vendorindex)
                #print("VendorID, Index", bcmdata.vendorlist[vendorindex], vendorindex)            
            result[elementindex, lowestprice[1]] = wantedqty
            resultarray[elementindex, lowestprice[1]] = wantedqty
            #print(vendors)
            #print("Element: " + elementindex + " value: " + element )
            #wantedqty = element[0]
            #print("wanted: ", wantedqty)
            #find the lowest price vendor that satisfies the wanted qty        
        self.result = result
        #trim the result array?
        #print(str(result))
        (cost, ordercost, nvendors) = self.cost(data.prices, resultarray)
         
        logging.info("Solution found.  Total part cost is $" + str(cost) + " using " + str(nvendors) + " vendors") 
        logging.info("Shipping costs are ~$" + str(ordercost))
        return result

    def isfeasible(self, result):
        # if total quantities = wantedqty
        partqty = result.sum(axis=1)
        return partqty >= self.data.WANTED
    
class Result(dict):
    def __init__(self):
        #    def __init__(self):
        dict.__init__(self)
        #self.data = dict()
        #essentially a shopping list using one of these formats (or all of them?)
        #dict[vendor] = [ (element, qty, price), ... ]
        
    def __str__(self):
        string = ""
        for vendor in self.keys():
            string += "Purchased from Vendor: " + str(vendor) + '\n'
            for element in self[vendor]:
                string += str(element[1]) + " of element " + str(element[0]) + " for " + str(element[2]) + '\n'
        
        partcost, shippingcost = self.cost()
        total = partcost + shippingcost
        
        string += '\n'
        string += "Total part cost: $" + "{:3.2f}".format(partcost) + '\n'
        string += "Total shipping cost: $" + "{:3.2f}".format(shippingcost) + '\n'
        string += "Total cost: $" + "{:3.2f}".format(total) + '\n'
        
        return string

    def cost(self):
        partcost = 0.0
        shippingcost = 3.0 * self.numvendors()
        for vendor in self.keys():
            for element in self[vendor]:
                partcost += element[1] * element[2]               
        return partcost, shippingcost
     
    def numvendors(self):
         return len(self)   
                
if __name__ == "__main__":
       
    A = np.array([[.12, .25, .03], [.14, .30, .04], [.11, .45, .035]])
    x = np.array([[0, 65, 15],[0, 15, 0],[25,0,0]])
    print(A)
    print(x)
    C = np.multiply(A,x)
    print(C)
    print(np.sum(C))
    
