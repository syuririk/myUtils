from .base import *

def statisticMeta(dataName: str, count=100000):
    api_key = API.get_api_key()

    base_url = "https://ecos.bok.or.kr/api/StatisticMeta"
    url = f"{base_url}/{api_key}/json/kr/1/{count}/{dataName}"
    
    response = getRequest(url)
    
    data = response.get('StatisticMeta', {}).get('row', [])
    
    return data
