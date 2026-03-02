from .base import *

def children(category_id, start_date=None, end_date=None):
    api_key = API.get_api_key()

    base_url = "https://api.stlouisfed.org/fred/category/children"
    url = f"{base_url}?category_id={category_id}&api_key={api_key}&file_type=json"

    if not start_date == end_date == None:
        url += f"&realtime_start={start_date}&realtime_end={end_date}"

    data = getRequest(url).get('categories')
    return data
