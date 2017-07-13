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
    
    
