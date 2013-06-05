'''
Created on Oct 23, 2012

@author: khooks
'''
from UserDict import UserDict
from blreader import BricklinkWebReader
#from BeautifulSoup import BeautifulSoup
from legoutils import LegoElement
from lxml import etree as ET
import vendors
from vendors import Vendor, vendorMap
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
        global vendorMap
        if not isinstance(vendorMap, vendors.VendorMap): #check for global vendormap
            vendorMap = vendors.VendorMap()
            #raise Exception, "vendorMap not defined"
        
        UserDict.__init__(self)
        self.data = dict()   # self.data[elementid] = list of vendors with prices
        #self.vendormap = VendorMap()
        
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
            logging.info("Loading element " + str(elementid))
            itemID = wanted[elementid].itemid          
            itemtypeID = wanted[elementid].itemtypeid
            itemColorID = wanted[elementid].colorid
            #elementID = lego.joinelement(itemID, itemColorID)
            pricelist = self.webreader.readitemfromurl( itemtypeID, itemID, itemColorID)
            if pricelist: 
                self[elementid] = pricelist   #get the item page, parse it, and get back a list of (itemid<-this is vendorid, vendorqty, vendorprice) tuples
            else:
                logging.error("No Information found for %s" % elementid)
        #self.buildvendormap()
        #self.buildvendordata()
        
        self.bricklink_initialized = True
                      
    def read(self, filename=None):
        global vendorMap
        assert filename != None, "price List filename required"
        logging.info("Building bricklink data from file: " + filename)
        self.data = dict()  #clear any existing data

        tree = ET.parse(filename)
        
        
        wantedlist = tree.findall('Item')
        for item in wantedlist:
            #print(item.text)
            
            itemid = item.find('ItemID').text
            colorid = item.find('ColorID').text
            elementid = LegoElement.joinelement(itemid, colorid)
            self[elementid] = [] #empty list
            logging.info("Loading element " + str(elementid))
            
            vendors = item.findall('Vendor')
            for vendor in vendors:
                
                vendorid = vendor.find('VendorID').text
                vendorqty = vendor.find('VendorQty').text
                vendorprice = vendor.find('VendorPrice').text
                #listitem = [vendorid, vendorqty, vendorprice]              
                self[elementid].append([vendorid, vendorqty, vendorprice])         
                vendorname = vendor.find('VendorName').text
                vendorMap.addvendor( Vendor(vendorid=vendorid, vendorname=vendorname) )
        
    def dataquality(self):
        global vendorMap
        assert self.bricklink_initialized == True, "bricklink not initialized, cannot report dataquality"
        
        print( "Price list includes:")
        print( str( len(self.keys()) ) + " Total Items")
        print( str( len(vendorMap.keys()) ) + " Total Vendors")
    
    def toXML(self):
        global vendorMap
        assert self.bricklink_initialized == True, "bricklink not initialized, cannot convert to XML"
        #[itemID, storeID, quantity, price]
        xml_string = '<xml>\n'
        for elementid in self.keys():
            itemid, color = LegoElement.splitelement(elementid)
            
            xml_string += '<Item>\n'
            xml_string += ' <ItemID>{}</ItemID>\n'.format(itemid)
            xml_string += ' <ColorID>{}</ColorID>\n'.format(color)
            for vendor in self.data[elementid]:
                vendorid = vendor[0]
                vendorname = vendorMap[vendorid]
                xml_string += '  <Vendor>\n'
                xml_string += '   <VendorID>{}</VendorID>\n'.format(vendor[0])
                xml_string += '   <VendorName>{}</VendorName>\n'.format(vendorname)
                xml_string += '   <VendorQty>{}</VendorQty>\n'.format(vendor[1])
                xml_string += '   <VendorPrice>{}</VendorPrice>\n'.format(vendor[2])
                xml_string += '  </Vendor>\n'
                        
            xml_string += '</Item>\n'    
        xml_string += '</xml>'
        return xml_string