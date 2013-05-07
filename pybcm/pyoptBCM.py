'''
Created on May 6, 2013

@author: khooks
'''
import pyopt




class BCMopt():

    def __init__(self, bcmdata):
                
        self.bcm = bcmdata
        self.problem = None
        
        return
      
    
    def objfuc(self, X):
        f = []
        g = []
    #TODO: Calculate some stuff
        fail = False
        return f, g, fail
    
    def solve(self):
        
        self.problem = pyopt.Optimization('BCM Problem', self.objfunc )
        
        
        slsqp = pyOpt.MIDACO() 