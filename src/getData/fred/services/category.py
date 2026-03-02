from .base import *
from .children import children

def category(category_id):
    api_key = API.get_api_key()

    base_url = "https://api.stlouisfed.org/fred/category"
    url = f"{base_url}?category_id={category_id}&api_key={api_key}&file_type=json"
    data = getRequest(url).get('categories')
    return data
