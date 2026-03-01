from getData.fisis.services.accountListSearch import accountListSearch

import pandas as pd

def searchStat(listNo: str):
    data = accountListSearch(listNo=listNo)
    result = pd.DataFrame(data)
    return result