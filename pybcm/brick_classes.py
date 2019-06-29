"""
Lego set class
"""
from typing import Union

from pybcm.brick_data import BrickData
from pybcm.config import BCMConfig
from pybcm.const import ItemType, NewUsed, GuideType
from pybcm.legoutils import legoColors
from pybcm.pricing import get_price_summaries, add_price_to_inv_df


class BrickItemBase:

    __itemtype__ = ''

    def __init__(self, itemid: str, itemtype: str, *args, **kwargs):
        self.itemid = itemid
        self.itemtype = itemtype
        self.name = 'NAME'

    @property
    def itemid(self):
        return self._itemid

    @itemid.setter
    def itemid(self, value):
        """set and validate itemid"""
        # todo: do a format check. Should be a string with letters and numbers only
        if value:
            self._itemid = str(value)
        else:
            raise ValueError(f"Item ID <{value}> is invalid")

    @property
    def itemtype(self):
        return self._itemtype

    @itemtype.setter
    def itemtype(self, value):
        if value in ItemType:
            self._itemtype = value
        else:
            raise ValueError(f"Item Type <{value}> is invalid.")

    def __repr__(self):
        return f"{{ {self.itemid}, {self.itemtype}, {self.name} }}"


class BrickPart(BrickItemBase):
    """ Provides validation for a lego element """

    __itemtype__ = ItemType.PART

    def __init__(self, itemid: str, color: str, **kwargs):

        super().__init__(itemid, self.__itemtype__)
        self.color = str(color)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value: Union[int, str]):
        value = int(value)
        if value in legoColors:
            self._color = str(value)
        else:
            raise ValueError(f"Color id <{value}> is invalid.")

    def get_price_details(self, bd: BrickData):
        itemid = self.itemid
        colorid = self.color
        return bd.get_part_price_details(itemid, colorid, new_or_used=NewUsed.N, guide_type=GuideType.stock)

    def __repr__(self):
        return f"{{ {self.itemid}, {self.itemtype}, {self.color}, {self.name} }}"


class BrickSet(BrickItemBase):

    __itemtype__ = ItemType.SET

    def __init__(self, itemid: str, **kwargs):
        super().__init__(itemid, self.__itemtype__, **kwargs)
        self.inv = None  # inventory dataframe
        self.prices = None
        self.inv_expanded = None  # inventory with expanded prices
        self.price = 0.0

    def get_inventory(self, bd: BrickData):
        self.inv = bd.get_set_inventory(self.itemid)
        return self.inv

    def piece_price_set(self, bd, new_or_used=NewUsed.N, guide_type=GuideType.stock):
        if self.inv is None:
            self.get_inventory(bd)
        self.prices = get_price_summaries(bd, self.inv, new_or_used=new_or_used, guide_type=guide_type)
        self.inv_expanded = add_price_to_inv_df(self.inv, self.prices)

        self.price = self.inv_expanded['total_part_cost'].sum()

        return self.price

if __name__ == '__main__':
    config = BCMConfig('../config/bcm.ini')
    bd = BrickData(config)

    brickpart = BrickPart('3006', '86')
    brickset = BrickSet('561410-1')
    inv = brickset.get_inventory(bd)

    prices = brickset.piece_price_set(bd, new_or_used='N', guide_type='stock')

    print(brickset.inv)
    print(brickset.inv_expanded)
    print(f"${brickset.price}")

