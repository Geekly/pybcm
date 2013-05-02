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
from bcmdata import BCMData
from pprint import pprint
from orBCM import OROptimizer
from reporter import *


if __name__ == '__main__':
      
    logging.basicConfig(level=logging.DEBUG)
    wantedlistfilename = '../Molding Machine.bsx'
    #wantedlistfilename = '../Inventory for 6964-1.bsx'
    
    
    reloadpricesfromweb = False  #set this to true if you want to update prices from the web and rewrite pricefilename
    #make sure to run this once every time that the wanted list changes
                                     
    pricefilename = '../Molding Machine.xml'

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

   
    bcm = BCMData(bricklink, wanteddict)


    rep = reporter(bcm)
    
    for elementid in bcm.elementlist:
        rep.pricehistogram( elementid )

    #oro = OROptimizer(data)
    #oro.solve()
