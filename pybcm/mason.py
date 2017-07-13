"""
    Mason manages the solution and results of the optimization

"""
import pandas as pd


class Mason:

    def __init__(self, brickpile):
        # required data
        # TODO: change to reference individual price and qty dataframes
        #self._prices = brickpile.df
        self.__price_df = brickpile.price_frame
        self.__qty_df = brickpile.qty_frame
        self.__wanted = brickpile.wanted
        self.__vendormap = brickpile.vendormap

        # working data
        self.shipping_cost = 3.00
        #self._simple_wanted = {e: self._wanted.get_wanted_qty(e) for e in self._wanted }
        #self.current_stock = dict.fromkeys(self._wanted.keys(), 0)
        #self.remaining = None
        #self.stock = DataFrame() # includes original wanted qty, current stock, amt remaining to buy

        # solution data
        # solution data is a table of elements vs. vendors with qty only as the value
        self.solution = pd.DataFrame(columns=self._price.columns, index=self._price.index, data=None)

    #TODO: calculate the part cost of a solution

    #TODO: calculate the total cost of a solution