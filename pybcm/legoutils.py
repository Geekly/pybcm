'''
Created on Oct 23, 2012

@author: khooks
'''
class LegoColor:
    anycolorID = [11, 1, 9, 10, 86, 85, 7, 5, 3, 6, 2, 8, 88]
    
    colors =  { 1: 'White',
                49: 'Very Light Gray',
                99: 'Very Light Bluish Gray',
                86: 'Light Bluish Gray',
                9: 'Light Gray',
                10: 'Dark Gray',
                85: 'Dark Bluish Gray',
                11: 'Black',
                59: 'Dark Red',
                5: 'Red',
                27: 'Rust',
                25: 'Salmon',
                26: 'Light Salmon',
                58: 'Sand Red',
                88: 'Reddish Brown',
                8: 'Brown',
                120: 'Dark Brown',
                69: 'Dark Tan' }



class LegoElement(object):
    
    @staticmethod
    def joinelement(itemid, colorid):
        return str( str(itemid) + "|" + str(colorid) )
    @staticmethod
    def splitelement(elementid):
        return elementid.split("|")
    
    def __init__(self, itemid=None, colorid=None, itemname=None, itemtypeid=None, itemtypename=None, colorname=None, wantedqty=0):
        self.itemid = str(itemid)
        self.colorid = str(colorid)
        self.itemname = str(itemname)
        self.itemtypeid = str(itemtypeid)
        self.itemtypename = str(itemtypename) 
        self.colorname = str(colorname)
        self.wantedqty = int(wantedqty)

        self.id = LegoElement.joinelement(itemid, colorid)
               
    def __str__(self):
        return self.id
              
        
if __name__ == "__main__":
    itemid = '35146'
    colorid = '88'
    wantedqty = '123'
    element = LegoElement.joinelement(itemid, colorid)
    print (element)
    print (LegoElement.splitelement(element))
    
    element = LegoElement(itemid, colorid, wantedqty)
    print (element.id)
    
    print (element.itemid)
    print (element.colorid)
    print (element.wantedqty)