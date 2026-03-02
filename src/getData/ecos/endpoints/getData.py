from getData.ecos.utils.convertData import parseTime

import pandas as pd

period_map = {
    "A": lambda d: d[:4],
    "Q": lambda d: d[:4] + "Q1",
    "M": lambda d: d[:6],
    "D": lambda d: d,
    "S": lambda d: d[:4] + "S1",
    "SM": lambda d: d[:6] + "S1"}

def _getSingleData(code, start_date, end_date)
    cycle = code.pop(0)
    start_var = period_map[cycle](start_date)
    end_var = period_map[cycle](end_date)

    code += [None]*(5-len(code))
    data = statisticSearch( statCode= code[0], 
                            cycle= cycle, 
                            start = start_val, 
                            end: end_val, 
                            item1 = code[1] or "?", 
                            item2 = code[2] or "?", 
                            item3 = code[3] or "?", 
                            item4 = code[4] or "?")
    
    stat_name = re.sub(r'^[\d\.]+\s*', '', data[0]["STAT_NAME"])

    df = pd.DataFrame(data)
    df["TIME"] = df["TIME"].map(parseTime)
    df = df.rename(columns={"TIME":"date"})
    df["DATA_VALUE"] = pd.to_numeric(df["DATA_VALUE"], errors="coerce")

    name_cols = ['ITEM_NAME1', 'ITEM_NAME2', 'ITEM_NAME3', 'ITEM_NAME4']
    df['stat_name'] = df[name_cols].apply(
        lambda row: f'{stat_name}_' + '_'.join([str(val).strip() for val in row if val]), axis=1 )

    pivot_df = df.pivot_table(
        index="TIME", 
        columns="stat_name", 
        values="DATA_VALUE",
        aggfunc="first")

    pivot_df = pivot_df.rename_axis(None, axis=1).sort_index().reset_index()

def getData(codes: list, start_date: str, end_date: str):
    dfs = []
    for code in codes:
        try:
            _getSingleData(code, start_date, end_date)
            dfs.append(pivot_df)
        except:
            print(f"fail to download {code_data} - {per} - {start_var} - {end_var}")

    df = pd.concat(dfs, axis=1).reset_index().rename(columns={"TIME":"date"})
    return df

