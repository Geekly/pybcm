'''
Created on Apr 23, 2013

@author: khooks
'''

from google.apputils import app
import gflags

from collections import defaultdict
import operator
from constraint_solver import pywrapcp as orsolver
#from linear_solver import pywraplp as orsolver
class OROptimizer():
    
    def __init__( self, bcmdata ):
        #data[elementid, vendorid] = (price, qty)
        self.solver = orsolver.Solver("Get best price")#, orsolver.Solver.GLPK_MIXED_INTEGER_PROGRAMMING)
        
        self.__v = bcmdata.vendorlist
        self.__e = bcmdata.elementlist
        
        self.__BCMDICT = bcmdata.BCMDICT
        self.__ELEMDICT = bcmdata.ELEMDICT
        self.__VENDICT = bcmdata.VENDICT
        self.__WANTDICT = bcmdata.WANTDICT
                
        self.__PRICES = bcmdata.PRICES
        self.__STOCK = bcmdata.STOCK
        self.__WANTED = bcmdata.WANTED
        
        self.__X = dict()  #solution
        
    def setup(self):      
        #set up the problem
        #create the solution domain
        bcmdict = self.__BCMDICT #price dictionary #does not include every combination of element, vendor - only ones with stock
        wanted = self.__WANTDICT       
        bcmkeys = bcmdict.keys()
        
        X = defaultdict(dict) # "X", solution X[element]->[vendor]->(quantity)
        #ekeys = sorted(bcmkeys) #keys of X sorted on element
        #vkeys = sorted(bcmkeys, key=lambda x: x[1]) #keys of X sorted on vendor
        vdict = defaultdict(list)
        for element, vendor in bcmkeys: vdict[vendor].append(element)
        
        #establish wanted/stock constraints and bound X by the stock or wanted constraint
        for (element, vendor) in bcmkeys: #iterate over elements                 
            string = 'w.%s.%s' % (element, vendor) 
            maxstock = bcmdict[element, vendor][0]
            xlimit = min( wanted[element], maxstock )        
            print(( 0, xlimit, string ))       
            X[element][vendor] = self.solver.IntVar(0, xlimit, string ) 
                        #wanted constraints on solution
            #elem_vend_dict[element][vendor] = ()
        for (element) in X:
            self.solver.Add( wanted[element] == self.solver.Sum( [ X[element][vendor] for vendor in X[element] ]))    

        #self.solver.Add( data.wantedarray[eindex] == self.solver.Sum( [ qtyarray[element, vendor] for vendor in data.vendorlist ]))
        #db = self.solver.Phase(X, 
        #                  solver.CHOOSE_FIRST_UNBOUND,
        #                  solver.INT_VALUE_DEFAULT) 
                   
        partcost = 0.0
        shippingcost = 0.0
        
        #the price
        #loop over vendors
        partcost = self.solver.Sum( [ X[element][vendor] * float(bcmdict[element, vendor][0]) for (element, vendor) in bcmkeys ] ) 
        
        num_orders = 0
        #b_vendors = dict() #b_vendors[vendor] = True/False
        #count the vendors with quantity > 0 in the X array
        #make a list of boolean variables that tell whether a vendor is used or not
        
        
        
        #for vendor in enumerate(v): #create a list of vendors that have some quantity in X[,vendor]            
            #b_vendors.append( self.solver.Sum( [ X[element][vendor] > 0 for element in e if (element, vendor) in X.keys() ] ) )
        #X[element][vendor]
        
        #shippingcost = 2.5 * self.solver.Sum( [X[element][vendor] > 0 for vendor in vdict for element in vdict[vendor]] ) 
        
        
        shippingcost = 2.5 * self.solver.Sum( [any( X[element, vendor] > 0.0 for element in vdict[vendor]) for vendor in vdict]  ) 

        
        #for vendor in v:
        #    b_vendors.append( self.solver.BoolVar( self.solver.Sum( X[vendor, element] > 0 for element in e ) > 0 ) )
        
        z = partcost + shippingcost
        
        objective = self.solver.Minimize(z)
        
        sc = self.solver.BestValueSolutionCollector()
        #sc.add(X)
        
        self.solver.Solve()
        print(partcost)
        print(X)
        #print(b_vendors)
        print( "Shipping Cost: $%f.2" % shippingcost )
        
        print( 'Cost: ', float(self.solver.ObjectiveValue()))
        
        print( self.solver.NumConstraints() )
        
        #print( [X[element][vendor].SolutionValue() for element in X.keys() for vendor in element.keys()] ) 
        #self.solver.Add(qtyarray)
        #create the wanted constraints
        #create the available quantity (stock) constraints
        #create the cost function
        
        
        
        return
    
    def solve(self):
        self.setup()
        
 
        
        return