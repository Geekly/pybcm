"""
Created on Oct 23, 2012

@author: khooks
"""
#TODO: replace beautifulsoup with lxml
#Converted the dictionary key from itemid, colorid to elementid, which is of the format 'itemid|colorid'

from collections import UserDict
from lxml import etree
from bs4 import BeautifulSoup as Soup
from legoutils import LegoElement


# from .legoutils import LegoElement

#from string import Template
#from xml.etree import ElementTree as ET 


class WantedDict(UserDict):
    """
    Dict[elementid] = LegoElement
    """

    def __init__(self, filename=None):
        UserDict.__init__(self)
        if filename is not None:
            self.filename = filename
        self._totalcount = 0

    def __str__(self):
        returnstring = "Item, Color, Qty\n"
        for tElement in list(self.keys()):
            # d = self.data[elementid]
            # print self[element]
            returnstring += str(
                self[tElement].elementId + ", " + str(self[tElement].wantedqty) + "\n")

        return returnstring

    def read(self, filename=None):
        try:
            f = open(filename, 'r')
            soup = Soup(f, "lxml")
            # wanteddict = dict() #initialize as an empty dictionary
            wantedlist = soup.findAll("item")

            for itemNode in wantedlist:
                itemid = itemNode.find('itemid').string
                itemname = itemNode.find('itemname').string
                itemtypeid = itemNode.find('itemtypeid').string
                itemtypename = itemNode.find('itemtypename').string
                colorid = itemNode.find('colorid').string
                colorname = itemNode.find('colorname').string
                wantedqty = int(itemNode.find('qty').string)
                self._totalcount += wantedqty

                newElement = LegoElement(itemid, colorid, wantedqty=wantedqty, itemname=itemname, itemtypeid=itemtypeid,
                                         itemtypename=itemtypename, colorname=colorname)

                self[newElement.elementId] = newElement
        except IOError as e:
            print(e)

    # TODO:Convert unique_items to read-only property
    @property
    def unique_items(self):
        """Return the total number of unique items in the Wanted List"""
        return len(self)

    # TODO:Convert total_items to read-only property
    @property
    def total_items(self):
        """Return the total number of parts in the Wanted List"""
        return self._totalcount

    def get_wanted_qty(self, elementid):
        """Return the quantity wanted for the passed elementid"""
        if elementid in self.data:
            return self[elementid].wantedqty
        else:
            return 0

if __name__ == '__main__':
    wantedlistfilename = "../Sampledata/Remaining Falcon.bsx"
    wanteddict = WantedDict()
    wanteddict.read(wantedlistfilename)
    print(wanteddict.data)
    print(wanteddict)
    # print(wanteddict.get_wanted_qty('3009|6'))
