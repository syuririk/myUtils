from .base import *

def accountListSearch(listNo: str):
    '''

    '''
    api_key = API.get_api_key()
    
    url = f'http://fisis.fss.or.kr/openapi/accountListSearch.json?auth={api_key}&listNo={listNo}&lang=kr'
    data = getRequest(url).get('result').get('list')
    df = pd.DataFrame(data)
    return df