"""
Created on May 17, 2013

@author: khooks
"""
from collections import defaultdict
import copy


class Solution():
    
    def __init__(self, wanted):
        
        #list of (element, vendor, qty, price) tuples        
        self.data = list()
        self.searchorder = None
        self.__needed = copy.deepcopy(wanted)
        self.__filled = dict.fromkeys( wanted.keys(), 0 )
        
        return
    
    def isfeasible(self):  
        #it's feasible if there are NO non-zero values in self.__needed    
        if any( self.__needed.values() ): return False
        return True
    
    def numOrders(self):
        seen = set()        
        for (element, myvendor, qty, price) in self.data:
            seen.add(myvendor)
        numvendors = len(seen)
        return numvendors
        
    def totalPartCost(self):
        cost = 0.0
        for (element, myvendor, qty, price) in self.data:
            cost += qty * price
        return cost
    
    def costFromVendor(self, vendor):
        cost = 0.0       
        mylist = ( [qty, price] for (element, myvendor, qty, price) in self.data if myvendor==vendor)
        for qty, price in mylist:
            cost += qty * price
        return cost
                          
    def addPurchase(self, element, vendor, qty, price):     
        #reduce the number needed
        #increase the number filled
        self.__filled[element] += qty
        self.__needed[element] -= qty
        self.data.append( (element, vendor, qty, price) )
    
    def incomplete(self):
        return any( [x > 0 for x in self.__needed.values() ])
        
    def needed(self):
        stillneeded = dict()
        for element, qty in self.__needed.items():
            if qty > 0: stillneeded[element] = qty
        return stillneeded
            
    def byElementDict(self):
        """ Return dictionary keyed on element """
        
        edict = defaultdict(list)
        for orderTuple in self.data:
            element = orderTuple[0]
            vendor = orderTuple[1]
            qty = int(orderTuple[2])
            price = float(orderTuple[3])
            edict[element].append(vendor, qty, price)
        return edict
        
    def byVendorDict(self):
        """ Return dictionary keyed on vendor """
        vdict = defaultdict(list)
        for orderTuple in self.data:
            element = orderTuple[0]
            vendor = orderTuple[1]
            qty = int(orderTuple[2])
            price = float(orderTuple[3])
            vdict[vendor].append( (element, qty, price) )
        return vdict
    
    def vitalStats(self):
        n = self.numOrders()
        p = self.totalPartCost()
        return n,p
    
    def __str__(self):
        
        vdict = self.byVendorDict()
        
        s = "Solution results:\n"

        s += "\n"
        
        for vendor in vdict:
            numitems = len(vdict[vendor])
            s += "VendorID: %s\n" % vendor             
            for element, qty, price in vdict[vendor]:
                s += "    "
                s += "Qty: %d" % qty + " of Element: " + element + " Price: $%.2f" % price + " Total: $%.2f\n" % (qty * price)
            
            s += "Found %d items for Total: $%.2f\n" % (numitems, self.costFromVendor(vendor))
            s += "\n"
        s += "Number of Orders: %d\n" % self.numOrders()
        s += "Total Part Cost: $%.2f\n" % self.totalPartCost()

        return s
    
class SolutionSet():
    
    def __init__(self):
        self.data = list()
        #persistant info for comparing new solutions
        self.bestsolution = None
        self.bestcost = 1000
        self.costperorder = 3.0
                
    def add(self, solution):
        self.data.append(solution)
        #check to see if this is the best solution so far
        numorders, partcost = solution.vitalStats()
        cost = numorders*self.costperorder + partcost
        if cost < self.bestcost:
            self.bestsolution = solution
            self.bestcost = cost
    
    def summary(self):        
        s = ""
        numsolutions = len(self.data)
        s += "%d Complete Order Found\n\n" % numsolutions
        
        sortedsolutions = sorted([ (soln.vitalStats()[0]*self.costperorder + soln.vitalStats()[1], soln) for soln in self.data])
        print (sortedsolutions)
        (costs, solnlist) = zip(*sortedsolutions)
        for index, soln in enumerate(solnlist[:20]): #first ten solutions
            numvendors, partcost = soln.vitalStats()
            totalcost = numvendors*self.costperorder + partcost
            s += "Solution %d, Number of Separate Orders: %d, Part Cost: $%.2f, Total: $%.2f\n" % (index, numvendors, partcost, totalcost)
        return s
    
    def totalOrderCost(self, solution):
        (n, p) = solution.vitalStats()
        totalCost = n * self.costperorder + p
        return totalCost
    
    def __len__(self):
        return len(self.data)
        
    def best(self):
        soln = self.bestsolution
        s = ""
        s += str(soln)
        s += "\n"
        s += "Total Cost @ $%.2f per order: $%.2f\n" % (self.costperorder, self.totalOrderCost(soln))
        return s