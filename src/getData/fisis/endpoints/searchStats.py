from getData.fisis.services.statisticsListSearch import statisticsListSearch
from getData.fisis.services.accountListSearch import accountListSearch
import pandas as pd

def searchStats(lrgDiv: str, smlDiv: str, details = True):
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
  if details:
    datas = statisticsListSearch(lrgDiv=lrgDiv, smlDiv=smlDiv)
    stat_code_list = list(datas['list_no'])
    stat_name_list = list(datas['list_nm'])
    dfs = []
    for i in range(len(stat_code_list)):
      dfs.append(accountListSearch(listNo=stat_code_list[i]))
    result = pd.concat(dfs)[['list_no', 'account_cd', 'list_nm', 'account_nm']]

  else:
    result = statisticsListSearch(lrgDiv=lrgDiv, smlDiv=smlDiv)
  return result