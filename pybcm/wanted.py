"""
Created on Oct 23, 2012

@author: khooks
"""
#TODO: replace beautifulsoup with lxml
#Converted the dictionary key from itemid, colorid to elementid, which is of the format 'itemid|colorid'

from UserDict import UserDict
from BeautifulSoup import BeautifulSoup as Soup
from legoutils import LegoElement
#from string import Template
#from xml.etree import ElementTree as ET 

class WantedDict(UserDict):
    """
    classdocs
    """
    def __init__(self, filename=None):
        UserDict.__init__(self)
        if filename is not None:
            self.filename = filename
        self.totalcount = 0
    
    def __str__(self):
        returnstring = "Item, Color, Qty\n"
        for element in self.keys():
            #d = self.data[elementid]
            #print self[element]
            returnstring += str(self[element].itemid + ", " + self[element].colorid + ", " + str(self[element].wantedqty) + "\n")
            
        return returnstring
                          
    def read(self, filename=None):
        assert filename is not None, "Wanted List filename required"
        f = open(filename, 'r')
        soup = Soup( f )
        #wanteddict = dict() #initialize as an empty dictionary
        wantedlist = soup.findAll("item")
    
        for node in wantedlist:
            itemid = node.find('itemid').string
            itemname = node.find('itemname').string
            itemtypeid = node.find('itemtypeid').string
            itemtypename = node.find('itemtypename').string
            colorid = node.find('colorid').string
            colorname = node.find('colorname').string
            wantedqty = int(node.find('qty').string)
            self.totalcount += wantedqty
            
            element = LegoElement( itemid, colorid, itemname, itemtypeid, itemtypename, colorname, wantedqty)
            
            #dictvalue = { 'itemid':itemid, 'itemname':itemname, 'itemtypeid':itemtypeid, 'itemtypename':itemtypename, 'colorid':colorid, 'colorname':colorname, 'qty':qty, 'condition':'N'}
            #self.data[itemid, colorid] = dictvalue #the key is a tuple of the itemid and the color id
            self[element.id] = element
            
    def uniqueitems(self):
        return len(self)        

    def totalitems(self):
        return self.totalcount

    def getwantedqty(self, elementid):
        return self[elementid].wantedqty 
     
        
if __name__ == '__main__':
    wantedlistfilename = '..\Molding Machine.bsx'
    wanteddict = WantedDict()
    wanteddict.read(wantedlistfilename)
    print( wanteddict.data )
    print( wanteddict )
    print( wanteddict.getwantedqty('3009|6') )
