from .base import *
from .children import children

def category(category_id):
    url = f"https://api.stlouisfed.org/fred/category?category_id={category_id}&api_key={API.get_api_key()}&file_type=json"
    data = getRequest(url)
    return data
