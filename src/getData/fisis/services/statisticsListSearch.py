from .base import *
import pandas as pd

def statisticsListSearch(lrgDiv: str, smlDiv:str):
    api_key = API.get_api_key()
    
    url = f'http://fisis.fss.or.kr/openapi/statisticsListSearch.json?auth={api_key}&lrgDiv={lrgDiv}&smlDiv={smlDiv}&lang=kr'
    data = getRequest(url).get('result').get('list')
    df = pd.DataFrame(data)
    return df