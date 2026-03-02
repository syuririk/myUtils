from .base import *

def statisticWord(word: str, count=1000):
    api_key = API.get_api_key()

    base_url = "https://ecos.bok.or.kr/api/StatisticWord"
    url = f"{base_url}/{api_key}/json/kr/1/{count}/{word}"
    
    response = getRequest(url)
    
    data = response.get('StatisticWord', {}).get('row', [])
    
    return data