from getData.fred.services.categorySeries import categorySeries
from getData.fred.services.tagsSeries import tagsSeries
import pandas as pd

def searchSeries(val_id :str, method='category'):
    if method == 'category':
        data = categorySeries(val_id)
        return pd.DataFrame(data)

    elif: method == 'tag'
        data = tagsSeries(val_id)
        return pd.DataFrame(data)

    else:
        raise ValueError(f"Can't find method : {method}\n            method should be category | tag" )
