
from __future__ import annotations

import pandas as pd
import numpy as np
from typing import Optional
from scipy import stats


class EconStats:

    def __init__(self, df: pd.DataFrame):
        self._df = df

    # ------------------------------------------------------------------
    # 통계 함수
    # ------------------------------------------------------------------

    def summary(self, col: str) -> dict:
        return {
            "name":              col,
            "start":             self._df.index.min(),
            "end":               self._df.index.max(),
            "n":                 len(self._df[col]),
            "mean":              self._df[col].mean(),
            "std":               self._df[col].std(),
            "min":               self._df[col].min(),
            "max":               self._df[col].max(),
            "latest":            self._df[col].iloc[-1],
            "skewness":          float(stats.skew(self._df[col].dropna())),
            "kurtosis":          float(stats.kurtosis(self._df[col].dropna())),
            "quantile":          self.quantile(col),
            # "stationarity_test": self.stationarity_test(),
        }

    # ------------------------------------------------------------------
    # 분포 특성 분석
    # ------------------------------------------------------------------

    def quantile(self, q: list[float] | float = None) -> dict | float:
        if q is None:
            q = [0.25, 0.5, 0.75]
        result = self._series.quantile(q)
        if isinstance(q, list):
            return result.to_dict()
        else:
            return float(result)


    # def stationarity_test(self) -> dict:
    #     adf_result = stats.adfuller(self._series.dropna(), autolag='AIC')
        
    #     return {
    #         'adf_statistic': float(adf_result[0]),
    #         'p_value': float(adf_result[1]),
    #         'critical_values': {
    #             '1%': float(adf_result[4]['1%']),
    #             '5%': float(adf_result[4]['5%']),
    #             '10%': float(adf_result[4]['10%']),
    #         },
    #         'is_stationary': bool(adf_result[1] < 0.05),
    #     }