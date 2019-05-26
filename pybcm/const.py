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

from collections import namedtuple

__all__ = ['ItemType', 'GuideType', 'Region', 'Vats', 'NewUsed', 'PRICEGUIDE_COLUMNS']

ITEM_TYPES = ['MINIFIG', 'PART', 'SET', 'BOOK', 'GEAR', 'CATALOG', 'INSTRUCTION', 'UNSORTED_LOT', 'ORIGINAL_BOX']
ItemTuple = namedtuple('item_tuple', ITEM_TYPES)
ItemType = ItemTuple._make(ITEM_TYPES)

GUIDE_TYPES = ['sold', 'stock']
GuideTuple = namedtuple('guide_tuple', GUIDE_TYPES)
GuideType = GuideTuple._make(GUIDE_TYPES)

REGIONS = ['asia', 'africa', 'north_america', 'south_america', 'middle_east', 'europe', 'eu', 'oceania']
RegionTuple = namedtuple('region_tuple', REGIONS)
Region = RegionTuple._make(REGIONS)

VATS = ['N', 'Y', 'O']
VatsTuple = namedtuple('vats_tuple', VATS)
Vats = VatsTuple._make(VATS)

NEWUSED = ['N', 'U']
NewUsedTuple = namedtuple('new_used_tuple', NEWUSED)
NewUsed = NewUsedTuple._make(NEWUSED)


# define priceguide fields as sets to be used for comparison as order doesn't matter
COMMON_FIELDS = {'item_id', 'itemtype', 'color_id'}
PRICEGUIDE_COLUMNS = {'item_id', 'color_id', 'new_or_used', 'itemtype', 'avg_price', 'max_price', 'min_price', 'qty_avg_price',
                      'total_quantity', 'unit_quantity', 'currency_code'}
HDF_PRICE_COLUMNS = PRICEGUIDE_COLUMNS


