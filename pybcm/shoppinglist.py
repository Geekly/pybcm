# Copyright (c) 2012-2017, Keith Hooks
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Created on Oct 26, 2012

@author: khooks
"""
from legoutils import LegoElement
from solution import *
from vendors import VendorMap


class ShoppingList():
    """Create shopping lists from Solutions

        shoppinglist = [ { itemid, color, vendorid, price, qty }, ...]

        also need to create one by vendor for Bricklink wanted lists
    """
    def __init__(self, solution):
        self.data = list()
        self.soln = solution
        if not isinstance(solution.vendor_map, VendorMap):
            raise Exception("vendor_map does not exist")
        #self.vendor_map = vendor_map

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
        #global vendor_map
        #TODO: access vendor_map
        xml_string = ''
        if self.soln:
            vdict = self.soln.byvendordict()
            #TODO: Finish this routine

            #print(self.vendor_map)
            for vendorid, itemlist in list(vdict.items()):
                vendorname = self.vendormap[vendorid]
                print((vendorid, vendorname))
                xml_string += "\n\n<INVENTORY>\n"

                for element, qty, price in itemlist:
                    elementid, color = LegoElement.splitElement(element)
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
