"""
Add caching to certain functions to reduce the number of http requests an pandas operations

Types of functions to cache:
_get prices
_get set inventory
do this for most functions that return a dataframe

"""
from datetime import timedelta

import pandas as pd

expire = timedelta(days=15)

def memoize_pg(function):

    store_file = '/Users/Keith/Projects/pybcm_proj/resources/cache.hd5'

    def wrapper(itemid, colorid, new_or_used, guide_type, *args, **kwargs):

        key = '_' + '_'.join([itemid, colorid, new_or_used, guide_type])
        with pd.HDFStore(store_file) as store:
            if key in store:
            # if key in hd5 and it's not too old
                df = store.get(key)
                return df
            # return hd5 df
            else:
            # call the function and cache
                df = function(itemid, colorid, new_or_used, guide_type, *args, **kwargs)
                store.put(key, df)
                return df

    return wrapper


