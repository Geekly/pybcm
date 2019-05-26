from pybcm.PartsList import PartsList

def test_PartsList():

    pl = PartsList()
    pdf = pl.read_partslist_csv(r'../resources/Sampledata/Cougar_partslist.csv')
    print(pdf)


