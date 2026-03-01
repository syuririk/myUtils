from .base import *

def children(category_id, start_date=None, end_date=None):
    url = f"https://api.stlouisfed.org/fred/category/children?category_id={category_id}&api_key={API.get_api_key()}&file_type=json"

    if not start_date == end_date == None:
        url += f"&realtime_start={start_date}&realtime_end={end_date}"

    data = getRequest(url, params=params).get('categories')
    return data
