# Copyright (c) 2012-2017, Keith Hooks
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Created on May 17, 2013

@author: khooks
"""
import copy
from collections import defaultdict


class Solution():
    """A Solution contains the results of a wanted list-driven search

        Attributes:
            data (list): element, vendor, qty, price tuples
            searchorder:
            vendormap (VendorMap): points to the global vendor_map
            __needed is a running list of unfufilled quantity
            __filled is the quantity already filled
    """

    def __init__(self, wanted, vendormap):

        self.data = list()
        self.searchorder = None
        self._vendormap = vendormap
        self.__needed = copy.deepcopy(wanted)
        self.__filled = dict.fromkeys(list(wanted.keys()), 0)

        return

    @property
    def vendormap(self):
        return self._vendormap

    def isfeasible(self):
        """It's feasible if there are NO non-zero values in self.__needed

            A False value means there are some unfulfilled quantities
        """
        if any(self.__needed.values()):
            return False
        return True

    def numorders(self):
        """Return the total number of seperate orders in the solution
        """
        seen = set()
        for (element, myvendor, qty, price) in self.data:
            seen.add(myvendor)
        numvendors = len(seen)
        return numvendors

    def totalpartcost(self):
        """Sum the total part cost the solution.

            Does not account for shipping.
        """
        cost = 0.0
        for (element, myvendor, qty, price) in self.data:
            cost += qty * price
        return cost

    def costfromvendor(self, vendor):
        """Sum the total amount bought from this vendor."""
        cost = 0.0
        mylist = ([qty, price] for (element, myvendor, qty, price) in self.data if myvendor == vendor)
        for qty, price in mylist:
            cost += qty * price
        return cost

    def addpurchase(self, element, vendor, qty, price):
        """Include this purchase in the solution

            __filled is increased by the quantity and __needed is reduced
        """
        self.__filled[element] += qty
        self.__needed[element] -= qty
        self.data.append((element, vendor, qty, price))

    def incomplete(self):
        return any([x > 0 for x in list(self.__needed.values())])

    def needed(self):
        """Return dictionary of needed quantities by element. """
        stillneeded = dict()
        for element, qty in list(self.__needed.items()):
            if qty > 0:
                stillneeded[element] = qty
        return stillneeded

    def byelementdict(self):
        """ Return dictionary keyed on element """

        edict = defaultdict(list)
        for orderTuple in self.data:
            element = orderTuple[0]
            vendor = orderTuple[1]
            qty = int(orderTuple[2])
            price = float(orderTuple[3])
            edict[element].append(vendor, qty, price)
        return edict

    def byvendordict(self):
        """ Return dictionary keyed on vendor """

        vdict = defaultdict(list)
        for orderTuple in self.data:
            element = orderTuple[0]
            vendor = orderTuple[1]
            qty = int(orderTuple[2])
            price = float(orderTuple[3])
            vdict[vendor].append((element, qty, price))
        return vdict

    def vitalstats(self):
        """Return various vital stats including number of orders and cost."""
        n = self.numorders()
        p = self.totalpartcost()
        return n, p

    def __str__(self):

        vdict = self.byvendordict()

        s = "Solution results:\n"

        s += "\n"

        for vendor in vdict:
            numitems = len(vdict[vendor])
            s += "VendorID: %s\n" % vendor
            for element, qty, price in vdict[vendor]:
                s += "    "
                s += "Qty: %d" % qty + " of Element: " + element + " Price: $%.2f" % price + " Total: $%.2f\n" % (qty * price)

            s += "Found %d items for Total: $%.2f\n" % (numitems, self.costfromvendor(vendor))
            s += "\n"
        s += "Number of Orders: %d\n" % self.numorders()
        s += "Total Part Cost: $%.2f\n" % self.totalpartcost()

        return s


class SolutionSet():
    """A collection of solutions

        SolutionSet is a live collection of solutions that are added to by the optimizer.  It contains functions for
        interacting with individual solutions, as well as identifying a "best" solution within the set.
    """
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
        numorders, partcost = solution.vitalstats()
        cost = numorders*self.costperorder + partcost
        if cost < self.bestcost:
            self.bestsolution = solution
            self.bestcost = cost

    def summary(self):
        """Create a summary string of the results."""
        s = ""
        numsolutions = len(self.data)
        s += "%d Complete Order Found\n\n" % numsolutions

        sortedsolutions = sorted([(soln.vitalstats()[0]*self.costperorder + soln.vitalstats()[1], soln) for soln in self.data])
        print(sortedsolutions)
        (costs, solnlist) = list(zip(*sortedsolutions))
        for index, soln in enumerate(solnlist[:20]):  # first ten solutions
            numvendors, partcost = soln.vitalstats()
            totalcost = numvendors*self.costperorder + partcost
            s += "Solution %d, Number of Separate Orders: %d, Part Cost: $%.2f, Total: $%.2f\n" % (index, numvendors, partcost, totalcost)
        return s

    def totalordercost(self, solution):
        """Calculate the total cost of a solution, including shipping."""
        (n, p) = solution.vitalstats()
        totalcost = n * self.costperorder + p
        return totalcost

    def __len__(self):
        return len(self.data)

    def best(self):
        """Return the best solution."""
        soln = self.bestsolution
        s = ""
        s += str(soln)
        s += "\n"
        s += "Total Cost @ $%.2f per order: $%.2f\n" % (self.costperorder, self.totalordercost(soln))
        return s
