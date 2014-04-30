"""
Created on Oct 23, 2012

@author: khooks
"""
from collections import UserDict
from lxml import etree as ET
import logging
from .blreader import BricklinkWebReader
from .legoutils import LegoElement
from .vendors import Vendor, VendorMap


class BricklinkData(UserDict):
    """Stores bricklink wanted and price information.
        data is a dictionary of the format:
        [storeID, quantity, price]
        data[elementid] = { [vendor1id, vendor1qty, vendor1price],
                                [vendor2id, vendor2qty, vendor2price],
                                ... }
        where elementid is itemid|colorid

        this class also works on the vendormap, which maps vendor ID to vendor name

    """
    def __init__(self):

        UserDict.__init__(self)
        self.data = dict()   # self.data[elementid] = list of vendors with prices
        self._vendormap = VendorMap()
        self.bricklink_initialized = False
        self.vendor_initialized = False
        self.averageprices = dict()
        self.webreader = None

    @property
    def vendormap(self):
        return self._vendormap

    def __str__(self):
        assert self.bricklink_initialized, "bricklink not initialized, cannot convert to string"
        return self.xmlvendordata()
    
    def readpricesfromweb(self, username, password, wanted):
        """Build a dictionary of price info from the Bricklink website
            Attributes:
                wanted(WantedDict): wanted[elementid] = LegoElement
        """
        self.webreader = BricklinkWebReader(self._vendormap, username, password)
        numitems = len(wanted)
        logging.info("Loading " + str(numitems) + " items from the web")
        #self.data = dict() # a dictionary with keys itemid, and color.  each entry contains a list of lists
        for elementid in list(wanted.keys()):  # TODO: elementid is not the correct key
            #grab the needed variables for constructing the URL
            logging.info("Loading element " + str(elementid))
            itemID = wanted[elementid].itemid          
            itemtypeID = wanted[elementid].itemtypeid
            itemColorID = wanted[elementid].colorid
            pricelist = self.webreader.readitemfromurl(itemtypeID, itemID, itemColorID)
            if pricelist: 
                self[elementid] = pricelist   #get the item page, parse it, and get back a list of (itemid<-this is vendorid, vendorqty, vendorprice) tuples
            else:
                logging.error("No Price Information found for %s" % elementid)

        
        self.bricklink_initialized = True
                      
    def read(self, filename=None):
        """Read vendor price information from a file."""

        assert filename is not None, "price List filename required"
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
                assert isinstance(elementid, object)
                self[elementid].append([vendorid, vendorqty, vendorprice])
                vendorname = vendor.find('VendorName').text
                self.vendormap.addvendor(Vendor(vendorid=vendorid, vendorname=vendorname))
        
    def summarize(self):
        """Return a summary string of the bricklink data."""
        assert self.bricklink_initialized == True, "bricklink not initialized, cannot report dataquality"
        
        print("Price list includes:")
        print(str(len(list(self.keys()))) + " Total Items")
        print(str(len(list(self.vendormap.keys()))) + " Total Vendors")
    
    def xmlvendordata(self):
        """Return an XML string of the bricklink vendor price & qty data."""
        assert self.bricklink_initialized == True, "bricklink not initialized, cannot convert to XML"
        #[itemID, storeID, quantity, price]
        xml_string = '<xml>\n'
        for elementid in list(self.keys()):
            itemid, color = LegoElement.splitelement(elementid)
            
            xml_string += '<Item>\n'
            xml_string += ' <ItemID>{}</ItemID>\n'.format(itemid)
            xml_string += ' <ColorID>{}</ColorID>\n'.format(color)
            for stockentry in self.data[elementid]:
                vendorid = stockentry[0]
                vendor = self.vendormap[vendorid]
                xml_string += '  <Vendor>\n'
                xml_string += '   <VendorID>{}</VendorID>\n'.format(stockentry[0])
                xml_string += '   <VendorName>{}</VendorName>\n'.format(vendor.name)
                xml_string += '   <VendorQty>{}</VendorQty>\n'.format(stockentry[1])
                xml_string += '   <VendorPrice>{}</VendorPrice>\n'.format(stockentry[2])
                xml_string += '  </Vendor>\n'
                        
            xml_string += '</Item>\n'    
        xml_string += '</xml>'
        return xml_string
