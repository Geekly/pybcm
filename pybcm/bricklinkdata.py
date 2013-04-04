'''
Created on Oct 23, 2012

@author: khooks
'''
from collections import UserDict
from blreader import BricklinkWebReader
from bs4 import BeautifulSoup as Soup
from vendors import VendorMap
from legoutils import Element

#from wanted import Wanted

class BricklinkData(UserDict):
    '''
    data is a dictionary of the format:
    [itemID, storeID, quantity, price]
    data[elementid] = { [vendor1id, vendor1qty, vendor1price],
                            [vendor2id, vendor2qty, vendor2price],
                            ... }
    where elementid is itemid|colorid
    
    this class also works on the vendormap, which maps vendor ID to vendor name
    
    '''
    def __init__(self):
        
        UserDict.__init__(self)
        self.data = dict()   # self.data[elementid] = list of vendors with prices
        self.vendordata = dict()
        self.vendormap = VendorMap()
        
        self.bricklink_initialized = False
        self.vendor_initialized = False
        
        self.webreader = BricklinkWebReader("Geekly", "codybricks")
        
    def __str__(self):
        assert self.bricklink_initialized == True, "bricklink not initialized, cannot convert to string"
        return self.toXML()    
   
   
    def buildvendormap(self):
        print( "Building Vendor Map")
        for elementid in self.keys():
            for vendor in self[elementid]:
                self.vendormap.addvendor(vendor[0], vendor[1])
        

    def buildvendordata(self):
    #try to make this function go away
        self.vendordata = dict()
        
        for elementid in self.data:
            tempitem = self[elementid]   #this is a list within a dictionary
            for i in tempitem:
                vendorid = i[0]
                self.vendormap.addvendor(vendorid, i[1])
                vendorqty = i[2]
                vendorcost = i[3]
                
                try:
                    if ( vendorid in self.vendordata ):
                        self.vendordata[vendorid].append( [elementid, vendorqty, vendorcost] )              
                    else:
                        self.vendordata[vendorid] = list()
                        self.vendordata[vendorid].append( [elementid, vendorqty, vendorcost] )
                except KeyError as e:
                    print( e)
        self.vendor_initialized = True
 
                
    def dataquality(self):
        assert self.bricklink_initialized == True, "bricklink not initialized, cannot report dataquality"
        
        print( "Price list includes:")
        print( str( len(self.keys()) ) + " Total Items")
        print( str( len(self.vendormap.keys()) ) + " Total Vendors")
       
    def readpricesfromweb(self, wanted):
    #    Build a dictionary of price info
        
        #self.data = dict() # a dictionary with keys itemid, and color.  each entry contains a list of lists
        for elementid in wanted.keys():
            #grab the needed variables for constructing the URL
            itemID = wanted[elementid].itemid          
            itemtypeID = wanted[elementid].itemtypeid
            itemColorID = wanted[elementid].colorid
            #elementID = lego.joinelement(itemID, itemColorID)
            
            self[elementid] = self.webreader.readitemfromurl( itemtypeID, itemID, itemColorID)  #get the item page, parse it, and get back a list of (vendorid, vendorname, vendorqty, vendorprice) tuples
        
        self.buildvendormap()
        #self.buildvendordata()
        
        self.bricklink_initialized = True
   
    def read(self, filename=None):
        assert filename != None, "price List filename required"
        print ("Building bricklink data from file: " + filename)
        self.data = dict()  #clear any existing data
        
        self.soup = Soup(open(filename).read(), "lxml")
        wantedlist = self.soup.findAll("item")
        
            # for each item node, recurse over each vendor node      
            
        for item in wantedlist:
            itemid = item.find('itemid').string
            colorid = item.find('colorid').string
            elementid = Element.joinelement(itemid, colorid)
            self[elementid] = [] #empty list
            
            vendors = item.findAll('vendor')
            for vendor in vendors:
                
                vendorid = vendor.find('vendorid').string
                vendorname = vendor.find('vendorname').string
                vendorqty = vendor.find('vendorqty').string
                vendorprice = vendor.find('vendorprice').string

                listitem = [vendorid, vendorname, vendorqty, vendorprice]
                self[elementid].append(listitem) 
        
        self.buildvendormap()
        #self.buildvendordata()
        
        self.bricklink_initialized = True
    
    def toXML(self):
        
        assert self.bricklink_initialized == True, "bricklink not initialized, cannot convert to XML"
        
        xml_string = ''
        for elementid in self.keys():
            itemid, color = Element.splitelement(elementid)
            xml_string += '<Item>\n'
            xml_string += ' <Itemid>{}</ItemID>\n'.format(itemid)
            xml_string += ' <ColorID>{}</ColorID>\n'.format(color)
            for vendor in self.data[elementid]:
                xml_string += '  <Vendor>\n'
                xml_string += '   <VendorID>{}</VendorID>\n'.format(vendor[0])
                xml_string += '   <VendorName>{}</VendorName>\n'.format(vendor[1])
                xml_string += '   <VendorQty>{}</VendorQty>\n'.format(vendor[2])
                xml_string += '   <VendorPrice>{}</VendorPrice>\n'.format(vendor[3])
                xml_string += '  </Vendor>\n'
            
            
            xml_string += '</Item>\n'    
        
        return xml_string