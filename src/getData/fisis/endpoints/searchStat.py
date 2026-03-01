from getData.fisis.services.accountListSearch import accountListSearch

import pandas as pd

def searchStat(listNo: str):
    return accountListSearch(listNo=listNo)