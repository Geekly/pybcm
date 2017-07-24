import log
from db import *

logger = log.setup_custom_logger('pybcm')

conn = sqlite3.connect('../database/pybcm.db')
cur = conn.cursor()


aset = { 'itemid': '10001',
             'description': 'Super Brickabrack',
             'est_price': 250.00 }

columns = ', '.join(aset.keys())
placeholders = ':'+', :'.join(aset.keys())
query = 'INSERT OR REPLACE INTO sets (%s) VALUES (%s)' % (columns, placeholders)

with conn:
    result = cur.execute(query, aset)
#result = serialize_set(aset)

aset['description'] = "BEST SET BUY IT"
#result = serialize_part(aset)
with conn:
    result = cur.execute(query, aset)

apart = {'itemid': '3004',
        'name': '2 X 1 Brick'}

with conn:
    result = serialize_part(apart)

aprices = {'itemid': '3004',
           'color': '86',
           'new_or_used': 'U',
           'avg_price': .12,
           'max_price': .25,
           'min_price': .08,
           'qty_avg_price': .12,
           'unit_quantity': 10,
           'total_quantity': 1000}

with conn:
    result = serialize_part_prices(aprices)
