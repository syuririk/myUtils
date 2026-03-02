from getData.fred.services.seriesObservations import seriesObservations

import pandas as pd

def getData(codes, start_date, end_date):
    dfs = []
    for code in codes:
        data = seriesObservations(code, start_date, end_date)
        df = pd.DataFrame(data)

        df = df[['date', 'value']].rename(columns={'value':code})
        df = df.set_index("date")

        dfs.append(df)

    result = pd.concat(dfs, axis=1)
    result.reset_index(inplace=True)

    return result