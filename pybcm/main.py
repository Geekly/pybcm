'''
Created on Jul 26, 2012

@author: khooks
'''

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
    
    
    reloadpricesfromweb = True  #set this to true if you want to update prices from the web and rewrite pricefilename
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
    #print(bricklink.toXML())
   
    
    data = BCMData(bricklink, wanteddict)
    #data.calculateavgprices()
    #print(data.vendormap.toXML())
    #print(data.avgprices())
    #data.cullvendors()
    #print(data.stockarray)
    #print(data.avgprices())
    #print(data.vendormap.toXML())
    
    
    #print( result )
    #pprint(data.maparray2vendorid(result))
    #print( data.wantedarray )
    #a = data.calculateavgprices() 
    #pprint(a)
    
    #w = data.elementweights()
    # pprint ( w )
    #print( data.cullbymetric() )
    # pprint( data.maparray2vendorid( data.pricearray))
    #pprint( data.maparray2vendorid( data.stockarray) )
    #pprint( data.itemspervendor())
    #pprint( data.dropifsingle())
    #vendoridx = data.cheapvendorsbyitem()
    #data.pricearray = data.pricearray[:, vendoridx]
    #data.stockarray = data.stockarray[:, vendoridx]
    #pprint( vendoridx )
    #print( data.describevendors() )
    #print( data.countitemspervendor())
    #pprint(data.vendorlist)
    #shortvlist = [ data.vendorlist[i] for i in vendoridx]
    #si = [ shortvlist.index(i) for i in shortvlist]
    #print (si)
    #opt = Optimizer()
    
    #result = opt.simplesearch(data)
    #ata.describevendors()
    
    #data.cullvendorsbyprice()
    
    
    pprint( data.sortedvendorindices() )
    
    #result = opt.simplesearch(data)
   
    #print( data.shoppinglist(result).display() )
    
    
    
    #data.describevendors()
    #print(result)
    
    #result = opt.simplesearch(data)
    #data.describevendors()
    #print(data.vendorlist)
    #print (shortvlist)
    #v = [ data.pricearray[:,i] for i in vendoridx ]
    #print(vendoridx)
    #print(data.vendorlist)
    #vl = np.array(data.vendorlist)
    #print( vl)
    #pprint(vl[vendoridx])
    #pprint(data.vendorlist[vendoridx])
    #pprint( data.vendorlist[vendoridx,] )
    #data.vendorlist = data.vendorlist[:vendoridx:]
    #pprint(data.vendorlist)
    #pprint( data.pricearray[:,vendoridx] ) #slice the pricearray using the vendor indices
    #print("Average prices")
    #pprint(data.calculateavgprices())
    #print("Vendor price metrics")
    #pprint(data.vendorcostmetric())
    #print("Items Per Vendor")
    #pprint(data.countitemspervendor())
    
    #pprint(data.wantedarray)
    #print("Result matrix")
    #pprint(data.result)
    #np.savetxt("../result.csv", data.result, delimiter=",")
    #np.savetxt("../vendorprices.csv", data.pricearray, delimiter=",")
    #np.savetxt("../avgprices.csv", data.calculateavgprices, delimiter=",")
    #np.savetxt("../costmetric.csv", data.vendorcostmetric, delimiter=",")
    #print(data.elementweights())
    
    #print( data.maparray2vendor(data.stockarray) )
    #print( data.maparray2vendor(data.pricearray ))
    #for tuple in data.data.keys():
    #    print( tuple, data.data[tuple] )
    #result = opt.simplesearch(data)
    #shoppinglist = data.shoppinglist()
    #print(shoppinglist.XMLforBricklink())
    #print(shoppinglist)
    #print(data.vendors)   
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





