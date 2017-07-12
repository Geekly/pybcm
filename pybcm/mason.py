"""
    Mason manages the solution and results of the optimization

"""
import pandas as pd


class Mason:

    def __init__(self, brickpile):
        # required data
        self._price = brickpile.df
        self._wanted = brickpile.wanted
        self._vendormap = brickpile.vendormap

        # working data
        self.shipping_cost = 3.00
        #self._simple_wanted = {e: self._wanted.get_wanted_qty(e) for e in self._wanted }
        #self.current_stock = dict.fromkeys(self._wanted.keys(), 0)
        #self.remaining = None
        #self.stock = DataFrame() # includes original wanted qty, current stock, amt remaining to buy

        # solution data
        self.solution = pd.DataFrame(columns=self._price.columns, index=self._price.index, data=None)

