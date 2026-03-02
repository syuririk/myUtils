from .endpoints.setApiKey import setApiKey

from .services.keyStatisticList import keyStatisticList
from .services.statisticItemList import statisticItemList
from .services.statisticMeta import statisticMeta
from .services.statisticSearch import statisticSearch
from .services.statisticTableList import statisticTableList
from .services.statisticWord import statisticWord

from getData.fisis.utils.api import API


__all__ = [
    'setApiKey',

    'keyStatisticList', 'statisticItemList', 'statisticMeta', 'statisticSearch', 'statisticTableList', 'statisticWord'
    'API'
]
