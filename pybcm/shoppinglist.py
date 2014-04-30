"""
Created on Oct 26, 2012

@author: khooks
"""
from pybcm.legoutils import LegoElement
from pybcm.vendors import VendorMap
from pybcm.solution import *


class ShoppingList():
    """Create shopping lists from Solutions

        shoppinglist = [ { itemid, color, vendorid, price, qty }, ...]

        also need to create one by vendor for Bricklink wanted lists
    """
    def __init__(self, solution):
        self.data = list()
        self.soln = solution
        if not isinstance(solution.vendormap, VendorMap):
            raise Exception("vendorMap does not exist")
        #self.vendormap = vendormap

    def additem(self, item):
        if isinstance(item, LegoElement):
            self.data.append(item)

    def toxml(self):
        """Generate the XML for a wanted list."""
        xml_string = ''
        xml_string += "<INVENTORY>"
        for row in self.data:
            xml_string += '<ITEM>\n'
            xml_string += ' <ITEMTYPE>P</ITEMTYPE>'
            xml_string += ' <ITEMID>{}</ITEMID>\n'.format(row[0])
            xml_string += ' <ColorID>{}</ColorID>\n'.format(row[1])
            xml_string += ' <WantedQty>{}</WantedQty>\n'.format(row[2])
            xml_string += ' <VendorID>{}</VendorID>\n'.format(row[3])
            xml_string += ' <VendorName>{}</VendorName>\n'.format(row[4])
            xml_string += ' <VendorQty>{}</VendorQty>\n'.format(row[5])
            xml_string += ' <VendorPrice>{}</VendorPrice>\n'.format(row[6])
            xml_string += ' <Cost>{}</Cost>\n'.format(row[7])
            xml_string += ' <Condition>N</Condition>'
            xml_string += '</Item>\n'
        xml_string += "</Inventory>"
        return xml_string

    def xmlforbricklink(self):
        """Generate the XML for a Bricklink wanted list."""
        #global vendorMap
        #TODO: access vendormap
        xml_string = ''
        if self.soln:
            vdict = self.soln.byvendordict()
            #TODO: Finish this routine

            #print(self.vendormap)
            for vendorid, itemlist in list(vdict.items()):
                vendorname = self.vendormap[vendorid]
                print((vendorid, vendorname))
                xml_string += "\n\n<INVENTORY>\n"

                for element, qty, price in itemlist:
                    elementid, color = LegoElement.splitelement(element)
                    xml_string += '<ITEM>'
                    xml_string += ' <ITEMTYPE>P</ITEMTYPE>'
                    xml_string += ' <ITEMID>%s</ITEMID>' % elementid
                    xml_string += ' <COLOR>%s</COLOR>' % color
                    xml_string += ' <MINQTY>%d</MINQTY>' % qty
                    xml_string += ' <CONDITION>N</CONDITION>'
                    xml_string += '</ITEM>\n'
                xml_string += "</INVENTORY>"
        return xml_string

    def display(self):

        print(self.toxml())

if __name__ == '__main__':

    slist = Solution()
    testlist = ShoppingList(slist)

    element = LegoElement()
    testlist.additem(4323, 88, 167895, "House of Lolgos", 15, 0.15)
    testlist.display()
