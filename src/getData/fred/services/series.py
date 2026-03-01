from .base import *

def series(id, start_date, end_date):
    url = f"https://api.stlouisfed.org/fred/series?series_id={id}&api_key={API.get_api_key()}&file_type=json&realtime_start={start_date}&realtime_end={end_date}"
    data = getRequest(url).get('seriess')
    return data