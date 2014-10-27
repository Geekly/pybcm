"""
Created on Oct 23, 2012

@author: khooks
"""


class LegoColor:
    """ Contains the color codes. """

    anycolorID = [11, 1, 9, 10, 86, 85, 7, 5, 3, 6, 2, 8, 88]

    _colorset = set(anycolorID)

    colors = {1:  'White',
              49: 'Very Light Gray',
              99: 'Very Light Bluish Gray',
              86: 'Light Bluish Gray',
              9:  'Light Gray',
              10: 'Dark Gray',
              85: 'Dark Bluish Gray',
              11: 'Black',
              59: 'Dark Red',
              5:  'Red',
              27: 'Rust',
              25: 'Salmon',
              26: 'Light Salmon',
              58: 'Sand Red',
              88: 'Reddish Brown',
              8:  'Brown',
              120: 'Dark Brown',
              69: 'Dark Tan'}

    @staticmethod
    def isvalidcolor(colorid):
        return int(colorid) in LegoColor._colorset


class LegoElement(object):
    """ Represents a Lego element and its attributes"""

    @staticmethod
    def joinelement(itemid, colorid):
        """ Create an elementid by combining the item and color."""
        return str(str(itemid) + "|" + str(colorid))

    @staticmethod
    def splitelement(elementid):
        """ Split an elementid into itemid and color tuple
        :rtype : string tuple (itemid, colorid)
        """
        return elementid.split("|")

    def __init__(self, itemid, colorid, itemname=None, itemtypeid=None, itemtypename=None, colorname=None,
                 wantedqty=0):
        """ A typical lego element

        :param itemid: Bricklink Item ID
        :param colorid: Lego Color ID
        :param itemname: Human Readable Item Name
        :param itemtypeid: Lego Type ID
        :param itemtypename: Human Readable Type Name
        :param colorname: Human Readable Type Name
        :param wantedqty: Quantity from the wanted list
        """

        self.itemid = str(itemid)
        self.colorid = str(colorid)
        self.itemname = str(itemname)
        self.itemtypeid = str(itemtypeid)
        self.itemtypename = str(itemtypename)
        self.colorname = str(colorname)
        self.wantedqty = int(wantedqty)

        self._elementid = LegoElement.joinelement(itemid, colorid)

        # Check if colorid exists in list
        try:
            if LegoColor.isvalidcolor(colorid): pass
            else:
                raise ValueError("Invalid Color ID")

        except ValueError as error:
            print(error)



    @property
    def elementid(self):
        return self._elementid

    def __str__(self):
        return self._elementid



if __name__ == "__main__":
    itemid = '35146'
    colorid = '88'
    wantedqty = '123'
    element = LegoElement.joinelement(itemid, colorid)
    print(element)
    print(LegoElement.splitelement(element))

    element = LegoElement(itemid, colorid, wantedqty)
    print(element.elementid)

    print(element.itemid)
    print(element.colorid)
    print(element.wantedqty)

    ele2 = LegoElement('6234', '4', 25)