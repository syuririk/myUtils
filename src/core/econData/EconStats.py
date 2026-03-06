
from __future__ import annotations

import pandas as pd

# scipy may not be installed in minimal environments used for testing; fall back gracefully
try:
    from scipy import stats
except ImportError:  # pragma: no cover
    stats = None


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

    def summary(self, col: str = None) -> pd.DataFrame | dict:
        """요약 통계.

        * DataFrame으로 초기화된 경우 `col`을 지정하지 않으면
          `DataFrame.describe().T` 결과에 왜도/첨도를 덧붙인
          ``pd.DataFrame``을 반환합니다.
        * Series 또는 단일 열에 대한 통계는 기존 사전 형태로 계속 반환됩니다.
        """
        # DataFrame 전체 요약 (col 미지정) ------------------------------------------------
        if self._df is not None and col is None:
            base = self._df.describe().T
            base["skewness"] = self._df.skew()
            base["kurtosis"] = self._df.kurt()
            return base

        # Series 또는 단일 열 요약 ------------------------------------------------------
        if self._series is not None:
            data_to_summarize = self._series
            col_name = col or data_to_summarize.name or "value"
        else:
            if col is None:
                raise ValueError("col parameter required when EconStats initialized with DataFrame")
            data_to_summarize = self._df[col]
            col_name = col

        skew_val = (
            float(stats.skew(data_to_summarize.dropna()))
            if stats is not None else float(data_to_summarize.skew())
        )
        kurt_val = (
            float(stats.kurtosis(data_to_summarize.dropna()))
            if stats is not None else float(data_to_summarize.kurt())
        )

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
            "skewness":          skew_val,
            "kurtosis":          kurt_val,
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