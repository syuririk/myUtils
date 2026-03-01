from .base import *

def tags():
    url = f"https://api.stlouisfed.org/fred/tags?api_key={API.get_api_key()}&file_type=json"
    data = getRequest(url).get('tags')
    return data
