"""
Created on May 16, 2013

@author: khooks
"""

from .solution import Solution, SolutionSet
from .vendors import VendorStats


class SearchTypes():
    (Shift, Swap) = list(range(0,2))

class Optimizer():
    #TODO: Convert this class to use only numpy arrays
    """Uses ndarrays to setup and solve an or-tools problem"""
    
    def __init__(self, bcmdata, search=SearchTypes.Swap):
        #self.solver = orsolver.Solver("Find the best price")
        self.m = len(bcmdata.elementlist)
        self.n = len(bcmdata.vendorlist)
        self.__v = bcmdata.vendorlist
        self.__e = bcmdata.elementlist
        self.__BCMDICT = bcmdata.BCMDICT
        self.__WANTDICT = bcmdata.WANTDICT
        self.__vs = VendorStats(bcmdata)
        self.solutions = SolutionSet()
        self.search_type = search
        #self.P = bcmdata.PRICES
        #self.S = bcmdata.STOCK
        #self.W = bcmdata.WANTED
        #self.X = None
        #self.B = None
        #self.VSORTED = bcmdata.VENDSORTLIST
         
    def solve(self):
        #TODO: cullvendors
        self.search()

    def fillOrders(self, order, vendor):
        #TODO: Convert this to use only the numpy arrays
        #buy all available elements from the current vendor
        for element, qty in list(order.needed().items()):            
            if (element, vendor) in self.__BCMDICT:
                vendorstock, price = self.__BCMDICT[element, vendor]
                purchase = min( qty, vendorstock )
                wanted = self.__WANTDICT[element]
                #if purchase >= self.__WANTDICT[element]/3:  #has at least half the desired qty
                if purchase >= ( wanted/2 ):  #has at least half of the wanted qty   
                    order.addpurchase( element, vendor, purchase, price )
            
        return
        
    def search(self):
        vlist = self.__v
        stockweights = self.__vs.vendorstockweights()
        sortedtuples = sorted( zip(stockweights, vlist ), reverse=True)
        weights, vendors = list(zip(*sortedtuples)) #unzip the sorted tuples
        initialsearchorder = list(vendors) #convert to a list
        # while still need elements
        # get a vendor search order
        # could truncate the vendor list here if we wanted to
        #firstsearchorder = firstsearchorder[:6] #limit how deep to swap vendors.  8 or higher will blow it up on the Shift search

        #establish the generator to be used
        if self.search_type == SearchTypes.Shift:
            gen = self.shiftorder(initialsearchorder[:6])
        elif self.search_type == SearchTypes.Swap:
            gen = self.orderswaps(initialsearchorder[:25])
        else: gen = self.orderswaps(initialsearchorder[:25])

        for searchorder in gen: #gets search order from generator
            #print("Next search order: ")
            #print(searchorder)
            order = Solution(self.__WANTDICT) #create empty solution
            for vendor in searchorder:
                #print("Filling order from next vendor: %s" % vendor)
                if order.incomplete():
                    self.fillOrders(order, vendor)
                else: #order is complete, now wrap it up
                    order.vendorsearchorder = searchorder[:] # assign it to a copy of this search order
                    break
            if order.isfeasible(): 
                #print("Feasible order found")
                self.solutions.add(order)
            #break #until I can limit the number of loops
            #count += 1
            #if count > limit: break
            
            #print( order )
            #if len(self.solutions) >= 500: return
            
        return True #if a feasible solution is found
    
    def cost(self, order):
        
        return order.cost()
    
    
    def shiftorder(self, seq):
        """unfortunately, the generator starts shifting values at the far end of the range, 
           when it's preferable to shift them at the beginning"""
        
        if len(seq) == 1:
            yield seq
        
        for indexoffset in reversed(list(range( len(seq)))):
            newseq = seq[:]
            newseq.insert( 0, newseq.pop(indexoffset))
            for tail in self.shiftorder( newseq[1:]):
                yield [newseq[0]] + tail
    
    def orderswaps(self, seq, depth=25):       
        
        yield seq #need to return an unmodified version
        
        depth = min( depth, len(seq) )
        
        for offset in range(1, depth):                
            for i in range(depth):
                for j in range(offset, depth-offset):               
                    if i == j:
                        break
                    newseq = seq[:]
                    newseq[i], newseq[j] = newseq[j], newseq[i]      
                    yield newseq
    
