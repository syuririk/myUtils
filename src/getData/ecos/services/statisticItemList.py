from .base import *

def statisticItemList(statCode: str, count=100000):
    api_key = API.get_api_key()

    base_url = "https://ecos.bok.or.kr/api/StatisticItemList"
    url = f"{base_url}/{api_key}/json/kr/1/{count}/{statCode}"
    
    response = getRequest(url)
    
    data = response.get('StatisticItemList', {}).get('row', [])
    
    return data