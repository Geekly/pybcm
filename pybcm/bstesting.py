'''
Created on Feb 6, 2013

@author: khooks
'''
from bs4 import BeautifulSoup as Soup

from bricklinkdata import *
from wanted import *
import re
import io
import unicodedata
#import bricklinkdata as bld
#from bricklinkdata import *



wantedlistfilename = '../Molding Machine.bsx'

#blr = BricklinkReader()
pricefilename = '../bricklink.xml'


wanteddict = WantedDict()
bricklink = BricklinkData()
    
 
print "Reading wanted list", wantedlistfilename

wanteddict.read(wantedlistfilename)
               
print "Loading Prices"


f = open(pricefilename, 'r')
bricklink.read(pricefilename)
f.close()

