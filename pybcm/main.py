'''
Created on Jul 26, 2012

@author: khooks
'''

from wanted import WantedDict
from legoutils import Element
from bricklinkdata import BricklinkData
from legoutils import LegoColor
from blreader import *
#from vendors import Vendors
from bcmdata import BCMData



if __name__ == '__main__':
    
    
    logging.basicConfig(level=logging.DEBUG)
    wantedlistfilename = '../Molding Machine.bsx'
    
    reloadpricesfromweb = True  #set this to true if you want to update prices from the web and rewrite pricefilename
    #make sure to run this once every time that the wanted list changes
                                   
    
    pricefilename = '../bricklink.xml'
    vendorpricelist = '../vendorprices.xml'
    outfilename = 'PriceGuidePy.mat'
    USOnly=1
    anycolorID = LegoColor.anycolorID
    makeplots = 0;
  

    wanteddict = WantedDict()
    bricklink = BricklinkData()
    
 
    print( "Reading wanted list", wantedlistfilename)
    
    wanteddict.read(wantedlistfilename)
                   
    print( "Loading Prices")
    if reloadpricesfromweb == True:
        bricklink.readpricesfromweb( wanteddict.data )
        f = open(pricefilename, 'w')
        f.write( bricklink.toXML() ) 
    else: 
        f = open(pricefilename, 'r')
        bricklink.read(pricefilename)
        f.close()

    bricklink.dataquality()
    

    #f = open(pricefilename, 'w')
    #f.write( bricklink.toXML()) 
        
    reporter = BCMData()
    reporter.buildfrombricklink(bricklink, wanteddict)
    #print reporter.toCSV()
    out = open("brick.csv", 'w')
    
    
    reporter.describevendors()
    
    #reporter.cullvendors()
    #out.write(reporter.toCSV())
    #reporter.describevendors()
    #reporter.calculateavgprices()
    #print reporter.toCSV()
    #print reporter    
    #reporter.display()
    #print "Building Vendor Map"
    #bricklink.buildvendormap()
    
    #print( reporter.toCSV())
    #vendordict = Vendors(bricklink)
    
    #print vendordict.toXML()
    #optimize = Optimizer()
    #shoppinglist = optimize.findcheapestparts(wanteddict, bricklink)
    #shoppinglist.display()  


    


