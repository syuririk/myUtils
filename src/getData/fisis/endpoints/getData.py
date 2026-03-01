from getData.fisis.services.statisticsInfoSearch import statisticsInfoSearch
from getData.fisis.utils.convertData import c_statInfo_to_df

import pandas as pd

def getData(codes, start_date, end_date):
  dfs = []
  for code in codes:
    financeCd = code[0] 
    listNo = code[1] 
    accountCd = code[2] 
    term = code[3] 
    data = statisticsInfoSearch(financeCd= financeCd, 
                                listNo= listNo, 
                                accountCd= accountCd, 
                                term= term, 
                                startBaseMm= start_date, 
                                endBaseMm= end_date)
    data = c_statInfo_to_df(data)
    dfs.append(data)

  pd.concat(dfs, axis=1)