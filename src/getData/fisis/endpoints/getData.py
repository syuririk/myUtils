from .services.statisticsInfoSearch import statisticsInfoSearch

import pandas as pd

def getData(codes, start_date, end_date):
  dfs = []
  for code in codes:
    code[0] = financeCd
    code[1] = listNo
    code[2] = accountCd
    code[3] = term
    data = statisticsInfoSearch(financeCd= financeCd, 
                              listNo= listNo, 
                              accountCd= accountCd, 
                              term= term, 
                              startBaseMm= start_date, 
                              endBaseMm= end_date)
    dfs.appned(data)
  pd.concat(dfs, axis=1)