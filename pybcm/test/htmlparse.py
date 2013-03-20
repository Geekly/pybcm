
import re
    
if __name__ == "__main__":

    pricestring = "US $0.05"
    result = re.match('US', pricestring)
    print( result )
    result = re.match('US', pricestring)
    print( result )
    