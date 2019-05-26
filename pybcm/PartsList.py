
import pandas as pd


class PartsList:
    """Parts list represented by a dataframe"""
    def __init__(self):
        self._data = pd.DataFrame()

    def load_partslist_csv(self, csv: str):
        self._data = self.read_partslist_csv(csv)
        if self._data.empty:
            return False
        else:
            return True

    @staticmethod
    def read_partslist_csv(csv: str)->pd.DataFrame:
        """Read the Partslist format CSV file from Stud.io"""
        try:
            pdf = pd.read_csv(csv, sep='\t', header=0, engine='python', na_values='', skipfooter=3,
                              dtype={'BLItemNo': str, 'BLColorId': int, 'LDrawColorId': int, 'Qty': int})
            pdf = pdf.fillna({'BLColorId': '', 'Qty': 0})
            pdf = pdf.rename(mapper={'BLItemNo': 'ItemId', 'BLColorId': 'Color'}, axis=1)
            pdf = pdf.drop(columns=['ElementId', 'LdrawId', 'LDrawColorId'])
            return pdf
        except FileNotFoundError as e:
            print(e)
            return None

    @property
    def data(self):
        return self._data