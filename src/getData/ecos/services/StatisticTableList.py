from .base import *

def statisticTableList(statCode: str = None, count=100000):

    api_key = API.get_api_key()
    
    base_url = "https://ecos.bok.or.kr/api/StatisticTableList"

    if statCode:
        url = f"{base_url}/{api_key}/json/kr/1/{count}/{statCode}"
    else:
        url = f"{base_url}/{api_key}/json/kr/1/{count}"
    
    response = getRequest(url)
    data = response.get('StatisticTableList', {}).get('row', [])
    
    return data