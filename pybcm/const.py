BASE_URL = 'https://api.bricklink.com/api/store/v1/'
ITEM_TYPES = ('MINIFIG', 'PART', 'SET', 'BOOK', 'GEAR', 'CATALOG', 'INSTRUCTION', 'UNSORTED_LOT', 'ORIGINAL_BOX')
GUIDE_TYPES = ('sold', 'stock')
REGIONS = ('asia', 'africa', 'north_america', 'south_america', 'middle_east', 'europe', 'eu', 'oceania')
VATS = ('N', 'Y', 'O')


API_PATH = {

                "base":             'https://api.bricklink.com/api/store/v1',
                "item":             '/items/{type}/{no}',
                "item_image":       '/items/{type}/{no}/images/{color_id}',
                "supersets":        '/items/{type}/{no}/supersets',
                "subsets":          '/items/{type}/{no}/subsets',
                "priceguide":       '/items/{type}/{no}/price',
                "known_colors":     '/items/{type}/{no}/colors'

}