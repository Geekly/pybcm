'''
Created on Oct 23, 2012

@author: khooks
'''

from shoppinglist import ShoppingList
from bcmdata import BCMData
import numpy as np

class Optimizer(object):   
    
    
    def __init__(self, mode='cheapestpart'):
        
        self.optimizemethod = mode
        self.maxvendorsperitem = 1
        
        
    def findcheapestparts(self, wanteddata, bricklinkdata):
        
        shoppinglist = ShoppingList()
        
        for itemid, colorid in wanteddata.keys():
            
            wantedqty = wanteddata[itemid, colorid]['qty']
            itemprices = bricklinkdata[itemid, colorid]  #this is a list of four items [vendorid, vendorname, vendorqty, vendorcost]
            sortedbyprice = sorted(itemprices, key=lambda tup: tup[3])
            
            count = 0
            for itemtuple in sortedbyprice:                
                if itemtuple[2] >= wantedqty:
                    shoppinglist.additem(itemid, colorid, wantedqty, itemtuple[0], itemtuple[1], itemtuple[2], itemtuple[3])
                    count += 1
                    if count >= self.maxvendorsperitem: 
                        break
            
        
        return shoppinglist
        
if __name__ == "__main__":
       
    A = np.array([[.12, .25, .03], [.14, .30, .04], [.11, .45, .035]])
    x = np.array([[0, 65, 15],[0, 15, 0],[25,0,0]])
    print(A)
    print(x)
    C = np.multiply(A,x)
    print(C)
    print(np.sum(C))
    