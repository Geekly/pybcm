import pytest

from config import BCMConfig
from dataframe import rest_wrapper


@pytest.fixture(scope="module")
def rw():
    config = BCMConfig('../config/bcm.ini')
    _rw = rest_wrapper(config)
    return _rw

@pytest.fixture(scope="module")
def price_tuple():
    _price_tuple = ({
                        "item": {
                            "no": "3006",
                            "type": "PART"
                        },
                        "new_or_used": "N",
                        "currency_code": "USD",
                        "min_price": "0.0525",
                        "max_price": "3.4290",
                        "avg_price": "0.5332",
                        "qty_avg_price": "0.3653",
                        "unit_quantity": 978,
                        "total_quantity": 14810,
                        "price_detail": [
                            {
                                "quantity": 1,
                                "unit_price": "0.6384",
                                "seller_country_code": "US",
                                "buyer_country_code": "US",
                                "date_ordered": "2017-02-16T23:58:22.797Z",
                                "qunatity": 1
                            },
                            {
                                "quantity": 1,
                                "unit_price": "0.5925",
                                "seller_country_code": "US",
                                "buyer_country_code": "US",
                                "date_ordered": "2017-02-18T05:42:10.397Z",
                                "qunatity": 1
                            }
                        ]
                    },
                    {
                        "item": {
                            "no": "3006",
                            "type": "PART"
                        },
                        "new_or_used": "U",
                        "currency_code": "USD",
                        "min_price": "0.0525",
                        "max_price": "3.4290",
                        "avg_price": "0.5332",
                        "qty_avg_price": "0.3653",
                        "unit_quantity": 678,
                        "total_quantity": 1810,
                        "price_detail": [
                            {
                                "quantity": 1,
                                "unit_price": "0.6384",
                                "seller_country_code": "US",
                                "buyer_country_code": "US",
                                "date_ordered": "2017-02-16T23:58:22.797Z",
                                "qunatity": 1
                            },
                            {
                                "quantity": 1,
                                "unit_price": "0.5925",
                                "seller_country_code": "US",
                                "buyer_country_code": "US",
                                "date_ordered": "2017-02-18T05:42:10.397Z",
                                "qunatity": 1
                            }
                        ]
                    })
    return _price_tuple


def test_get_item(rw):
    pass


def test_get_supersets(rw):
    pass


def test_get_subsets(rw):
    pass


def test_get_priceguide_df(rw):
    df1 = rw.get_priceguide_summary_df('3008', 'PART', '10', guide_type='sold')
    df2 = rw.get_priceguide_summary_df('3008', 'PART', '10', guide_type='stock')

    assert {'item', 'color'}.issubset(set(df1.columns))
    assert {'item', 'color'}.issubset(set(df2.columns))

    assert df1.shape[0] == 2
    assert df2.shape[0] == 2

    print(df1.head())
    print(df2.head())


def test_get_part_price_guide_df(rw):
    df = rw.get_part_priceguide_summary_df('3008', '10')
    assert set(('item', 'color')).issubset(set(df.columns))
    assert df.shape[0] == 2


def test_get_known_colors(rw):
    colors_df = rw.get_known_colors('3008', 'PART')
    assert colors_df.index.name == 'color_id'
    print(colors_df.head())


def test_get_part_priceguide_details(rw):
    df = rw.get_part_priceguide_details_df('3008', '34', new_or_used='U')
    print(df)
