import pytest

from PartsList import read_partslist_csv
from pybcm.legoutils import Color


def test_Color():

    color = Color(10)
    assert str(color) == 'Dark Gray'
    print(color.__repr__())

    color.id = 8
    assert str(color) == 'Brown'
    print(color.__repr__())

    assert color.id_is_valid(0) is False
    assert color.id_is_valid(125)
    assert color.id_is_valid('125')

    color.id = 125

    with pytest.raises(Exception) as context:
        color.id = 0

    with pytest.raises(Exception) as context:
        color.id = 'ten'


def test_read_partslist_csv():
    partslist = r'../resources/Sampledata/Cougar_partslist.csv'
    pdf = read_partslist_csv(partslist)
    print(pdf)