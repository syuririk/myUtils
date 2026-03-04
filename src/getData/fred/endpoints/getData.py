from ..services.seriesObservations import seriesObservations

import pandas as pd

def getData(codes, start_date, end_date):
    dfs = []
    start_var = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
    end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"
    
    for code in codes:

        data = seriesObservations(code, start_var, end_date)
        df = pd.DataFrame(data)

        df = df[['date', 'value']].rename(columns={'value':code})
        df = df.set_index("date")

        dfs.append(df)

    result = pd.concat(dfs, axis=1)
    result.reset_index(inplace=True)

    return result