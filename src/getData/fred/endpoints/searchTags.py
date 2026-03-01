from getData.fred.services.tags import tags
import pandas as pd

def searchTags(keyword = None, col='name'):
    datas = tags()
    if keyword is None:
        return pd.DataFrame(datas)
    else:
        result = []
        for single_dict in datas:
            if keyword in single_dict.get(col):
                result.append(single_dict)
        return pd.DataFrame(result)
