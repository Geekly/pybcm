"""
Created on Jun 6, 2013

@author: khooks
"""

from ConfigParser import SafeConfigParser


class BCMConfig():

    def __init__(self):
        parser = SafeConfigParser()
        parser.read('../bcm.ini')
        self.wantedfilename = parser.get('filenames', 'wanted')
        self.pricefilename = parser.get('filenames', 'prices')
        self.reloadpricesfromweb = parser.get('options', 'reloadpricesfromweb')

if __name__ == '__main__':

    config = BCMConfig()
    open(config.wantedfilename, 'r')

    wanted = '../Sampledata/Star Destroyer 30056-1.bsx'
    open(wanted, 'r')