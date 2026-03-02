from .base import *

def keyStatisticList(count=200):
    api_key = API.get_api_key()

    base_url = "https://ecos.bok.or.kr/api/KeyStatisticList"
    url = f"{base_url}/{api_key}/json/kr/1/{count}"
    
    response = getRequest(url)
    
    data = response.get('KeyStatisticList', {}).get('row', [])
    
    return data