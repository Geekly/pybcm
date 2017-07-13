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


from pybcm.bcmdata import bcmdata

# TODO: refactor, add to seperate file, and add to unit tests
class VendorStats():
    """Process bcmdata and organize stats.

        Attributes:
            data(BCMData): the BCMData object
            ELEMWEIGHTS(ndarray): numpy array of element weights
            NUMVENDORS(int): number of vendors in vendorlist
            NUMELEMS(int): number of elements in elementlist
            ITEMS(ndarray): points to elementlist
            ITEMSPERVENDOR(ndarray): ITEMSPERVENDOR[vendorid] = num different items stocked by vendorid
            VENDORSPERELEMENT(ndarray): VENDORSPERELEMENT[elementid] = num vendors stocking elementid
            TOTALPERVENDOR(ndarray): TOTALPERVENDOR[
    """

    def __init__(self, bcmdata):
        self.update(bcmdata)

        self.data = bcmdata
        self.elemweights = bcmdata.elementweights()  # numpy array
        self.numvendors = len(self.data.vendorlist)
        self.numelems = len(self.data.elementlist)
        self.items = len(self.data.elementlist)
        self.itemspervendor = self.__itemspervendor()
        self.vendorsperelement = self.__vendorsperelement()
        self.totalvendor = self.__totalitemspervendor()
        self.vdict = self.__makedictionary()

    def update(self, bcmdata):
        self.data = bcmdata
        self.elemweights = bcmdata.elementweights()  # dictionary
        self.numvendors = len(self.data.vendorlist)
        self.numelems = len(self.data.elementlist)
        self.items = len(self.data.elementlist)
        self.itemspervendor = self.__itemspervendor()
        self.vendorsperelement = self.__vendorsperelement()
        self.totalvendor = self.__totalitemspervendor()
        self.vdict = self.__makedictionary()

    def __itemspervendor(self):
        s = self.data.stock
        itemspervendor = (s > 0).sum(0)
        return itemspervendor

    def __totalitemspervendor(self):
        # for each vendor
        # sum the min( stock, wanted) for each element
        # vitems = np.zeros(shape=(self.NUMVENDORS), dtype='int')
        stockarray = self.data.stock
        wantedarray = self.data.wanted.reshape(len(self.data.elementlist), 1)
        vitems = np.minimum(stockarray, wantedarray).sum(0)
        vitems.mask = stockarray.mask
        # print(vitems)
        # print(np.minimum(stockarray,wantedarray))
        # print(np.minimum(stockarray,wantedarray).sum(0))
        # for vidx, stock in enumerate(stockarray.T): #enumerate over the columns in stock
        #    for eidx, wanted in enumerate(wantedarray): #enumerate over each element in the wanted list
        #        vitems[vidx] += min( stock[eidx], wanted )
        return vitems

    def __vendorsperelement(self):
        s = self.data.stock
        vendorsperelement = (s > 0).sum(1)
        return vendorsperelement

    def stockbywanted(self):
        return self.__stockbywanted()

    def __stockbywanted(self):
        """  
        Calculates a sorting helper for vendors.  The more items a vendor can completely fill, the higher its
            value.
        SBW = stock / wanted
        SBW = 1.0 if stock/wanted >= 1.0 ELSE stock/wanted
        """
        stockarray = self.data.stock.astype('float')
        wantedarray = self.data.wanted.reshape(self.numelems, 1).astype('float')
        stockbywant = stockarray / wantedarray
        greaterthan1 = stockbywant >= 1.0  # creates a true/false array that will be used in the next line
        stockbywant[greaterthan1] = 2.0  # completely filling an order counts 3X more than a partial fill
        return stockbywant

    def vendorstockweights(self):
        return self.__stockbywanted().sum(0)

    def vendorpriceweights(self):
        # function of element weight, vendor price, vendor qty (gets credit for how many it has)
        # sort by self.data.elementlist
        sortedweights = self.elemweights  # aligned with elementlist now
        # print(sortedweights)
        elemweight = np.array(sortedweights, dtype='float').reshape((len(self.elemweights), 1))
        pricearray = self.data.prices
        stockarray = self.data.stock
        avgpricearray = self.avgprices()
        # print(elemweight)
        # print(pricearray)

        priceweight = elemweight / pricearray
        # for vindex, vendor in enumerate(self.data.vendorlist):
        #    totalweight = 0
        #    for eindex, element in enumerate(self.data.elementlist):
        #        pricew = ewd[element]/p[eindex, vindex]
        #        totalweight += pricew
        #    costweights[vindex] = totalweight
        # return costweights
        # define some weight based on elementweights and qty
        return priceweight

    def avgprices(self):
        # data[elementid, vendorid] = [price, qty]
        p = self.data.prices
        avgprices = p.sum(1) / (p > 0).sum(1)  # the 1 causes
        return avgprices

    def vendorweights(self):
        # Use nd arrays

        vendorstockweights = self.__stockbywanted().sum(0) * 2.5
        vendorpriceweights = self.vendorpriceweights().sum(0)

        print(vendorstockweights)
        print(vendorpriceweights)

    def __makedictionary(self):
        vdict = dict()
        # avgprices = self.data.avgprices()
        for vindex, vendor in enumerate(self.data.vendorlist):
            vdict[vendor] = (self.itemspervendor[vindex], self.totalvendor[vindex])
        return vdict

    def report(self):
        print("There are %d items to purchase" % self.items)
        print("%d vendors have the following number distinct items available:" % self.numvendors)
        print("Vendors per element", self.itemspervendor)
        print("Elements per vendor", self.vendorsperelement)
        print(self.vdict)
        # vlist = self.data.vendorlist
