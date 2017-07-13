"""
Created on Oct 23, 2012

@author: khooks
"""

#  import numpy as np
import json


class VendorMap(dict):
    """ Map of Bricklink vendor id to Vendor object as extracted from the Bricklink item page
        Because the VendorMap is intimately link to Vendor, it's bundled together

        Attributes:
            data(dict): dict[vendor.id] = Vendor
    """

    def __setitem__(self, key, value):
        key = str(key)
        dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        key = str(key)
        val = dict.__getitem__(self, key)
        return val

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
    vendormap_['123456'] = "Stew's brick town"
    vendormap_[111] = "111 Bricks on the Wall"
    vendormap_['334567'] = "Bricks be bricks"
    vendormap_['367777'] = "Damn bricks!"
    print(vendormap_[123456])
    print(vendormap_[111])
    print(vendormap_['111'])
    print(vendormap_.json)
    print(vendormap_)
    pass
    
    