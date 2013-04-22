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



if __name__ == '__main__':
    
    
    logging.basicConfig(level=logging.DEBUG)
    wantedlistfilename = '../Molding Machine.bsx'
    #wantedlistfilename = '../Inventory for 6964-1.bsx'
    
    
    reloadpricesfromweb = False  #set this to true if you want to update prices from the web and rewrite pricefilename
    #make sure to run this once every time that the wanted list changes
                                   
    
    pricefilename = '../Molding Machine.xml'
    #vendorpricelist = '../vendorprices.xml'
    #outfilename = 'PriceGuidePy.mat'
    #USOnly=1
    #anycolorID = LegoColor.anycolorID
    #makeplots = 0;
  

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

    bricklink.dataquality()    

    
    data = BCMData(bricklink, wanteddict)

    opt = Optimizer()
    
    (elementorder, vsorted) = data.cheapvendorsbyitem()
    #print(elementorder)

    result = opt.orderedsearch( elementorder, vsorted, data )
 
    #print( opt.numvendors(result, data.pricearray) )
    product = result * data.pricearray
    #print( product[np.all(product <= 0, axis=1)] )
    #mask = ~np.all(result<=0.0, axis=0)
    #print(result[mask])
    data.pprices.to_csv('../prices.csv', sep=',')#, na_rep, float_format, cols, header, index, index_label, mode, nanRep, encoding, quoting, line_terminator)
