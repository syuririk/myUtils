from .endpoints.searchCategory import searchCategory
from .endpoints.searchTags import searchTags
from .endpoints.setApiKey import setApiKey
from .endpoints.searchSeries import searchSeries
from .endpoints.getData import getData


from .services.category import category

__all__ = [
    'searchCategory', 'setApiKey', 'searchTags', 'searchSeries', 'getData'
]