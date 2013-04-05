'''
Created on Jul 26, 2012

@author: khooks
'''

from wanted import WantedDict
from legoutils import LegoElement
from bricklinkdata import BricklinkData
from legoutils import LegoColor
from blreader import *
import io
#from vendors import Vendors
from bcmdata import BCMData



if __name__ == '__main__':
    
    
    logging.basicConfig(level=logging.DEBUG)
    wantedlistfilename = '../Molding Machine.bsx'
    
    reloadpricesfromweb = False  #set this to true if you want to update prices from the web and rewrite pricefilename
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
    
    #for element in bricklink.keys():
        
    #for key in bricklink.keys():
        #print (key)
        
    data = BCMData(bricklink, wanteddict)
    for key in data.keys():
        print(key)
        
    print("Getting price & qty")
    print(data.getpriceandqty('3460|86', '235082')) 
      
    
    print(data.pricenumpy())
    
    print(data.getelements())
    print(data.getvendors())
    #data.buildfrombricklink(bricklink, wanteddict)
    #data.dataquality()
    #f = open('test.out', 'w')
    #f.write(bricklink.toXML())
    

    #f = open(pricefilename, 'w')
    #f.write( bricklink.toXML()) 
        
    #reporter = BCMData()
    #reporter.buildfrombricklink(bricklink, wanteddict)
    #print reporter.toCSV()
    #out = open("brick.csv", 'w')
    
    
    #reporter.describevendors()
    
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


    


