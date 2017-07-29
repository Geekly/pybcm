# Copyright (c) 2017, Keith Hooks
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import logging
import sqlite3
import time

import log

logger = logging.getLogger('pybcm.db')

conn = sqlite3.connect('../database/pybcm.db')


def serialize_set(aset):
    """aset = { 'itemid': '10001',
            'description': 'Super Brickabrack',
            'est_price': 250.00 } """
    columns = ', '.join(aset.keys())
    placeholders = ':' + ', :'.join(aset.keys())
    query = 'INSERT OR REPLACE INTO sets (%s) VALUES (%s)' % (columns, placeholders)
    with conn:
        result = conn.execute(query, aset)
        logger.info(query)
    return result


def serialize_part(apart):
    """apart = { 'itemid': '3004',
                 'name': '2 X 1 Brick' } """
    columns = ', '.join(apart.keys())
    placeholders = ':' + ', :'.join(apart.keys())
    query = 'INSERT OR REPLACE INTO parts (%s) VALUES (%s)' % (columns, placeholders)
    with conn:
        result = conn.execute(query, apart)
        logger.info(query)
    return result


def serialize_part_prices(aprices):
    """aprices = {'itemid': '3004',
                'color': '86',
                'new_or_used': 'U',
                'avg_price': .12,
                'max_price': .25,
                'min_price': .08,
                'qty_avg_price': .12,
                'unit_quantity': 10,
                'total_quantity': 1000 } """
    dbname = 'part_prices'
    columns = ', '.join([*aprices.keys(), 'age'])
    placeholders = ':' + ', :'.join([*aprices.keys(), 'age'])
    aprices['age'] = time.time()
    query = 'INSERT OR REPLACE INTO %s (%s) VALUES (%s)' % (dbname, columns, placeholders)
    with conn:
        result = conn.execute(query, aprices)
        logger.info(query)
    return result


def prune_pull_list(pull_list):
    """
        select the records from the pull_list that don't already exist in the db. These
        are the ones to download from the website.

        pull_list = [('6587', '10', 'N'),
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
        cur.executemany('insert into pair values (?, ?, ?)', pull_list)

        # find items not present in the db
        query = "SELECT pair.* FROM pair LEFT JOIN part_prices " \
                "ON pair._itemid=part_prices.itemid " \
                "AND pair._color=part_prices.color " \
                "AND pair._new_or_used=part_prices.new_or_used " \
                "WHERE part_prices.itemid is NULL " \
                "OR part_prices.color is NULL " \
                "OR part_prices.new_or_used is NULL "
        logger.info(query)
        to_pull = cur.execute(query).fetchall()

        # select all of the prices that already exist
        query = "SELECT part_prices.* " \
                "FROM part_prices " \
                "INNER JOIN pair " \
                "ON pair._itemid = part_prices.itemid " \
                "AND pair._color = part_prices.color " \
                "AND pair._new_or_used = part_prices.new_or_used "

        existing_prices = cur.execute(query).fetchall()

        # return price info for items that are present

    return to_pull, existing_prices
        # create a temporary db


if __name__=='__main__':
    log.setup_custom_logger('pybcm')

    aset = { 'itemid': '10001',
             'description': 'Super Brickabrack',
             'est_price': 250.00 }

    cur.execute("insert into people values (?, ?)", (who, age))


