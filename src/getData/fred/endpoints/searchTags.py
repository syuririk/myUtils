from getData.fred.services.tags import tags

def searchTags(keyword = None, col='name'):
    datas = tags()
    if keyword is None:
        return pd.DataFrame(data)
    else:
        result = []
        for single_dict in data:
            if keyword in single_dict.get(col):
                result.append(single_dict)
        return pd.DataFrame(result)
        