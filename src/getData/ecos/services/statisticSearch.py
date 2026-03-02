from .base import *

def statisticSearch(statCode: str, 
                    cycle: str, 
                    start: str, 
                    end: str, 
                    item1: str = "?", 
                    item2: str = "?", 
                    item3: str = "?", 
                    item4: str = "?", 
                    count=100000):
                    
    api_key = API.get_api_key()

    base_url = "https://ecos.bok.or.kr/api/StatisticSearch"
    url = f"{base_url}/{api_key}/json/kr/1/{count}/{statCode}/{cycle}/{start}/{end}/{item1}/{item2}/{item3}/{item4}"
    
    response = getRequest(url)
    
    data = response.get('StatisticSearch', {}).get('row', [])
    
    return data