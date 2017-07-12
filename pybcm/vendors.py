"""
Created on Oct 23, 2012

@author: khooks
"""

#  import numpy as np
import json
import logging

from collections import namedtuple

VendorBase = namedtuple('VendorBase', 'vendor_id vendor_name')


class Vendor(VendorBase):
    """Vendor represented by id and name and can be output to XML.
        Args:
            vendorid (str):  Bricklink id of the vendor
            vendorname (str):  Name of the vendor store
        Attributes:
            vendorid (str):  Bricklink id of the vendor
            vendorname (str):  Name of the vendor store
    """

    def __new__(cls, vendor_id, vendor_name):
        self = super(Vendor, cls).__new__(cls, vendor_id, vendor_name)
        self._hash = hash(self.vendor_id) + hash(self.vendor_name)
        self._log = logging.getLogger("Vendor.py")
        return self

    def __hash__(self):
        return self._hash

    def __repr__(self):
        return self.json

    @property
    def xml(self):
        """Return an XML string of the Vendor."""

        xmlstring = ''
        xmlstring += "<Vendor>\n"
        xmlstring += "<VendorID>" + str(self.vendor_id) + "</VendorID>\n"
        xmlstring += "<VendorName>" + str(self.vendor_name) + "</VendorName>\n"
        xmlstring += "</Vendor>\n"
        return xmlstring

    @property
    def json(self):
        return '{{ "{0}": "{1}" }}'.format(self.vendor_id, self.vendor_name)

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
# not sure this works


class VendorMap(dict):
    """ Map of Bricklink vendor id to Vendor object as extracted from the Bricklink item page
        Because the VendorMap is intimately link to Vendor, it's bundled together

        Attributes:
            data(dict): dict[vendor.id] = Vendor
    """

    # def __init__(self, *args, **kwargs):
    #     self._log = logging.getLogger("Vendor.py")
    #     self.update(*args, **kwargs)
    #
    # def __getitem__(self, key):
    #     val = dict.__getitem__(self, key)
    #     # self._log.debug("GET %s" % key)
    #     return val
    #
    # def __setitem__(self, key, val):
    #     # duplicate keys can't be added, so don't
    #     if key in self:
    #         self._log.debug(ValueError("Vendor %s already exists" % key))
    #     else:
    #         self._log.debug("Adding %s:%s" % (key, val))
    #         dict.__setitem__(self, key, val)
    #
    # def __repr__(self):
    #     dictrepr = dict.__repr__(self)
    #     return '%s(%s)' % (type(self).__name__, dictrepr)
    #
    # def __str__(self):
    #     """ Return an XML formatted vendor map. """
    #     return self.xml
    #
    # def __missing__(self, key):
    #     self._log.debug("missing %s" % key)
    #     raise ValueError("Vendor does not exist")
    #
    # def update(self, *args, **kwargs):
    #     self._log.debug("update %s %s" % (args, kwargs))
    #     for k, v in dict(*args, **kwargs).items():
    #         self[k] = v
    #
    # def addVendor(self, vendor):
    #     #     """Add a vendor to the vendor map.
    #     #         If the vendor id is not present yet, add it.
    #     #
    #     #         Args:
    #     #             vendor (Vendor): the Vendor object to be added
    #     #         Returns:
    #     #             false if the vendor id is already present, true otherwise
    #     #     """
    #     if vendor in self.keys():
    #         return False
    #     else:
    #         # self._log.debug("Adding vendor: %r" % vendor)
    #         self[vendor.vendor_id] = vendor.vendor_name  # assign the whole vendor object in case we add to it later
    #         return True

    @property
    def xml(self):
        """Return an XML string of the VendorMap."""

        vendorkeys = list(self.keys())
        xml_string = '<VendorMap>'
        for vendorid in vendorkeys:
            vendor = Vendor(vendorid, self[vendorid])
            xml_string += vendor.xml
        xml_string += '</VendorMap>'
        return xml_string

    @property
    def json(self):
        return json.dumps(self, sort_keys=True, indent=4)

#test code goes here
if __name__ == '__main__':
    vendormap_ = VendorMap()
    pass
    
    