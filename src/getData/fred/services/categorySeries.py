from .base import *

def categorySeries(category_id):
    api_key = API.get_api_key()

    base_url = "https://api.stlouisfed.org/fred/category/series"
    url = f"{base_url}?category_id={category_id}&api_key={api_key}&file_type=json&order_by=popularity&sort_order=desc"
    data = getRequest(url).get('seriess')
    return data