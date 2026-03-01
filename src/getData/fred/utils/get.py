
def generateFredData(self, series_id, start_date, end_date):

url = "https://api.stlouisfed.org/fred/series/observations"
params = {
    "api_key" : self.api_key,
    "file_type" : "json",
    "series_id" : series_id,
    'observation_start' : start_date,
    'observation_end' : end_date
}

data = self.request(url, params=params)
data = pd.DataFrame(data.get('observations'))

data = data[['date', 'value']].rename(columns={'value':series_id})
data = data.set_index("date")
return data


def processFredData(self, df):
pass


def getFredData(self, codes=list, release_date=False, start_date='2023-01-01', end_date='2024-01-01'):

dfs = []
for code in codes:

    data = self.generateFredData(code, start_date=start_date, end_date=end_date)
    dfs.append(data)
result = pd.concat(dfs, axis=1)
result.reset_index(inplace=True)
return result
