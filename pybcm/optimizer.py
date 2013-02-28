'''
Created on Oct 23, 2012

@author: khooks
'''

from shoppinglist import ShoppingList
from bcmdata import BCMData

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
        
   
