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

import logging
from collections import UserDict

from bs4 import BeautifulSoup as Soup

import log
from legoutils import WantedElement

logger = logging.getLogger(__name__)


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
                self[tElement].elementid + ", " + str(self[tElement].wantedqty) + "\n")

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
                wantedqty = int(itemNode.find('qty').string)
                self._totalcount += wantedqty

                newElement = WantedElement(itemid, colorid, wantedqty=wantedqty, itemname=itemname,
                                           itemtypeid=itemtypeid,
                                           itemtypename=itemtypename)
                self[newElement.elementid] = newElement

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

    @property
    def element_list(self):
        return list(set([e for e in self]))

    @property
    def simple_dict(self):
        return { e.elementid:e.wantedqty for e in self.values() }


if __name__ == '__main__':
    log.setup_custom_logger(__name__)
    wantedlistfilename = "../Sampledata/Remaining Falcon.bsx"
    wanteddict = WantedDict()
    wanteddict.read(wantedlistfilename)
    print(wanteddict.data)
    print(wanteddict)
    # print(wanteddict.get_wanted_qty('3009|6'))
    print(wanteddict.element_set)
    print(wanteddict.simple_dict)