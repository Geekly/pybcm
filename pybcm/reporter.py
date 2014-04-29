import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

class reporter(object):
    """
    Make a histogram of normally distributed random numbers and plot the
    analytic PDF over it
    """

    def __init__(self, bcm):
        self.bcm = bcm
        self.data = bcm.data

    def partpricehistogram( self, elementid ):
       
        fig = plt.figure()
        ax = fig.add_subplot(111)
        index = self.bcm.elementlist.index(elementid)
        x = self.bcm.pricearray[index] #first row in the price array
        #strip zeros
        x = x[x > 0]
        mu = np.mean(x)
        sigma = np.std(x)
        
        n, bins, patches = ax.hist(x, 20, normed=1, facecolor='green', alpha=0.75)
        bincenters = 0.5*(bins[1:]+bins[:-1])
        # add a 'best fit' line for the normal PDF
        y = mlab.normpdf( bincenters, mu, sigma)
        l = ax.plot(bincenters, y, 'r--', linewidth=1)

        ax.set_xlabel(elementid)
        ax.set_ylabel('Price')
        #ax.set_title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
        ax.set_xlim(x.min(), x.max())
        ax.set_ylim(y.min(), y.max())
        ax.grid(True)

        plt.show()
        
    def allpartsbarchart( self ):
       
        fig = plt.figure()
        ax = fig.add_subplot(111)
        N = len( self.data.WANTED )
        ind = np.arange(N)
        width = .2
        
        elements = self.data.elementlist[:]       
        avgprices = self.data.avgprices()/100 #Y1
        maxprice = avgprices.max()
        totalcosts = avgprices * self.data.WANTED #Y2

        #index = self.bcm.elementlist.index(elementid)
        totalcosts, prices, elements = list(zip(*sorted(zip(totalcosts, avgprices, elements), reverse = True)))
        
        costbars = ax.bar(ind, totalcosts, color='green')
        pricebars = ax.bar(ind, prices, color='blue')
        
        maxheight = int( max( [ bar.get_height() for bar in costbars ] ) * 1.2 )
        
        def autolabel(rects, elements):
    # attach some text labels
            for i, rect in enumerate(rects):
                height = rect.get_height()
                ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, elements[i],
                ha='center', va='bottom', rotation='vertical')
        
        autolabel(costbars, elements)
        
        #ax.tick_params(axis='x', )
        print( maxheight )
        yticks = [ x for x in range(0, maxheight)]
        ax.set_yticks( yticks )
        #ax.set_xticks(ind)
        #ax.set_xticklabels( elements )
        
        ax.legend( (pricebars[0], costbars[0]), ('Price', 'Total'))
        plt.show()    
    
    def stockhistogram( self ):
        #create a histogram showing how many parts a vendor can supply
        itemcounts = self.bcm.itemspervendor()
        fig = plt.figure()
        ax = fig.add_subplot(111)
        
        x, y = self.count_unique(itemcounts)
        
        mu = np.mean(x)
        sigma = np.std(x)
        
        n, bins, patches = ax.hist(x, len(x), normed=1, facecolor='green', alpha=0.75)
        bincenters = 0.5*(bins[1:]+bins[:-1])
        # add a 'best fit' line for the normal PDF
        
        #l = ax.plot(x, y, 'r--', linewidth=1)
        b = ax.bar(x, y, align='center')
        ax.set_xlabel('Items per Vendor')
        ax.set_ylabel('Vendor Count')
        #ax.set_title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
        ax.set_xlim(x.min()-1, x.max()+1)
        ax.set_ylim(0, y.max()*1.1)
        ax.grid(True)

        plt.show()
    
    def count_unique(self, keys):
        uniq_keys = np.unique(keys)
        bins = uniq_keys.searchsorted(keys)
        return uniq_keys, np.bincount(bins)    
               
    def elementstats( self ):
        wanted = self.data.wantedarray
        avg = self.bcm.avgprices() #uses pricearray indices
        print("Elements", str(self.data.elementlist))
        print("Wanted: ", str(wanted)) 
        print("Average prices: " , str(avg))
        print("Element weights: " , str(avg * wanted)) 
        print("Relative weights:" , str(self.bcm.elementweights()))     
        
    def vendorstats( self ):
        prices = self.data.prices
        print(("There are a total of " + str(len(self.data.vendorlist)) + " vendors."))
        itemcounts = self.bcm.itemspervendor()
        avg = self.bcm.avgprices()
        itemsper, counts = self.count_unique(itemcounts)
        for (per, count) in zip(itemsper, counts):
            print(count, " vendors have at most <", per, "> items") 
        #print "Items per vendor: ", zip(itemsper, counts) 
        

if __name__ ==  '__main__':
   
    pass
    