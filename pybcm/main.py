'''
Created on Jul 26, 2012

@author: khooks
'''

from UserDict import UserDict
from wanted import WantedDict
from legoutils import LegoElement
from bricklinkdata import BricklinkData
from legoutils import LegoColor
from blreader import *
from optimizer import *
import io
import numpy as np
#from vendors import Vendors
from bcm import *
from pprint import pprint
from orBCM import OROptimizer
from reporter import *



if __name__ == '__main__':
      
    logging.basicConfig(level=logging.DEBUG)
    wantedlistfilename = '../Star Destroyer 30056-1.bsx'
    #wantedlistfilename = '../Inventory for 6964-1.bsx'
    
    
    reloadpricesfromweb = False  #set this to true if you want to update prices from the web and rewrite pricefilename
    #make sure to run this once every time that the wanted list changes
                                     
    pricefilename = '../Star Destroyer 30056-1.xml'

    wanteddict = WantedDict()
    bricklink = BricklinkData()
    
    logging.info( "Reading wanted list: " + wantedlistfilename)
    
    wanteddict.read(wantedlistfilename)
                      
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
    
    
    
    
    #print( bcm.ELEMDICT )
    #print( 'wut')
    #bcm.presolve()
    #print( bcm.cheapvendorsbyitem(5) )
    #bcm.cullvendorsbyprice()
    #rep = reporter(bcm)
    #rep.vendorstats()
    
    #w = bcm.elementweights()
    #print( bcm.data.elementsort(w) )
    

    opt = Optimizer(bcm.data)
    result = opt.bucketsearch(bcm.data)
    print( result )
    #print( result.cost() )
    
    #result = opt.allfeasible(bcm.data) 
    #pprint( result )
    #svl = bcm.sortedvendorlists()
    #print svl
    #for element in svl: 
        #print element 
    #    for vid in svl[element]:
            #print vid
    #        print bcm.bcmdict[element, vid]
    #opt = BCMopt(bcm)
    #print( opt.solve() )
