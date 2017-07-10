"""
Created on Oct 23, 2012

@author: khooks
"""
import logging
import numpy as np
import pandas as pd
from pandas import DataFrame
import pprint

import log
from elementreader import ElementWebReader
from legoutils import LegoElement
from vendors import VendorMap

logger = logging.getLogger('root')


def dataframe_from_pricelist(element_id, price_list):
    _data = {(d.storeid, param): d.__getattribute__(param) for d in price_list for param in ['price', 'qty']}
    _index = [element_id]
    _df = DataFrame(_data, index=_index)
    return _df


class BrickPile:
    """Stores bricklink wanted and price information.
        data is a dictionary of the format:
        [storeID, quantity, price]
        data[elementid] = { [vendor1id, vendor1qty, vendor1price],
                                [vendor2id, vendor2qty, vendor2price],
                                ... }
        where elementid is itemid|colorid

        this class also works on the vendor_map, which maps vendor ID to vendor name

    """
    #TODO: change data format to a pandas table

    def __init__(self):

        self.df = DataFrame()
        self.vendormap = VendorMap()
        self.wanted = dict()
        self.bricklink_initialized = False
        self.vendor_initialized = False
        #self.averageprices = dict()
        logger.debug("BrickPile vendormap id: %s" % id(self.vendormap))
        self.webreader = ElementWebReader(self.vendormap)

    @property
    def vendormap(self):
        return self._vendormap

    @vendormap.setter
    def vendormap(self, vendormap_):
        self._vendormap = vendormap_

    def __str__(self):
        assert self.bricklink_initialized, "bricklink not initialized, cannot convert to string"
        return self.xmlvendordata()

    def add_pricelist(self, elementid, pricelist):
        # pricelist : array of PriceTuple's
        # There could be multiple price/qty entries per vendor, but these need to be pruned
        # to a single Pricetuple per vendor
        logging.debug("Adding pricelist to df")
        if pricelist:
            # remove duplicate vendor columns from pricelist
            _df = dataframe_from_pricelist(elementid, pricelist)
            # print(_df)
            self.merge_frame(_df)
        else:
            raise ValueError("No Price Information found for %s" % elementid)
        return

    def merge_frame(self, df_):
        if not self.df.empty:
            #logger.debug("self.df, id(self.df)", self.df, id(self.df))
            #logger.debug("df_", pprint.pformat(df_.__repr__()))
            try:
                self.df = pd.concat([df_, self.df])
            except AssertionError:
                logger.info("Assertion error in concat")
        else:
            self.df = df_.copy()
        return

    def readpricesfromweb(self, wanted):
        """Build a dictionary of price info from the Bricklink website
            Attributes:
                wanted(WantedDict): wanted[elementid] = LegoElement
        """
        self.wanted = wanted
        numitems = len(wanted)
        logging.info("Loading " + str(numitems) + " items from the web")
        #self.data = dict() # a dictionary with keys itemid, and color.  each entry contains a list of lists
        for elementid in list(wanted.keys()):
            # added wanted item to dataframe
            logging.info("Loading element " + str(elementid))
            itemid = wanted[elementid].itemid
            itemtypeid = wanted[elementid].itemtypeid
            itemcolorid = wanted[elementid].colorid
            _elementid, pricelist = self.webreader.web_price_list(itemtypeid, itemid, itemcolorid)
            self.add_pricelist(_elementid, pricelist)

        self.bricklink_initialized = True

    # def read(self, filename=None):
    #     """Read vendor price information from a file."""
    #
    #     assert filename is not None, "price List filename required"
    #     logging.info("Building bricklink data from file: " + filename)
    #     self.data = dict()  # clear any existing data
    #
    #     tree = etree.parse(filename)
    #
    #     wantedlist = tree.findall('Item')
    #     for item in wantedlist:
    #         #print(item.text)
    #
    #         itemid = item.find('ItemID').text
    #         colorid = item.find('ColorID').text
    #         elementid = LegoElement.joinElement(itemid, colorid)
    #         self[elementid] = []  #empty list
    #         logging.info("Loading element " + str(elementid))
    #
    #         vendors = item.findall('Vendor')
    #         for vendor in vendors:
    #             vendorid = vendor.find('VendorID').text
    #             vendorqty = vendor.find('VendorQty').text
    #             vendorprice = vendor.find('VendorPrice').text
    #             #listitem = [vendorid, vendorqty, vendorprice]
    #             assert isinstance(elementid, object)
    #             self[elementid].append([vendorid, vendorqty, vendorprice])
    #             vendorname = vendor.find('VendorName').text
    #             self.vendormap.addVendor(Vendor(vendorid=vendorid, vendorname=vendorname))

    def summarize(self):
        """Return a summary string of the bricklink data."""
        assert self.bricklink_initialized == True, "bricklink not initialized, cannot report dataquality"

        print("Price list includes:")
        print(str(len(list(self.keys()))) + " Total Items")
        print(str(len(list(self.vendormap.keys()))) + " Total Vendors")

    def xmlvendordata(self):
        """Return an XML string of the bricklink vendor price & qty data."""
        assert self.bricklink_initialized == True, "bricklink not initialized, cannot convert to XML"
        #[itemID, storeID, quantity, price]
        xml_string = '<xml>\n'
        for elementid in list(self.keys()):
            itemid, color = LegoElement.splitElement(elementid)

            xml_string += '<Item>\n'
            xml_string += ' <ItemID>{}</ItemID>\n'.format(itemid)
            xml_string += ' <ColorID>{}</ColorID>\n'.format(color)
            for stockentry in self.data[elementid]:
                vendorid = stockentry[0]
                vendor = self.vendormap[vendorid]
                xml_string += '  <Vendor>\n'
                xml_string += '   <VendorID>{}</VendorID>\n'.format(stockentry[0])
                xml_string += '   <VendorName>{}</VendorName>\n'.format(vendor.name)
                xml_string += '   <VendorQty>{}</VendorQty>\n'.format(stockentry[1])
                xml_string += '   <VendorPrice>{}</VendorPrice>\n'.format(stockentry[2])
                xml_string += '  </Vendor>\n'

            xml_string += '</Item>\n'
        xml_string += '</xml>'
        return xml_string


if __name__ == '__main__':
    logger = log.setup_custom_logger(__name__)
    pass
