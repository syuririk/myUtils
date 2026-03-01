from .base import *

def companySearch(partDiv: str):
    api_key = API.get_api_key()

    url = f'http://fisis.fss.or.kr/openapi/companySearch.json?auth={api_key}&partDiv={partDiv}&lang=kr'
    data = getRequest(url).get('result').get('list')
    return data