from .base import *

def tagsSeries(self, tag):
url = f"https://api.stlouisfed.org/fred/tags/series?tag_names={tag}&api_key={API.get_api_key()}&file_type=json&order_by=popularity&sort_order=desc"
data = getRequest(url)
return data.get('seriess')