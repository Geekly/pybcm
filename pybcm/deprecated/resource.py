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

'''Object representations of the BrickLink result data types'''

import logging
from collections import UserDict
from pprint import pprint

from rest import RestClient

logger = logging.getLogger('pybcm.resource')

class ItemResult(UserDict):
    pass


class SuperSetResult(UserDict):
    pass


class SubSet(UserDict):
    pass



class PriceGuide(UserDict):

    def __init__(self, no=None, itemtype=None, color=None, **kwargs):
        super().__init__(self, **kwargs)
        self.data['item'] = {
            'no': no,
            'type': itemtype
        }
        self.data['color'] = color


    def load(self, itemid, itemtypeid, colorid):
        rc = RestClient()
        color, pg = rc.get_part_price(itemid, itemtypeid, colorid)
        self.data = dict(pg)
        return color, pg


pg = PriceGuide()
color, guide = pg.load('3004', 'PART', '86')
pprint(guide)
pprint(color)

pass