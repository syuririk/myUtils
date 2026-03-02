from .base import *

def seriesObservations(series_id, start_date, end_date):
    api_key = API.get_api_key()

    base_url = "https://api.stlouisfed.org/fred/series/observations" 
    url = f"{base_url}?api_key={api_key}&file_type=json&series_id={series_id}&observation_start={start_date}&observation_end={end_date}"
    data = getRequest(url).get('observations')
    return data