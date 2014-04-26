"""
Created on May 17, 2013

@author: khooks
"""
from collections import defaultdict
import copy


class Solution():
    """A Solution contains the results of a wanted list-driven search

        Attributes:
            data (list): element, vendor, qty, price tuples
            searchorder:
            __needed is a running list of unfufilled quantity
            __filled is the quantity already filled
    """

    def __init__(self, wanted):

        #list of (element, vendor, qty, price) tuples
        self.data = list()
        self.searchorder = None
        self.__needed = copy.deepcopy(wanted)
        self.__filled = dict.fromkeys(wanted.keys(), 0)

        return

    def isfeasible(self):
        """It's feasible if there are NO non-zero values in self.__needed"""
        if any(self.__needed.values()):
            return False
        return True

    def numOrders(self):
        """Return the total number of seperate orders in the solution"""
        seen = set()
        for (element, myvendor, qty, price) in self.data:
            seen.add(myvendor)
        numvendors = len(seen)
        return numvendors

    def totalPartCost(self):
        """Sum the total part cost the solution.

            Does not account for shipping.
        """
        cost = 0.0
        for (element, myvendor, qty, price) in self.data:
            cost += qty * price
        return cost

    def costFromVendor(self, vendor):
        """Sum the total amount bought from this vendor."""
        cost = 0.0
        mylist = ([qty, price] for (element, myvendor, qty, price) in self.data if myvendor == vendor)
        for qty, price in mylist:
            cost += qty * price
        return cost

    def addPurchase(self, element, vendor, qty, price):
        """Include this purchase in the solution

            __filled is increased by the quantity and __needed is reduced
        """
        self.__filled[element] += qty
        self.__needed[element] -= qty
        self.data.append((element, vendor, qty, price))

    def incomplete(self):
        return any( [x > 0 for x in self.__needed.values() ])

    def needed(self):
        """Return dictionary of needed quantities by element. """
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
        """Return various vital stats including number of orders and cost."""
        n = self.numOrders()
        p = self.totalPartCost()
        return n, p

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
        """Add the solution to the set.

            After adding the solution to the set, check to see if it's the
            best solution.  If so, assign bestsolution and bestcost
        """
        self.data.append(solution)
        #check to see if this is the best solution so far
        numorders, partcost = solution.vitalStats()
        cost = numorders*self.costperorder + partcost
        if cost < self.bestcost:
            self.bestsolution = solution
            self.bestcost = cost

    def summary(self):
        """Create a summary string of the results."""
        s = ""
        numsolutions = len(self.data)
        s += "%d Complete Order Found\n\n" % numsolutions

        sortedsolutions = sorted([(soln.vitalStats()[0]*self.costperorder + soln.vitalStats()[1], soln) for soln in self.data])
        print (sortedsolutions)
        (costs, solnlist) = zip(*sortedsolutions)
        for index, soln in enumerate(solnlist[:20]): #first ten solutions
            numvendors, partcost = soln.vitalStats()
            totalcost = numvendors*self.costperorder + partcost
            s += "Solution %d, Number of Separate Orders: %d, Part Cost: $%.2f, Total: $%.2f\n" % (index, numvendors, partcost, totalcost)
        return s

    def totalOrderCost(self, solution):
        """Calculate the total cost of a solution, including shipping."""
        (n, p) = solution.vitalStats()
        totalCost = n * self.costperorder + p
        return totalCost

    def __len__(self):
        return len(self.data)

    def best(self):
        """Return the best solution."""
        soln = self.bestsolution
        s = ""
        s += str(soln)
        s += "\n"
        s += "Total Cost @ $%.2f per order: $%.2f\n" % (self.costperorder, self.totalOrderCost(soln))
        return s
