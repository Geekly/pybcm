'''
Created on Oct 23, 2012

@author: khooks
'''
from collections import UserDict
from blreader import BricklinkWebReader
from legoutils import LegoElement
from vendors import *
import logging

#from wanted import Wanted

class BricklinkData(UserDict):
    '''
    data is a dictionary of the format:
    [storeID, quantity, price]
    data[elementid] = { [vendor1id, vendor1qty, vendor1price],
                            [vendor2id, vendor2qty, vendor2price],
                            ... }
    where elementid is itemid|colorid
    
    this class also works on the vendormap, which maps vendor ID to vendor name
    
    '''
    def __init__(self):
        
        UserDict.__init__(self)
        self.data = dict()   # self.data[elementid] = list of vendors with prices
        self.vendormap = VendorMap()
        
        self.bricklink_initialized = False
        self.vendor_initialized = False
        self.averageprices = dict()
        self.webreader = None
        
    def __str__(self):
        assert self.bricklink_initialized == True, "bricklink not initialized, cannot convert to string"
        return self.toXML()    
    
    def readpricesfromweb(self, wanted):
    #    Build a dictionary of price info
        self.webreader = BricklinkWebReader("Geekly", "codybricks")
        numitems = len(wanted)
        logging.info("Loading " + str(numitems) + " items from the web")
        #self.data = dict() # a dictionary with keys itemid, and color.  each entry contains a list of lists
        for elementid in wanted.keys():
            #grab the needed variables for constructing the URL
            itemID = wanted[elementid].itemid          
            itemtypeID = wanted[elementid].itemtypeid
            itemColorID = wanted[elementid].colorid
            #elementID = lego.joinelement(itemID, itemColorID)
            pricelist = self.webreader.readitemfromurl( itemtypeID, itemID, itemColorID, self.vendormap)
            self[elementid] = pricelist   #get the item page, parse it, and get back a list of (itemid<-this is vendorid, vendorqty, vendorprice) tuples
            
        #self.buildvendormap()
        #self.buildvendordata()
        
        self.bricklink_initialized = True
               
           
    def read(self, filename=None):
        assert filename != None, "price List filename required"
        logging.info("Building bricklink data from file: " + filename)
        self.data = dict()  #clear any existing data
        
        self.soup = Soup(open(filename).read(), "lxml")
        wantedlist = self.soup.findAll("item")
        
            # for each item node, recurse over each vendor node      
            
        for item in wantedlist:
            itemid = item.find('itemid').string
            colorid = item.find('colorid').string
            elementid = LegoElement.joinelement(itemid, colorid)
            self[elementid] = [] #empty list
            
            vendors = item.findAll('vendor')
            for vendor in vendors:
                
                vendorid = vendor.find('vendorid').string

                vendorqty = vendor.find('vendorqty').string
                vendorprice = vendor.find('vendorprice').string

                listitem = [vendorid, vendorqty, vendorprice]              
                self[elementid].append(listitem) 
        
                vendorname = vendor.find('vendorname').string
                self.vendormap.addvendor( Vendor(vendorid=vendorid, vendorname=vendorname) )
                
        
        self.bricklink_initialized = True
        

    def dataquality(self):
        assert self.bricklink_initialized == True, "bricklink not initialized, cannot report dataquality"
        
        print( "Price list includes:")
        print( str( len(self.keys()) ) + " Total Items")
        print( str( len(self.vendormap.keys()) ) + " Total Vendors")
    
    '''def getpriceandqty(self, elementid, vendorid):  #delete this   
        
        if elementid in self:
            element = self[elementid]
            #search for the vendor being asked for
            for vendor in element:
                vendorid = vendor[1]
                if True:#id == vendorid:
                    qty = vendor[2]
                    price = vendor[3]
                    #logging.DEBUG("vendorid: " + id)
                    return [qty, price]
                
        pass
    '''
    
    def createshoppinglists(self, bcmdata):
        #the shopping list will be parsed and used to place orders.  Non-zero quantities are eliminated
        #remove columns with zero values from optimizedresult
        pass
          
    def toXML(self):
        
        assert self.bricklink_initialized == True, "bricklink not initialized, cannot convert to XML"
        #[itemID, storeID, quantity, price]
        xml_string = ''
        for elementid in self.keys():
            itemid, color = LegoElement.splitelement(elementid)
            xml_string += '<Item>\n'
            xml_string += ' <Itemid>{}</ItemID>\n'.format(itemid)
            xml_string += ' <ColorID>{}</ColorID>\n'.format(color)
            for vendor in self.data[elementid]:
                vendorid = vendor[0]
                vendorname = self.vendormap[vendorid]
                xml_string += '  <Vendor>\n'
                xml_string += '   <VendorID>{}</VendorID>\n'.format(vendor[0])
                xml_string += '   <VendorName>{}</VendorName>\n'.format(vendorname)
                xml_string += '   <VendorQty>{}</VendorQty>\n'.format(vendor[1])
                xml_string += '   <VendorPrice>{}</VendorPrice>\n'.format(vendor[2])
                xml_string += '  </Vendor>\n'
                        
            xml_string += '</Item>\n'    
        
        return xml_string