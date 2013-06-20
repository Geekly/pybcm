"""
Created on Jul 26, 2012

@author: khooks
"""


from wanted import WantedDict

from bricklinkdata import BricklinkData
from bcmconfig import *
from blreader import *
from optimizer import *

import numpy as np
#from vendors import Vendors
from bcm import *
from pprint import pprint
#from orBCM import OROptimizer

from reporter import *
import cProfile, pstats
import vendors
from vendors import vendorMap, VendorStats


#vendormap = VendorMap()

def main():
    
    #np.set_printoptions(threshold=np.nan)  
    logging.basicConfig(level=logging.DEBUG)    

    
    wantedlistfilename = BCMConfig.wantedfilename
    pricefilename = BCMConfig.pricefilename
    logging.info( "Reading wanted list: %s" % wantedlistfilename )
    wanteddict = WantedDict()
    wanteddict.read(wantedlistfilename)
    
    bricklink = BricklinkData()
                     
    if BCMConfig.reloadpricesfromweb:
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

    #vendormap = bricklink.vendormap
    bcm = BCMEngine(bricklink, wanteddict)

    #print (bcm.data.vendorlist)
    #print bcm.data.partcount()
    bcm.prunevendorsbyavgprice()
    #print bcm.data.partcount()
    #print (bcm.data.vendorlist)

    #print( bcm.data.elementlist)
    #print( bcm.data.WANTED)
    #print( bcm.data.avgprices())
    #print( bcm.data.avgprices(stockweighted=True))

    #ndo = Optimizer(bcm.data, search=SearchTypes.Swap)
    #ndo.solve()
    #print( ndo.solutions.summary() )
    
    #print( ndo.solutions.best() )
    
    #rep = reporter(bcm)
    #rep.allpartsbarchart()
    #shopping = ShoppingList(ndo.solutions.best())
    #print( shopping.XMLforBricklink() )
    
    vs = VendorStats(bcm.data)
    #print(vs.stockbywanted().sum(0) )
    print(vs.vendorpriceweights())
    #print bcm.data.count()
    
if __name__ == '__main__':
    
    main()
          
    
    '''cp = cProfile.Profile()
       
    cp.run('main()')
    
    ps = pstats.Stats(cp)
    ps.sort_stats('cumulative')
    ps.print_stats(0.1)
    '''
