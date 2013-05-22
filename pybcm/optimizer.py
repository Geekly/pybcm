'''
Created on May 16, 2013

@author: khooks
'''

import numpy as np
from solution import Solution, SolutionSet
from vendors import VendorStats

class Optimizer():
    """Uses ndarrays to setup and solve an or-tools problem"""
    
    def __init__(self, bcmdata):
        #self.solver = orsolver.Solver("Find the best price")
        self.m = len(bcmdata.elementlist)
        self.n = len(bcmdata.vendorlist)
        self.__v = bcmdata.vendorlist
        self.__e = bcmdata.elementlist
        self.__BCMDICT = bcmdata.BCMDICT
        self.__WANTDICT = bcmdata.WANTDICT
        self.__vs = VendorStats(bcmdata)
        self.solutions = SolutionSet()
        #self.P = bcmdata.PRICES
        #self.S = bcmdata.STOCK
        #self.W = bcmdata.WANTED
        #self.X = None
        #self.B = None
        #self.VSORTED = bcmdata.VENDSORTLIST
         
    def solve(self):
        
        return (self.search())
        
    def Vendors(self):
        for vrow in self.VSORTED:
            #return a vendor for elements that are still unfilled
            vidx = vrow[0]
            vendor = self.__v[vidx]
            #vendor = self.__v[vidx]
            yield vendor
    
    def fillOrders(self, order, vendor):
        #buy all available elements from the current vendor
        for element, qty in order.needed().items():            
            if (element, vendor) in self.__BCMDICT:
                vendorstock, price = self.__BCMDICT[element, vendor]
                purchase = min( qty, vendorstock )
                if purchase > 0:  #has all of the qty
                    order.addPurchase( element, vendor, purchase, price )
            
        return
        
    def search(self):
        vlist = self.__v
        stockweights = self.__vs.vendorstockweights()
        sortedtuples = sorted( zip(stockweights, vlist ), reverse=True)
        weights, vendors = zip(*sortedtuples) #unzip the sorted tuples
        firstsearchorder = list(vendors) #convert to a list
        # while still need elements
        # get a vendor search order
        for searchorder in self.searchorder(firstsearchorder):
            order = Solution(self.__WANTDICT)
            for vendor in searchorder:
                if order.incomplete():
                    self.fillOrders(order, vendor)
                else: #order is complete, now wrap it up
                    order.searchorder = searchorder[:] # assign it to a copy of this search order
                    break
            self.solutions.add(order)
            #break #until I can limit the number of loops
            
            #print( order )
            if len(self.solutions) > 10: return
            
        return order
    
    def cost(self, order):
        
        return order.cost()
    
    def searchorder(self, initialorder):
        #each time, pick the next vendor and put it at the beginning of the search order
        #searchorder = initialorder[:]
        indextomove = 0
        while 1:
            searchorder = initialorder[:]
            if indextomove != 0: searchorder.insert(0, searchorder.pop(indextomove) ) #inserts indexttomove at the beginning of the list
            indextomove += 1
            yield searchorder
            #if indextomove >= 5: return
        #yield a new search order (list of vendors)
           