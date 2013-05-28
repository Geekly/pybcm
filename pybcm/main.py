'''
Created on Jul 26, 2012

@author: khooks
'''


from wanted import WantedDict

from bricklinkdata import BricklinkData

from blreader import *
from optimizer import *

import io
import numpy as np
#from vendors import Vendors
from bcm import *
from pprint import pprint
#from orBCM import OROptimizer

from reporter import *
import cProfile, pstats
from vendors import VendorMap, VendorStats


#vendormap = VendorMap()

def main():
    
    #np.set_printoptions(threshold=np.nan)  
    logging.basicConfig(level=logging.DEBUG)
    #wantedlistfilename = '../Star Destroyer 30056-1.bsx'
    wantedlistfilename = '../Orange.bsx'
    #wantedlistfilename = '../Inventory for 6964-1.bsx'
       
    reloadpricesfromweb = True  #set this to true if you want to update prices from the web and rewrite pricefilename
    #make sure to run this once every time that the wanted list changes
                                     
    #pricefilename = '../Star Destroyer 30056-1.xml'
    pricefilename = '../Orange.xml'
    wanteddict = WantedDict()
    logging.info( "Reading wanted list: " + wantedlistfilename)
    wanteddict.read(wantedlistfilename)
    #print("want this many items: " , wanteddict.totalcount) 
    
    bricklink = BricklinkData()
                     
    if reloadpricesfromweb == True:
        logging.info("Reading prices from web")
        bricklink.readpricesfromweb( wanteddict )
        logging.info("Saving XML file")
        f = open(pricefilename, 'w')
        f.write( bricklink.toXML() ) 
    else: 
        logging.info("Reading prices from file")
        f = open(pricefilename, 'r')
        
        bricklink.read(pricefilename)
        f.close()

    vendormap = bricklink.vendormap
    bcm = BCMEngine(bricklink, wanteddict)

    #bcm.prunevendorsbyavgprice()

    #print( bcm.data.elementlist)
    #print( bcm.data.WANTED)
    #print( bcm.data.avgprices())
    #print( bcm.data.avgprices(stockweighted=True))
    #rep = reporter(bcm)
    #rep.allpartsbarchart()
    ndo = Optimizer(bcm.data)
    ndo.solve()
    
    #print( ndo.solutions.summary() )
    
    #print("The best solution found:\n")
    print( ndo.solutions.best() )
    
    shopping = ShoppingList(ndo.solutions.best(), vendormap )
    print( shopping.XMLforBricklink() )
    
if __name__ == '__main__':
    
    main()
          
    '''
    cp = cProfile.Profile()
       
    cp.run('main()')
    
    ps = pstats.Stats(cp)
    ps.sort_stats('time')
    ps.print_stats(0.2)
    '''
