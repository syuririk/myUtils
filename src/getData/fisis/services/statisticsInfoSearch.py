from .base import *

def statisticsInfoSearch(financeCd: str, listNo: str, accountCd: str, term: str, startBaseMm:str, endBaseMm: str):
    api_key = API.get_api_key()
    
    url = f'http://fisis.fss.or.kr/openapi/statisticsInfoSearch.json?auth={api_key}&financeCd={financeCd}&listNo={listNo}&accountCd={accountCd}&term={term}&startBaseMm={startBaseMm}&endBaseMm={endBaseMm}&lang=kr'
    data = getRequest(url).get('result').get('list')
    return data