import pytest
from pandas.testing import assert_frame_equal

from brick_classes import Brick
from brick_data import BrickData
from config import BCMConfig
from const import PRICEGUIDE_COLUMNS, NewUsed


def assert_frame_not_equal(df1, df2, **kwargs):
    # assert_frame_equal exists, but we need the ability to assert that frames are not equal
    try:
        assert_frame_equal(df1, df2, **kwargs)
        raise AssertionError('DataFrames are equal.')
    except AssertionError:
        pass


@pytest.fixture(scope="module")
def bd():
    config = BCMConfig('../config/bcm.ini')
    _bd = BrickData(config)
    return _bd


@pytest.fixture(scope="module")
def brick():
    _brick = Brick('3008', 'PART', '10')
    return _brick


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


def test_get_priceguide_summary_df(bd):
    df1 = bd.get_price_summary('3008', 'PART', '10', new_or_used=NewUsed.U, guide_type='sold')
    df2 = bd.get_price_summary('3008', 'PART', '10', new_or_used=NewUsed.U, guide_type='stock')

    assert {'item_id', 'color_id'}.issubset(set(df1.columns))
    assert {'item_id', 'color_id'}.issubset(set(df2.columns))

    # assert df1.shape[0] == 2
    # assert df2.shape[0] == 2

    assert_frame_not_equal(df1, df2, check_like=True)

    print(df1.head())
    print(df2.head())


def test_get_part_price_guide_summary_df(bd):
    df = bd.get_part_price_summary('3008', '10', new_or_used=[NewUsed.U, NewUsed.N])
    assert {'item_id', 'color_id'}.issubset(set(df.columns))
    assert set(PRICEGUIDE_COLUMNS).issubset(set(df.columns))
    assert df.shape[0] == 2
    print(df.head())


def test_get_part_priceguide_details(bd):
    df = bd.get_part_price_details('3008', '34', new_or_used='U', guide_type='stock')
    assert {'quantity', 'shipping_available', 'unit_price'}.issubset(set(df.columns))
    print(df.head(5))
    df = bd.get_part_price_details('3008', '34', new_or_used='U', guide_type='sold')
    assert {'buyer_country_code', 'date_ordered', 'quantity', 'seller_country_code', 'unit_price'}.issubset(
        set(df.columns))
    print(df.head(5))


def test_get_known_colors(bd):
    colors_df = bd.get_known_colors('3008', 'PART')
    assert colors_df.index.name == 'color_id'
    assert 'quantity' in colors_df.columns
    print(colors_df.head())


def test_priceguide_summary_df_from_json(bd, price_tuple):
    s1 = bd._summary_df_from_json(price_tuple, '11', sold_or_stock='sold')
    s2 = bd._summary_df_from_json(price_tuple, '12', sold_or_stock='stock')
    print(s1)
    print(s2)


def test_priceguide_details_df_from_json(bd, price_tuple):
    d1 = bd._details_df_from_json(price_tuple[0])  # called for a single 'N' or 'U'
    d2 = bd._details_df_from_json(price_tuple[1])
    print(d1.append(d2))


def test_get_brick_price_summary(bd, brick):
    d1 = bd.get_brick_price_summary(brick)
    print(d1)


def test_get_all_colors(bd):
    d1 = bd.get_all_colors()
    print(d1)