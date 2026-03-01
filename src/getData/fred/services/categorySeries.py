from .base import *

def categorySeries(category_id=0):
    url = f"https://api.stlouisfed.org/fred/category/series?category_id={category_id}&api_key={API.get_api_key()}&file_type=json&order_by=popularity&sort_order=desc"
    data = getRequest(url).get('seriess')
    return data