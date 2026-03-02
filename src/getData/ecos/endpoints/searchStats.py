from ..services.statisticTableList import statisticTableList
from ..services.statisticItemList import statisticItemList

import pandas as pd

def searchStats(keyword, sub_col: str = None, col_val: str = None):
    data = statisticTableList()

    candidate_dict = {}
    for row in data:
        if keyword in row.get('STAT_NAME'):
            candidate_dict[row['STAT_NAME']] = row
    
    result = {}
    for name, val in candidate_dict.items():
        result[name] = val
        try:
            code = val.get('STAT_CODE')
            detail = statisticItemList(val['STAT_CODE'])
            for line in detail:
                if sub_col:
                    if line[sub_col] == col_val:
                        result[f"{name} - {line['ITEM_NAME']}"] = line
                else:
                    result[f"{name} - {line['ITEM_NAME']}"] = line
        except:
            pass

    return pd.DataFrame(result).T
