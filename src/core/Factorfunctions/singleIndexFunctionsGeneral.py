import numpy as np
import pandas as pd


def safe_div(numer: pd.Series, denom: pd.Series) -> pd.Series:
  result = numer / denom.replace(0, np.nan)
  return result.replace([np.inf, -np.inf], np.nan)

def ratioFactor(numer, denom):
    def factor(df):
        if isinstance(numer, (int, float)):
            return safe_div(numer, df[denom])
        return safe_div(df[numer], df[denom])
    return factor

def returnFactor(col, period, subtract=None, date_col=None):
    def factor(df):
        g = df[col]
        base = g.pct_change(period)
        if subtract:
            base -= g.pct_change(subtract)
        return base.replace([np.inf, -np.inf], np.nan)
    return factor

def rollingStatFactor(col, window, stat="mean"):
    def factor(df):
        g = df[col]

        if stat == "mean":
            out = g.rolling(window).mean()
        elif stat == "std":
            out = g.rolling(window).std()
        else:
            raise ValueError("stat must be 'mean' or 'std'")

        return out.reset_index(level=0, drop=True)

    return factor

def logFactor(col):
    def factor(df):
        return np.log(df[col])
    return factor

def maCrossFactor(col, short=5, long=60, method="ratio"):
    def factor(df):
        g = df[col]
        short_ma = g.rolling(short).mean()
        long_ma = g.rolling(long).mean()

        if method == "ratio":
            return safe_div(short_ma, long_ma)
        elif method == "diff":
            return short_ma - long_ma
        elif method == "signal":
            return (short_ma > long_ma).astype("float32")
        else:
            raise ValueError("method must be ratio | diff | signal")
    return factor

def compareFactor(left, right, op="gt"):
    def factor(df):
        l = df[left] if isinstance(left, str) else left
        r = df[right] if isinstance(right, str) else right

        if op == "gt":
            out = l > r
        elif op == "ge":
            out = l >= r
        elif op == "eq":
            out = l == r
        elif op == "ne":
            out = l != r
        else:
            raise ValueError("op must be gt | ge | eq | ne")
        return out.astype(int)
    return factor

def rollingZscoreFactor(col, window, eps=1e-8):
    def factor(df):
        g = df[col]
        mean = g.rolling(window).mean()
        std = g.rolling(window).std()
        return ((df[col] - mean) / (std + eps)).astype("float32")
    return factor

