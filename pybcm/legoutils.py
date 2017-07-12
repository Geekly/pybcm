"""
Created on Oct 23, 2012

@author: khooks
"""
import json
import logging
from collections import namedtuple

# from collections import UserDict
logging.getLogger('pybcm.legoutils')

PriceTuple = namedtuple('PriceTuple', 'elementid storeid storename price qty')

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


class LegoColor():
    """ Dictionary of allowable color codes. """

    def __init__(self, colorid):
        colorid = int(colorid)
        try:
            if colorid in legoColors:
                self.colorid = colorid
                self.name = legoColors[colorid]
            else:
                raise KeyError("Color %s does not exist" % str(colorid))

        except KeyError as e:
            print(e)

    def __repr__(self):
        return "LegoColor<colorid:%s, name:%s>" % (self.colorid, self.name)


# module global dict of legocolors

ElementBase = namedtuple('ElementBase', 'elementid itemid colorid wantedqty itemname itemtypid itemtypename')


class LegoElement(ElementBase):
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

    def __new__(cls, itemid, colorid, wantedqty=0, itemname=None, itemtypeid='P', itemtypename='Part'):
        """ A typical lego element

        :param itemid: Bricklink Item ID
        :param colorid: Lego Color ID
        :param wantedqty: Quantity from the wanted list
        :param itemname: Human Readable Item Name
        :param itemtypeid: Lego Type ID
        :param itemtypename: Human Readable Type Name
        :param colorname: Human Readable Type Name

        """
        self = super(LegoElement, cls).__new__(cls, itemid, colorid, wantedqty=0, itemname=None, itemtypeid='P', itemtypename='Part')
        self._hash = hash(self.itemid) + hash(self.colorid)
        self.elementid = LegoElement.joinElement(self.itemid, self._colorid)
        #self.itemid = str(itemid)
        #self._colorid = int(colorid)
        # if self._colorid in legoColors:
        #     self.color = LegoColor(self._colorid)
        # self.wantedqty = int(wantedqty)
        # self.itemname = str(itemname)
        # self.itemtypeid = str(itemtypeid)
        # self.itemtypename = str(itemtypename)

        # self._elementid = LegoElement.joinElement(self.itemid, self._colorid)
    # def __new__(cls, vendor_id, vendor_name):
    #     self = super(Vendor, cls).__new__(cls, vendor_id, vendor_name)
    #     self._hash = hash(self.vendor_id) + hash(self.vendor_name)
    #     self._log = logging.getLogger("Vendor.py")
    #     return self
    #

    # def __repr__(self):
    #     return self.json
    #
    # @property
    # def xml(self):
    #     """Return an XML string of the Vendor."""
    #
    #     xmlstring = ''
    #     xmlstring += "<Vendor>\n"
    #     xmlstring += "<VendorID>" + str(self.vendor_id) + "</VendorID>\n"
    #     xmlstring += "<VendorName>" + str(self.vendor_name) + "</VendorName>\n"
    #     xmlstring += "</Vendor>\n"
    #     return xmlstring
    #
    # @property
    # def json(self):
    #     return '{{ "{0}": "{1}" }}'.format(self.vendor_id, self.vendor_name)
    #
    # def __str__(self):
    #     return self.xml


    def __init__(self, itemid, colorid, wantedqty=0, itemname=None, itemtypeid='P', itemtypename='Part'):
        """ A typical lego element

        :param itemid: Bricklink Item ID
        :param colorid: Lego Color ID
        :param wantedqty: Quantity from the wanted list
        :param itemname: Human Readable Item Name
        :param itemtypeid: Lego Type ID
        :param itemtypename: Human Readable Type Name
        :param colorname: Human Readable Type Name
        
        """

        self.itemid = str(itemid)
        self._colorid = int(colorid)
        if self._colorid in legoColors:
            self.color = LegoColor(self._colorid)
        self.wantedqty = int(wantedqty)
        self.itemname = str(itemname)
        self.itemtypeid = str(itemtypeid)
        self.itemtypename = str(itemtypename)

        self._elementid = LegoElement.joinElement(self.itemid, self._colorid)

    # def __dict__(self):
    #     _dict = {
    #         "elementid": self._elementid,
    #         "wantedqty": self.wantedqty,
    #         "itemid": self.itemid,
    #         "itemname": self.itemname,
    #         "itemcolor": self.colorName,
    #         "itemtypeid": self.itemtypeid,
    #     }
    #
    #     return _dict

    @property
    def elementId(self):
        return self._elementid

    @property
    def colorid(self):
        return self._colorid

    @property
    def colorName(self):
        return self.color.name

    @property
    def json(self):
        return json.dumps(self, sort_keys=False, indent=4)

    def __hash__(self):
        return hash(self.itemid) + hash(self.colorid)

    def __repr__(self):
        return self.json


if __name__ == "__main__":
    testitemid = '35146'
    testcolorid = '88'
    testwanted = 123

    elementId = LegoElement.joinElement(testitemid, testcolorid)
    print(elementId)
    print(LegoElement.splitElement(elementId))

    thsElement = LegoElement(testitemid, testcolorid, wantedqty=testwanted)

    #   print(LegoElement.legoColor.isValidColor(300))

    ele2 = LegoElement('6234', '9', 25)

    print(ele2)

    print(legoColors[144])

    l = LegoElement('3527', '10000')
    l = LegoElement('3527', 44)
