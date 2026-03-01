from .base import *

def seriesObservations():
    url = f"https://api.stlouisfed.org/fred/series/observations?api_key={API.get_api_key()}&file_type=json&series_id={series_id}&observation_start={start_date}&observation_end={end_date}"
    data = getRequest(url).get('tags')
    return data