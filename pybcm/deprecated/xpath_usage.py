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


# selects the rows of the first Currently Available table
"""
Various xpaths used for selecting data. Currently deprecated.

STORE_LINKS = '//tbody/tr/td/table[3]/tbody/tr[5]/td[3]/table[3]/tbody/tr/td/table/tbody/tr[td/a]'
STORE_CHILD_LINK = './td/a/@href'
STORE_NAME = './td/a/img/@alt'
STORE_PRICE = './td[4]/text()'
STORE_QTY = './td[2]/text()'
CURRENTLY_AVAILABLE1 = '//tbody/tr/td/table[3]/tbody/tr[4]/td[3]'
CURRENTLY_AVAILABLE2 = '//table/tbody/tr/td/font/b[text()="Currently Available"]'
LOGOFF_URL = '/html/body/center/table[1]/tbody/tr/td/table/tbody/tr/td[3]/span/font/a'
"""

if __name__ == "__main__":
    pass
