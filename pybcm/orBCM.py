'''
Created on Apr 23, 2013

@author: khooks
'''

from google.apputils import app
import gflags
from linear_solver import pywraplp

class OROptimizer():
    
    def __init__( self, bcmdata ):
        self.solver = pywraplp.Solver("Get best price", pywraplp.Solver.GLPK_MIXED_INTEGER_PROGRAMMING)
        self.bcm = bcmdata
        
        
    def setup(self):      
        #set up the problem
        #create the solution domain
        m = len(self.bcm.elementlist)
        n = len(self.bcm.vendorlist)
        
        price = self.bcm.data #price dictionary #does not include every combination of element, vendor - only ones with stock
        
        e = self.bcm.elementlist
        v = self.bcm.vendorlist
        
        P = self.bcm.pricearray #mxn
        S = self.bcm.stockarray #mxn
        W = self.bcm.wantedarray #m
        
        X = {} # "X", solution 
        #qtyarray = [[ 0 for j in range(0, n)] for i in range(0,m)]
        
        #establish wanted/stock constraints and bound X by the stock or wanted constraint
        for eindex, element in enumerate( e ): #iterate over elements           
            for vindex, vendor in enumerate( v ): #iterate over vendors
                string = 'w.%s.%s' % (element, vendor) 
                wantedqty = int(W[eindex])
                maxstock = int( S[eindex, vindex])
                xlimit = min( wantedqty, maxstock )               
                X[element,vendor] = self.solver.IntVar(0, xlimit, string ) 
                        #wanted constraints on solution
            self.solver.Add( wantedqty == self.solver.Sum( [ X[element, vendor] for vendor in v ]))    

        #self.solver.Add( data.wantedarray[eindex] == self.solver.Sum( [ qtyarray[element, vendor] for vendor in data.vendorlist ]))
        #db = self.solver.Phase(X, 
        #                  solver.CHOOSE_FIRST_UNBOUND,
        #                  solver.INT_VALUE_DEFAULT) 
                   
        partcost = 0.0
        shippingcost = 0.0
        
        #the price
        partcost = self.solver.Sum( [ X[element, vendor] * float(price[element, vendor][0]) for (element, vendor) in price.keys() ] ) 
        
        num_orders = 0
        b_vendors = list()
        #count the vendors with quantity > 0 in the X array
        #make a list of boolean variables that tell whether a vendor is used or not
        
        for vindex, vendor in enumerate(v): #create a list of vendors that have some quantity in X[,vendor]            
            b_vendors.append( self.solver.Sum( [ X[element, vendor] > 0 for element in e if (element, vendor) in X.keys() ] ) )
        
        
        shippingcost = 2.5 * self.solver.Sum( b_vendors ) 

        
        #for vendor in v:
        #    b_vendors.append( self.solver.BoolVar( self.solver.Sum( X[vendor, element] > 0 for element in e ) > 0 ) )
        
        z = partcost + shippingcost
        
        objective = self.solver.Minimize(z)
        
        self.solver.Solve()
        
        print( shippingcost )
        
        print( 'Cost: ', float(self.solver.ObjectiveValue()))
        
        print( self.solver.NumConstraints() )
        
        print( [X[element, vendor].SolutionValue() for element, vendor in price.keys()] ) 
        #self.solver.Add(qtyarray)
        #create the wanted constraints
        #create the available quantity (stock) constraints
        #create the cost function
        
        
        
        return
    
    def solve(self):
        self.setup()
        
 
        
        return