import pandas as pd

def c_statInfo_to_df(df):
    result = df.pivot(index=['base_month', 'finance_cd'], columns='account_nm', values='a')
    result.columns.name = None
    result = result.reset_index().rename(columns={'base_month': 'date'})
    return result
