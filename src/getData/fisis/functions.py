from .services.statisticsListSearch import statisticsListSearch
from .services.accountListSearch import accountListSearch
from .services.statisticsInfoSearch import statisticsInfoSearch
from .services.companySearch import companySearch
from .process.convertData import c_statInfo_to_df
from .utils.api import API

def searchCompany(div, type_val:str):
  '''
  A : 국내은행
  J : 외은지점
  H : 생명보험
  I : 손해보험
  F : 투자매매중개업자Ⅰ
  W : 투자매매중개업자Ⅱ
  G : 집합투자업자
  X : 투자자문일임업자
  D : 종합금융회사
  C : 신용카드사
  K : 리스사
  T : 할부금융사
  N : 신기술금융사
  E : 상호저축은행
  O : 신용협동조합
  Q : 농업협동조합
  P : 수산업협동조합
  S : 산림조합
  M : 부동산신탁
  L : 금융지주회사
  B : 공통(신탁)
  R : 공통(파생상품)
  '''
  return companySearch(div)

def searchStats(lrgDiv: str, smlDiv:str):
  '''
  - A: 국내은행       -> [A:일반현황, B:재무현황, C:주요경영지표, D:주요영업활동, P:보도자료통계]
  - J: 외은지점       -> [A:일반현황, B:재무현황, C:주요경영지표, P:보도자료통계]
  - H: 생명보험       -> [A:일반현황, B:재무현황, C:주요경영지표, D:주요영업활동, P:보도자료통계]
  - I: 손해보험       -> [A:일반현황, B:재무현황, C:주요경영지표, D:주요영업활동, P:보도자료통계]
  - F: 증권사         -> [A:일반현황, B:재무현황, C:주요경영지표, D:주요영업활동, P:보도자료통계]
  - W: 선물사         -> [A:일반현황, B:재무현황, C:주요경영지표, D:주요영업활동, P:보도자료통계]
  - G: 자산운용사     -> [A:일반현황, B:재무현황, C:주요경영지표, D:주요영업활동]
  - X: 투자자문/일임사 -> [A:일반현황, B:재무현황, C:주요경영지표, D:주요영업활동]
  - D: 종합금융회사   -> [A:일반현황, B:재무현황, C:주요경영지표]
  - C: 신용카드사     -> [A:일반현황, B:재무현황, C:주요경영지표, D:주요영업활동, P:보도자료통계]
  - K: 리스사         -> [A:일반현황, B:재무현황, C:주요경영지표, D:주요영업활동, P:보도자료통계]
  - T: 할부금융사     -> [A:일반현황, B:재무현황, C:주요경영지표, D:주요영업활동, P:보도자료통계]
  - N: 신기술금융사   -> [A:일반현황, B:재무현황, C:주요경영지표, D:주요영업활동, P:보도자료통계]
  - E: 상호저축은행   -> [A:일반현황, B:재무현황, C:주요경영지표, P:보도자료통계]
  - O: 신용협동조합   -> [A:일반현황, B:재무현황, C:주요경영지표, P:보도자료통계]
  - Q: 농업협동조합   -> [A:일반현황, B:재무현황, C:주요경영지표, P:보도자료통계]
  - P: 수산업협동조합 -> [A:일반현황, B:재무현황, C:주요경영지표, P:보도자료통계]
  - S: 산림조합       -> [A:일반현황, B:재무현황, C:주요경영지표, P:보도자료통계]
  - M: 부동산신탁     -> [A:일반현황, B:재무현황, E:주요경영지표] ※주의: 경영지표가 E코드임
  - L: 금융지주회사   -> [A:일반현황, B:재무현황, C:주요경영지표, P:보도자료통계]
  - B: 공통(신탁)     -> [A:신탁회사현황, B:은행, C:증권, D:보험, E:부동산신탁, F:신탁보수]
  - R: 공통(파생상품) -> [A:총괄(신탁제외), B:신탁]
  '''
  datas = statisticsListSearch(lrgDiv=lrgDiv, smlDiv=smlDiv)
  stat_code_list = list(datas['list_no'])
  stat_name_list = list(datas['list_nm'])
  dfs = []
  for i in range(len(stat_code_list)):
    dfs.append(accountListSearch(listNo=stat_code_list[i]))
  result = pd.concat(dfs)
  return result[['list_no', 'account_cd', 'list_nm', 'account_nm']]


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

def setApiKey(key: str):
  API.set_api_key(key)
