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
        

        self.m = len(bcmdata.elementlist)
        self.n = len(bcmdata.vendorlsit)
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
        
        
        #establish wanted/stock constraints and bound X by the stock or wanted constraint
        for (element, vendor) in bcmkeys: #iterate over elements                 
            string = 'w.%s.%s' % (element, vendor) 
            stock = bcmdict[element, vendor][0]                   
            #print(( 0, xlimit, string )) 
            ''' Changed the logic here to only include vendors with all of the quantity needed.  This pruning should
                really be done outside of this function
                '''
            buylimit = wanted[element]
            if( stock >= buylimit ): 
                #xlimit = min( wanted[element], stock )     
                X[element][vendor] = self.solver.IntVar(0, buylimit, string ) 
                        #wanted constraints on solution
            #elem_vend_dict[element][vendor] = ()
        #have to get the keys from X now since we eliminated some of the vendors
        for element in X:
            for vendor in X[element]: vdict[vendor].append(element)

            self.solver.Add( wanted[element] == self.solver.Sum( [ X[element][vendor] for vendor in X[element] ]))    

        #self.solver.Add( data.wantedarray[eindex] == self.solver.Sum( [ qtyarray[element, vendor] for vendor in data.vendorlist ]))
        #db = self.solver.Phase(X, 
        #                  solver.CHOOSE_FIRST_UNBOUND,
        #                  solver.INT_VALUE_DEFAULT) 
                   
        partcost = 0
        shippingcost = 0
        
        #the price
        #loop over vendors
        partcost = self.solver.Sum( [X[element][vendor] * int(bcmdict[element, vendor][0]*100) for element in X for vendor in X[element] ] ) 
        
        #try to count the number of vendors being used
        v_bools = dict()
        #for vendor in vdict:
        #    v_bools[vendor] = self.solver.BoolVar()
        for vendor in vdict:
            v_bools[vendor] = self.solver.Sum( [X[element][vendor] > 0 for element in vdict[vendor]] ) > 0
        
        vendor_count = self.solver.Sum( [v_bools[b] for b in v_bools])
                
        #temp = self.solver.Sum( [ any( X[element][vendor].Value() > 0 for element in vdict[vendor] ) for vendor in vdict ] )
        #shippingcost = 2.5 * self.solver.Sum( [any( X[element, vendor] > 0.0 for element in vdict[vendor]) for vendor in vdict]  ) 
        #shippingcost = 2.5 * temp
        
        #for vendor in v:
        #    b_vendors.append( self.solver.BoolVar( self.solver.Sum( X[vendor, element] > 0 for element in e ) > 0 ) )
        shippingcost = vendor_count * 3
        cost = partcost + shippingcost
        
        objective = self.solver.Minimize(cost, 1)
        
        solution = self.solver.Assignment()
        solution.AddObjective(cost)
        #solution.Add(X)
        
        sc = self.solver.LastSolutionCollector(solution)
        #sc.add(X)
        
        '''self.solver.Solve( self.solver.Phase(X + [cost],
                                             self.solver.INT_VAR_SIMPLE,
                                             [objective, sc]) )
        '''
        self.solver.Solve( self.solver.Phase(X,
                                             self.solver.INT_VAR_SIMPLE,
                                             self.solver.ASSIGN_MIN_VALUE
                                             ))
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


