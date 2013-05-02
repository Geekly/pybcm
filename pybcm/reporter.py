import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

class reporter(object):
    """description of class"""


    """
Make a histogram of normally distributed random numbers and plot the
analytic PDF over it
"""
    def __init__(self, bcm):
        self.bcm = bcm

    def pricehistogram( self, elementid ):
       
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

if __name__ == '__main__':

    