from .services import *
from .process import *

def searchCompany(keyword, type_val:str):
    return companySearch(keyword)

def searchStats(lrgDiv: str, smlDiv:str):
  datas = statisticsListSearch(lrgDiv=lrgDiv, smlDiv=smlDiv)
  stat_code_list = list(datas['list_no'])
  stat_name_list = list(datas['list_nm'])
  dfs = []
  for i in range(len(stat_code_list)):
    dfs.append(accountListSearch(listNo=stat_code_list[i]))
  result = pd.concat(dfs)
  return result[['list_no', 'account_cd', 'list_nm', 'account_nm']]