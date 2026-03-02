

def getData(codes: list, start_date, end_date):
    for code in codes:
        code += [None]*(5-len(code))
        statisticSearch(statCode= code[0], 
                        cycle: str, 
                        start: str, 
                        end: str, 
                        item1 = code[1] or "?", 
                        item2 = code[2] or "?", 
                        item3 = code[3] or "?", 
                        item4 = code[4] or "?")


def processECOSData(self, data=dict):

    first = rows[0]
    stat_name = re.sub(r'^[\d\.]+\s*', '', first["STAT_NAME"])
    data_detail = first

    df = pd.DataFrame(rows)
    df["TIME"] = df["TIME"].map(self.parseTime)
    df["DATA_VALUE"] = pd.to_numeric(df["DATA_VALUE"], errors="coerce")

    for col in ["ITEM_NAME4","ITEM_NAME3","ITEM_NAME2","ITEM_NAME1"]:
        if col in df.columns and df[col].notna().any():
            name_col = col
            break
    else:
        df = df[["TIME","DATA_VALUE"]].set_index("TIME")
        df.columns = [stat_name]
        return df, data_detail

    df["col"] = df[name_col].astype(str).str.strip()

    df = df.pivot_table(
        index="TIME",
        columns="col",
        values="DATA_VALUE",
        aggfunc="first"
    ).sort_index()

    df.columns = [stat_name if c == "" else f"{stat_name}_{c}" for c in df.columns]

    return df, data_detail

def getECOSData(self, codes, method="value", start_date="20230101", end_date="20260101", return_detail=False):

    period_map = {
        "A": lambda d: d[:4],
        "Q": lambda d: d[:4] + "Q1",
        "M": lambda d: d[:6],
        "D": lambda d: d,
        "S": lambda d: d[:4] + "S1",
        "SM": lambda d: d[:6] + "S1"
    }

    dfs = []
    details = {}

    for code in codes:
        per, code_data = code

        if per not in period_map:
            raise ValueError(f"period is not valid: {per}")

        start_var = period_map[per](start_date)
        end_var = period_map[per](end_date)

        try:
            data = self.generateECOSData(code=code_data, period=per, start_date=start_var, end_date=end_var)
            processed_data, detail = self.processECOSData(data)
            dfs.append(processed_data)
            details[code_data[0]] = detail
        except:
            print(f"fail to download {code_data} - {per} - {start_var} - {end_var}")

    df = pd.concat(dfs, axis=1).reset_index().rename(columns={"TIME":"date"})

    return (df, details) if return_detail else df

