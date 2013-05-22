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
from vendors import VendorStats




def main():
    
    #np.set_printoptions(threshold=np.nan)  
    logging.basicConfig(level=logging.DEBUG)
    wantedlistfilename = '../Star Destroyer 30056-1.bsx'
    #wantedlistfilename = '../Inventory for 6964-1.bsx'
       
    reloadpricesfromweb = False  #set this to true if you want to update prices from the web and rewrite pricefilename
    #make sure to run this once every time that the wanted list changes
                                     
    pricefilename = '../Star Destroyer 30056-1.xml'

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

    
    bcm = BCMEngine(bricklink, wanteddict)

    bcm.prunevendorsbyavgprice()

    
    ndo = Optimizer(bcm.data)
    print( ndo.solve() )
    
    print( ndo.solutions.summary() )
    
if __name__ == '__main__':
    
    main()
          
    '''
    cp = cProfile.Profile()
       
    cp.run('main()')
    
    ps = pstats.Stats(cp)
    ps.sort_stats('time')
    ps.print_stats(0.2)
    '''
