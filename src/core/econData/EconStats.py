
from __future__ import annotations

import pandas as pd
from scipy import stats


class EconStats:

    def __init__(self, data):
        if isinstance(data, pd.Series):
            self._series = data
            self._df = None
        else:
            self._df = data
            self._series = data.iloc[:, 0] if len(data.columns) > 0 else None

    def __repr__(self):
        return str(self.summary())
    # ------------------------------------------------------------------
    # 통계 함수
    # ------------------------------------------------------------------

    def summary(self, col: str = None) -> dict:
        if self._series is not None:
            data_to_summarize = self._series
            col_name = col or data_to_summarize.name or "value"
        else:
            if col is None:
                raise ValueError("col parameter required when EconStats initialized with DataFrame")
            data_to_summarize = self._df[col]
            col_name = col
            
        return {
            "name":              col_name,
            "start":             data_to_summarize.index.min(),
            "end":               data_to_summarize.index.max(),
            "n":                 len(data_to_summarize),
            "mean":              data_to_summarize.mean(),
            "std":               data_to_summarize.std(),
            "min":               data_to_summarize.min(),
            "max":               data_to_summarize.max(),
            "latest":            data_to_summarize.iloc[-1],
            "skewness":          float(stats.skew(data_to_summarize.dropna())),
            "kurtosis":          float(stats.kurtosis(data_to_summarize.dropna())),
            "quantile":          self.quantile(col),
            # "stationarity_test": self.stationarity_test(),
        }

    # ------------------------------------------------------------------
    # 분포 특성 분석
    # ------------------------------------------------------------------

    def quantile(self, q: list[float] | float = None) -> dict | float:
        if q is None:
            q = [0.25, 0.5, 0.75]
        
        # Use series if available, otherwise access the column from dataframe
        if self._series is not None:
            result = self._series.quantile(q)
        else:
            # This shouldn't be called when initialized with DataFrame without col context
            raise ValueError("quantile() requires Series data or col context")
            
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