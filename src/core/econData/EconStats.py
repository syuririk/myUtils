
from __future__ import annotations

import pandas as pd
import numpy as np
from typing import Optional
from scipy import stats


class EconStats:

    def __init__(self, series: pd.Series):
        self._series = series

    def summary(self, col: str) -> dict:
        return {
            "name":              col,
            "start":             self._series.index.min(),
            "end":               self._series.index.max(),
            "n":                 len(self._series),
            "mean":              self._series.mean(),
            "std":               self._series.std(),
            "min":               self._series.min(),
            "max":               self._series.max(),
            "latest":            self._series.iloc[-1],
            "skewness":          float(stats.skew(self._series.dropna())),
            "kurtosis":          float(stats.kurtosis(self._series.dropna())),
            "quantile":          self.quantile(),
            "stationarity_test": self.stationarity_test(),
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


    def stationarity_test(self) -> dict:
        adf_result = stats.adfuller(self._series.dropna(), autolag='AIC')
        
        return {
            'adf_statistic': float(adf_result[0]),
            'p_value': float(adf_result[1]),
            'critical_values': {
                '1%': float(adf_result[4]['1%']),
                '5%': float(adf_result[4]['5%']),
                '10%': float(adf_result[4]['10%']),
            },
            'is_stationary': bool(adf_result[1] < 0.05),
        }