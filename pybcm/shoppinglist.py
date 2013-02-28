'''
Created on Oct 26, 2012

@author: khooks
'''


class ShoppingList(object):
    '''
    shoppinglist = [ { itemid, color, vendorid, price, qty }, ...]
    
    '''      
    def __init__(self):
        '''
        Constructor
        '''
        self.data = list()
        
    def additem(self, itemid, colorid, wantedqty, vendorid, vendorname, vendorqty, vendorprice):
        cost = float(wantedqty) * float(vendorprice)    
        self.data.append( (itemid, colorid, wantedqty, vendorid, vendorname, vendorqty, vendorprice, cost) )
        
    def toXML(self):
        
        xml_string = ''
        for row in self.data:
            xml_string += '<Item>\n'
            xml_string += ' <Itemid>{}</ItemID>\n'.format(row[0])
            xml_string += ' <ColorID>{}</ColorID>\n'.format(row[1])
            xml_string += ' <WantedQty>{}</WantedQty>\n'.format(row[2])
            xml_string += ' <VendorID>{}</VendorID>\n'.format(row[3]) 
            xml_string += ' <VendorName>{}</VendorName>\n'.format(row[4])             
            xml_string += ' <VendorQty>{}</VendorQty>\n'.format(row[5])
            xml_string += ' <VendorPrice>{}</VendorPrice>\n'.format(row[6])
            xml_string += ' <Cost>{}</Cost>\n'.format(row[7])             
            xml_string += '</Item>\n'
        return xml_string
            
    def display(self):
        print self.toXML()      
            
if __name__ == '__main__':
    
    testlist = ShoppingList()
    testlist.additem(4323, 88, 167895, "House of Lolgos", 15, 0.15)
    testlist.display()             