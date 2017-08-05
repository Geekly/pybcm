import pandas as pd


class PriceDataFrame:

    def __init__(self, data):
        self.df = pd.DataFrame(data)
