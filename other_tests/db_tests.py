from pprint import pprint

from db import *

logger = log.setup_custom_logger('pybcm')

#conn = sqlite3.connect('../database/pybcm.db')
#cur = conn.cursor()

#
# aset = { 'itemid': '10001',
#              'description': 'Super Brickabrack',
#              'est_price': 250.00 }
#
# columns = ', '.join(aset.keys())
# placeholders = ':'+', :'.join(aset.keys())
# query = 'INSERT OR REPLACE INTO sets (%s) VALUES (%s)' % (columns, placeholders)
#
# with conn:
#     result = cur.execute(query, aset)
# #result = serialize_set(aset)
#
# aset['description'] = "BEST SET BUY IT"
# #result = serialize_part(aset)
# with conn:
#     result = cur.execute(query, aset)
#
# apart = {'itemid': '3004',
#         'name': '2 X 1 Brick'}
#
# with conn:
#     result = serialize_part(apart)
#
# aprices = {'itemid': '3004',
#            'color': '86',
#            'new_or_used': 'U',
#            'avg_price': .12,
#            'max_price': .25,
#            'min_price': .08,
#            'qty_avg_price': .12,
#            'unit_quantity': 10,
#            'total_quantity': 1000}
#
# with conn:
#     result = serialize_part_prices(aprices)


need_set = {('10247', '86', 'U'), ('10247', '85', 'N'), ('10247', '85', 'U'), ('6587', '10', 'N'), ('2356', '9', 'N'), ('4589', '1', 'U'), ('3706', '11', 'N'), ('2573', '9', 'N'), \
            ('3043', '1', 'N'), ('3005', '9', 'N'), ('6232', '9', 'N'), ('6249', '5', 'U'), ('3622', '9', 'U'), \
            ('3700', '7', 'N'), ('32039', '9', 'U'), ('30359b', '12', 'N'), ('4070', '9', 'U'), ('30374', '10', 'U')}
need_list = list(need_set)
print(need_list)

# This works in sqlite console but not here
# SELECT * from part_prices where (itemid, color) in (('6587', '10'));
# This doesn't select the pairs
# select * from (select itemid, color from part_prices where color in ('10', '9', '11')) where itemid in ('6587', '4589');

def prune_list(needed_list):
    """
        select the records from the needed_list that don't already exist in the db
    
        need_list = [('6587', '10', 'N'),
                    ('3700', '7', 'U'),...]
                    
        CREATE TEMPORARY TABLE pair (itemid_ INTEGER, color_ INTEGER, new_or_used_ INTEGER);
        INSERT INTO pair (itemid_, color_, new_or_used_) VALUES ('6587', '9', 'N');
        INSERT INTO pair (itemid_, color_, new_or_used_) VALUES ('2356', '1', 'U');

        SELECT pair.*
        from pair
        left join price_guide
        ON pair.itemid_ = price_guide.itemid
        AND pair.color_ = price_guide.color
        AND pair.new_or_used_ = price_guide.new_or_used
        where price_guide.color is NULL
        OR price_guide.itemid is null
        or price_guide.new_or_used is null;

    """
    with sqlite3.connect('../database/pybcm.db') as conn:
        cur = conn.cursor()
        cur.execute('''drop table pair''')
        cur.execute('''create table if not exists pair 
                     (_itemid text, _color text, _new_or_used text)''')
        cur.executemany('insert into pair values (?, ?, ?)', need_list)
        query = "SELECT pair.* FROM pair LEFT JOIN part_prices " \
                "ON pair._itemid=part_prices.itemid " \
                "AND pair._color=part_prices.color " \
                "AND pair._new_or_used=part_prices.new_or_used " \
                "WHERE part_prices.itemid is NULL " \
                "OR part_prices.color is NULL " \
                "OR part_prices.new_or_used is NULL "
        pprint(query)
        result = cur.execute(query).fetchall()
        return result
    # create a temporary db

short_list = prune_list(need_list)

#result = cur.execute("select * from (select itemid, color from part_prices where color in ('10', '9', '11')) where itemid in ('6587', '4589')")
"""
CREATE TEMPORARY TABLE pair (itemid_ INTEGER, color_ INTEGER);
INSERT INTO pair (itemid_, color_) VALUES ('6587', '9');
INSERT INTO pair (itemid_, color_) VALUES ('2356', '1');

-- the tuple should be unique
SELECT     price_guide.*
FROM       price_guide
INNER JOIN pair
        ON pair.itemid_ = price_guide.itemid
       AND pair.color_ = price_guide.color;

"""
print(short_list)

# select itemid, color from (select itemid, color where color in ()) where itemid in ()

# select itemid, color from part_prices where (itemid, color) in (('11455','11'));

"""SELECT *
  FROM mytable
 WHERE (group_id, group_type) IN (
                                  VALUES ('1234-567', 2), 
                                         ('4321-765', 3), 
                                         ('1111-222', 5)
                                 );"""