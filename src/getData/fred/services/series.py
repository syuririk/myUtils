from .base import *

def series(series_id, start_date, end_date):
    api_key = API.get_api_key()

    base_url = "https://api.stlouisfed.org/fred/series"
    url = f"{base_url}?series_id={series_id}&api_key={api_key}&file_type=json&realtime_start={start_date}&realtime_end={end_date}"
    data = getRequest(url).get('seriess')
    return data