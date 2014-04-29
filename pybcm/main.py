"""
Created on Jul 26, 2012

The main function loads the wanted list, optional price list, and calls the optimization
and shopping list functions.

@author: khooks
"""

from .bcm import *
from .wanted import WantedDict
from .bricklinkdata import BricklinkData
from .bcmconfig import BCMConfig
from .optimizer import *
# vendormap = VendorMap()


def main():
    # np.set_printoptions(threshold=np.nan)
    logging.basicConfig(level=logging.DEBUG)

    config = BCMConfig()

    wantedlistfilename = config.wantedfilename
    reloadpricesfromweb = config.reloadpricesfromweb  # set this to true if you want to update prices from the web and rewrite pricefilename
    pricefilename = config.pricefilename

    wanteddict = WantedDict()
    logging.info("Reading wanted list: " + wantedlistfilename)
    wanteddict.read(wantedlistfilename)
    # print("want this many items: " , wanteddict.totalcount)
    
    bricklink = BricklinkData()
                     
    if config.reloadpricesfromweb:
        logging.info("Reading prices from web")
        bricklink.readpricesfromweb(config.username, config.password, wanteddict)
        logging.info("Saving XML file")
        f = open(pricefilename, 'w')
        f.write(bricklink.toXML())
    else: 
        logging.info("Reading prices from file")
        f = open(pricefilename, 'r')
        
        bricklink.read(pricefilename)
        f.close()

    #vendormap = bricklink.vendormap
    bcm = BCMEngine(bricklink, wanteddict)

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
