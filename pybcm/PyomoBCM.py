'''
Created on Apr 19, 2013

@author: khooks
'''

from __future__ import division

from coopr import *
from coopr.pyomo import *
from coopr.opt import *


import numpy as np
import pprint

class PyomoBCM(object):
    
    def __init__(self):
        
        self.opt = SolverFactory('glpk')
        model = AbstractModel()
       
        model.E = Set()
        model.V = Set()
               
        model.W = Param( model.E, within=NonNegativeIntegers ) #wanted quantity
        model.S = Param( model.E, model.V, within=NonNegativeIntegers ) #the stock
        model.P = Param( model.E, model.V, within=NonNegativeReals ) #the price
               
        '''def v_init(model):
            for j in model.V:
                for i in model.E:
                    if model.X[i,j] > 0.0:
                        return True
                    return False
        '''        
        #model.vbool = Var( model.V, within=Boolean)#is this vendor used

        def xbounds(model, i, j):
            if model.S[i,j] >= 0:
                return ( 0, min( value(model.S[i,j]), value(model.W[i])) )
            else:
                return (0,0)

        model.X = Var(model.E, model.V, initialize=0, within=NonNegativeIntegers, bounds=xbounds) #purchased quantity
        
        #def s_constraint_rule(model, i, j):
        #    return model.X[i,j] <= model.S[i,j] #can't buy more than the vendor has         

        #model.CANORDER = Constraint(model.E, model.V, rule=s_constraint_rule)
        
        #def v_constraint_rule(model, i, j):
            #if we're buying some, then the vendor better have some      
        #    if model.S[i,j] > 0:
        #        return model.X[i,j] <= model.S[i,j]
        #    else: 
        #        return model.X[i,j] == 0    
           
        #model.CANORDER = Constraint(model.E, model.V, rule=v_constraint_rule)
        
        def w_constraint_rule(model, i):
            #for each row, sum of X == W[i]
            return sum( model.X[i,j] for j in model.V) == model.W[i] #check that the total orders meets the wanted qty
        
        model.WANTED = Constraint(model.E, rule=w_constraint_rule)
               
        def objective_expr(model):
            
            partcost = summation( model.P, model.X )
            #partcost = sum( model.X[i,j] * model.P[i,j] for i in model.E for j in model.V )
            shipcost = sum( [ value(model.X[i,j] ) for i in model.E] > 0 for j in model.V  ) 
            #test =  ( [ model.X[i,j] > 0.0 for i in model.E] > 0 for j in model.V  ) *3
            
            #obj = sum( (sum( model.X[i,j] * model.P[i,j] for i in model.E for j in model.V ), sum( [ model.X[i,j] > 0.0 for i in model.E] > 0 for j in model.V  ) *3) )
            
            obj = shipcost
            #obj = sum( (partcost, shipcost) )
            return obj
        
        model.OBJ = Objective(rule=objective_expr)
        
        self.model = model
        self.results = None
    
     
            
if __name__ == "__main__":
       

    
    opt = PyomoBCM()
   
    data = ModelData(model=opt.model)
    #opt.solve()
    data.add("../output/prices.xls", range="Element", set='E' )
    data.add("../output/prices.xls", range="Vendor", set='V' )
    data.add("../output/prices.xls", range="Price", format='array', param='P' )
    data.add("../output/stock.xls", range="Stock", format='array', param='S')
    data.add("../output/wanted.xls", range="Wanted", index=['E'], param=['W'] )
    
    
    data.read()
    
    
    instance = opt.model.create(data)
    instance.pprint()
    
    results = opt.opt.solve(instance)
    print (results)
    #instance.solve()
    #pprint( instance )