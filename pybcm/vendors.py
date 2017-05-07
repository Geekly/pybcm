"""
Created on Oct 23, 2012

@author: khooks
"""

#  import numpy as np
from collections import UserDict


class Vendor(object):
    """Vendor represented by id and name and can be output to XML.
        Args:
            vendorid (str):  Bricklink id of the vendor
            vendorname (str):  Name of the vendor store
        Attributes:
            vendorid (str):  Bricklink id of the vendor
            vendorname (str):  Name of the vendor store
    """
    
    def __init__(self, vendorid='', vendorname=''):
        self._id = str(vendorid)
        self._name = str(vendorname)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = str(value)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = str(value)

    @property
    def xml(self):
        """Return an XML string of the Vendor."""

        xmlstring = ''
        xmlstring += "<Vendor>\n"
        xmlstring += "<VendorID>" + str(self._id) + "</VendorID>\n"
        xmlstring += "<VendorName>" + str(self._name) + "</VendorName>\n"
        xmlstring += "</Vendor>\n"
        return xmlstring

    def __str__(self):
        return self.xml



# TODO: Make this work
#not sure this works                           
    #def read(self, filename=None):
    #     assert filename is not None, "price List filename required"
    #     print( "Building vendor map from file: " + filename)
    #     self.data = dict()  #clear any existing data
    #
    #     soup = stockarrayoup( open(filename).read(), "lxml")
    #     vendorlist = soup.findAll("vendor")
    #
    #         # for each item node, recurse over each vendor node
    #
    #     for vendor in vendorlist:
    #         vendorid = vendor.find('vendorid').string
    #         vendorname = vendor.find('vendorname').string
    #
    #         self[vendorid] = vendorname
    #
    #     # for now, just save and process the prices structure.  They contain the same data.
    #    pass

#not sure this works


class VendorMap(UserDict):
    """ Map of Bricklink vendor id to Vendor object as extracted from the Bricklink item page
        Because the VendorMap is intimately link to Vendor, it's bundled together

        Attributes:
            data(dict): dict[vendor.id] = Vendor
    """

    def __init__(self):
        UserDict.__init__(self)
        self.data = dict()

    def __str__(self):
        """ Return an XML formatted vendor map. """
        return self.xml()

    def addVendor(self, vendor):
        """Add a vendor to the vendor map.
            If the vendor id is not present yet, add it.

            Args:
                vendor (Vendor): the Vendor object to be added
            Returns:
                false if the vendor id is already present, true otherwise
        """
        if vendor.id in self.data:
            return False
        else:
            # logging.debug("Adding vendor: " + vendor.name)
            self[vendor.id] = vendor  # assign the whole vendor object in case we add to it later
            return True

    def getNumVendors(self):
        """Get the length of the vendor map."""
        return len(self)

    def getVendorName(self, vendorid):
        """Get the name of the vendor for a given id."""
        if vendorid in list(self.keys()):
            return self[vendorid].name
        else:
            return ''

    @property
    def xml(self):
        """Return an XML string of the VendorMap."""

        vendorkeys = list(self.keys())
        xml_string = '<VendorMap>'
        for vendorid in vendorkeys:
            vendor = self[vendorid]
            xml_string += vendor.xml
        xml_string += '</VendorMap>'
        return xml_string

    def __str__(self):
        return self.xml

#test code goes here
if __name__ == '__main__':
    vendormap_ = VendorMap()
    pass
    
    