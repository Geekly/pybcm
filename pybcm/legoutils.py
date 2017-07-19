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
Miscellaneous helpers and constants for the package
"""
import json
import logging

from collections import namedtuple

# from collections import UserDict
logging.getLogger('pybcm.legoutils')

Condition = namedtuple('Condition', 'USED NEW')(NEW=1, USED=2)

PriceTuple = namedtuple('PriceTuple', 'elementid storeid storename price qty condition')

legoColors = {
        1: 'White',
        2: 'Tan',
        3: 'Yellow',
        4: 'Orange',
        5: 'Red',
        6: 'Green',
        7: 'Blue',
        8: 'Brown',
        9: 'Light Gray',
        10: 'Dark Gray',
        11: 'Black',
        12: 'Trans-Clear',
        13: 'Trans-Black',
        14: 'Trans-Dark Blue',
        15: 'Trans-Light Blue',
        16: 'Trans-Neon Green',
        17: 'Trans-Red',
        18: 'Trans-Neon Orange',
        19: 'Trans-Yellow',
        20: 'Trans-Green',
        21: 'Chrome Gold',
        22: 'Chrome Silver',
        23: 'Pink',
        24: 'Purple',
        25: 'Salmon',
        26: 'Light Salmon',
        27: 'Rust',
        28: 'Flesh',
        29: 'Earth Orange',
        31: 'Medium Orange',
        32: 'Light Orange',
        33: 'Light Yellow',
        34: 'Lime',
        35: 'Light Lime',
        36: 'Bright Green',
        37: 'Medium Green',
        38: 'Light Green',
        39: 'Dark Turquoise',
        40: 'Light Turquoise',
        41: 'Aqua',
        42: 'Medium Blue',
        43: 'Violet',
        44: 'Light Violet',
        46: 'Glow In Dark Opaque',
        47: 'Dark Pink',
        48: 'Sand Green',
        49: 'Very Light Gray',
        50: 'Trans-Dark Pink',
        51: 'Trans-Purple',
        52: 'Chrome Blue',
        54: 'Sand Purple',
        55: 'Sand Blue',
        56: 'Light Pink',
        57: 'Chrome Antique Brass',
        58: 'Sand Red',
        59: 'Dark Red',
        60: 'Milky White',
        61: 'Pearl Light Gold',
        62: 'Light Blue',
        63: 'Dark Blue',
        64: 'Chrome Green',
        65: 'Metallic Gold',
        66: 'Pearl Light Gray',
        67: 'Metallic Silver',
        68: 'Dark Orange',
        69: 'Dark Tan',
        70: 'Metallic Green',
        71: 'Magenta',
        72: 'Maersk Blue',
        73: 'Medium Violet',
        74: 'Trans-Medium Blue',
        76: 'Medium Lime',
        77: 'Pearl Dark Gray',
        78: 'Metal Blue',
        80: 'Dark Green',
        81: 'Flat Dark Gold',
        82: 'Chrome Pink',
        83: 'Pearl White',
        84: 'Copper',
        85: 'Dark Bluish Gray',
        86: 'Light Bluish Gray',
        87: 'Sky Blue',
        88: 'Reddish Brown',
        89: 'Dark Purple',
        90: 'Light Flesh',
        91: 'Dark Flesh',
        93: 'Light Purple',
        94: 'Medium Dark Pink',
        95: 'Flat Silver',
        96: 'Very Light Orange',
        97: 'Blue-Violet',
        98: 'Trans-Orange',
        99: 'Very Light Bluish Gray',
        100: 'Glitter Trans-Dark Pink',
        101: 'Glitter Trans-Clear',
        102: 'Glitter Trans-Purple',
        103: 'Bright Light Yellow',
        104: 'Bright Pink',
        105: 'Bright Light Blue',
        106: 'Fabuland Brown',
        107: 'Trans-Pink',
        108: 'Trans-Bright Green',
        109: 'Dark Blue-Violet',
        110: 'Bright Light Orange',
        111: 'Speckle Black-Silver',
        113: 'Trans-Very Lt Blue',
        114: 'Trans-Light Purple',
        115: 'Pearl Gold',
        116: 'Speckle Black-Copper',
        117: 'Speckle DBGray-Silver',
        118: 'Glow In Dark Trans',
        119: 'Pearl Very Light Gray',
        120: 'Dark Brown',
        121: 'Trans-Neon Yellow',
        122: 'Chrome Black',
        123: 'Mx White',
        124: 'Mx Light Bluish Gray',
        125: 'Mx Light Gray',
        126: 'Mx Charcoal Gray',
        127: 'Mx Tile Gray',
        128: 'Mx Black',
        129: 'Mx Red',
        130: 'Mx Pink Red',
        131: 'Mx Tile Brown',
        132: 'Mx Brown',
        133: 'Mx Buff',
        134: 'Mx Terracotta',
        135: 'Mx Orange',
        136: 'Mx Light Orange',
        137: 'Mx Light Yellow',
        138: 'Mx Ochre Yellow',
        139: 'Mx Lemon',
        140: 'Mx Olive Green',
        141: 'Mx Pastel Green',
        142: 'Mx Aqua Green',
        143: 'Mx Tile Blue',
        144: 'Mx Medium Blue',
        145: 'Mx Pastel Blue',
        146: 'Mx Teal Blue',
        147: 'Mx Violet',
        148: 'Mx Pink',
        149: 'Mx Clear',
        150: 'Medium Dark Flesh',
        151: 'Speckle Black-Gold',
        152: 'Light Aqua',
        153: 'Dark Azure',
        154: 'Lavender',
        155: 'Olive Green',
        156: 'Medium Azure',
        157: 'Medium Lavender',
        158: 'Yellowish Green',
        159: 'Glow In Dark White',
        160: 'Fabuland Orange',
        161: 'Dark Yellow',
        162: 'Glitter Trans-Light Blue',
        163: 'Glitter Trans-Neon Green',
        164: 'Trans-Light Orange',
        165: 'Neon Orange',
        166: 'Neon Green'

    }


class WantedElement(namedtuple('ElementBase', 'itemid colorid wantedqty itemname itemtypeid itemtypename elementid')):
    """ Represents a Lego element and its attributes"""

    @staticmethod
    def joinElement(itemid, colorid):
        """ Create an elementid by combining the item and color."""
        return str(str(itemid) + "|" + str(colorid))

    @staticmethod
    def splitElement(elementid):
        """ Split an elementid into itemid and color tuple
        :rtype : string tuple (itemid, colorid)
        """
        return elementid.split("|")

    def __new__(cls, itemid, colorid, wantedqty=0, itemname=None, itemtypeid='P', itemtypename='Part', elementid=None):
        if int(colorid) in legoColors:
            elementid = WantedElement.joinElement(itemid, colorid)
            return super().__new__(cls, str(itemid), int(colorid), int(wantedqty), itemname, itemtypeid, itemtypename, elementid)
        else:
            raise KeyError("Color number not found")
        return None

    @property
    def json(self):
        return json.dumps(self._asdict(), sort_keys=True, indent=4)

    def __hash__(self):
        return hash(self.itemid) + hash(self.colorid)

    def __repr__(self):
        return self.json

if __name__ == "__main__":

    testitemid = '35146'
    testcolorid = '88'
    testwanted = 123

    elementId = WantedElement.joinElement(testitemid, testcolorid)
    print(elementId)
    print(WantedElement.splitElement(elementId))

    thisElement = WantedElement(testitemid, testcolorid, wantedqty=testwanted)
    print(thisElement)
    print(thisElement.elementid)
    print(thisElement.itemid)
    print(thisElement.colorid)
    print(legoColors[thisElement.colorid])
    print(thisElement.wantedqty)

