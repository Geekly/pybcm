"""
Created on Apr 12, 2013

@author: khooks

Similar to BCMData, but simplifies and consolidates the data

"""

class ResultSet(object):
    
    def __init__(self):
        
        self.vendorlist = list()
        self.elementlist = list()
        self.result = None  #this is an ndarray with indexes that map to elementlist and vendorlist
        
        return
    
