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

"""
Created on Jul 26, 2012

The main function loads the wanted list, optional price list, and calls the optimization
and shopping list functions.

@author: khooks
"""

from config import BCMConfig
from log import setup_custom_logger
from vendorstats import VendorStats
from wanted import WantedDict


# vendor_map = VendorMap()
# TODO: add arguement parsing

def main():

    logger = setup_custom_logger('root')

    # process command line instructions
    #TODO: process command instructions

    # load configuration
    config = BCMConfig('../config/bcm.ini')  # create the settings object and load the file

    wantedlistfilename = config.wantedfilename
    # reloadpricesfromweb = config.reloadpricesfromweb  # set this to true if you want to update prices from the web and rewrite pricefilename
    pricefilename = config.pricefilename

    logger.info("Reading wanted list: " + wantedlistfilename)
    # create a WantedDict and read the list into it
    wanteddict = WantedDict()
    wanteddict.read(wantedlistfilename)
    logger.info("Loaded {0} items from {1}".format(wanteddict.totalcount, wantedlistfilename))

    # process the wanted list, loading prices from the web
    #bricklink = BrickPile()
                     
    if config.reloadpricesfromweb is True:
        logger.info("Reading prices from web")
        #bricklink.readpricesfromweb(config.username, config.password, wanteddict)
        logger.info("Saving XML file")
        #f = open(pricefilename, 'w')
        #f.write(bricklink.xmlvendordata())
    else: 
        logger.info("Reading prices from file")
        bricklink.read(pricefilename)

    #vendor_map = bricklink.vendor_map
    #bcm = BCMManager(bricklink, wanteddict)

    #bcm.prunevendorsbyavgprice()

    #print( bcm.data.elementlist)
    #print( bcm.data.WANTED)
    #print( bcm.data.avgprices())
    #print( bcm.data.avgprices(stockweighted=True))

    #ndo = Optimizer(bcm.data, search=SearchTypes.Swap)
    #ndo.solve()
    #print( ndo.solutions.summary() )
    
    #print( ndo.solutions.best() )
    
    #rep = reporter(bcm)
    #rep.allpartsbarchart()
    #shopping = ShoppingList(ndo.solutions.best())
    #print( shopping.XMLforBricklink() )
    
    vs = VendorStats(bcm.data)
    #print(vs.stockbywanted().sum(0) )
    print(vs.vendorpriceweights())
    #print bcm.data.count()
    
if __name__ == '__main__':
    
    main()

    '''
    cp = cProfile.Profile()
       
    cp.run('main()')
    
    ps = pstats.Stats(cp)
    ps.sort_stats('time')
    ps.print_stats(0.2)
    '''
