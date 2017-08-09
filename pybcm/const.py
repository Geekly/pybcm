# Copyright (c) 2012-2017, Keith Hooks
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

BASE_URL = 'https://api.bricklink.com/api/store/v1/'
ITEM_TYPES = ('MINIFIG', 'PART', 'SET', 'BOOK', 'GEAR', 'CATALOG', 'INSTRUCTION', 'UNSORTED_LOT', 'ORIGINAL_BOX')
GUIDE_TYPES = ('sold', 'stock')
REGIONS = ('asia', 'africa', 'north_america', 'south_america', 'middle_east', 'europe', 'eu', 'oceania')
VATS = ('N', 'Y', 'O')
PRICEGUIDE_COLUMNS = ('item', 'color', 'new_or_used', 'avg_price', 'max_price', 'min_price', 'qty_avg_price',
                      'total_quantity', 'unit_quantity', 'currency_code')

API_PATH = {

    "base": 'https://api.bricklink.com/api/store/v1',
    "item": '/items/{type}/{no}',
    "item_image": '/items/{type}/{no}/images/{color_id}',
    "supersets": '/items/{type}/{no}/supersets',
    "subsets": '/items/{type}/{no}/subsets',
    "priceguide": '/items/{type}/{no}/price',
    "known_colors": '/items/{type}/{no}/colors'

}
