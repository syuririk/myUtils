from getData.ecos.services.keyStatisticList import keyStatisticList

import pandas as pd

def getKeyStats():
    data = keyStatisticList()
    return pd.DataFrame(data)