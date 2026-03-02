"""
analyzeData/comparative.py
지표 간 비교 분석기.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from typing import List, Optional, Tuple

from core.dataset import EconDataset
from core.transformer import DataTransformer


class ComparativeAnalyzer:
    """
    여러 지표 비교 분석기.

    Examples
    --------
    >>> ca = ComparativeAnalyzer(ds)
    >>> ca.normalized_comparison('minmax')             # 정규화 후 비교 DataFrame
    >>> ca.lead_lag('총지수', '식료품', max_lag=4)    # 리드-래그 상관계수 Series
    >>> ca.relative_performance()                      # 기준 시점 대비 상대 성과(%)
    >>> ca.dispersion()                                # 시점별 지표 간 분산도
    >>> ca.rolling_correlation('총지수', '식료품', 4) # 이동 상관계수
    >>> ca.pairwise_correlation_matrix()               # 전체 / 특정 기간 상관행렬
    """

    def __init__(self, dataset: EconDataset):
        self.dataset = dataset
        self._df = dataset.df

    def normalized_comparison(self, method: str = "minmax") -> pd.DataFrame:
        """정규화된 지표 비교. method: 'minmax' | 'zscore' | 'base'"""
        return DataTransformer.normalize(self._df, method)

    def lead_lag(
        self,
        indicator_a: str,
        indicator_b: str,
        max_lag: int = 4,
    ) -> pd.Series:
        """
        lag별 상관계수.
        양수 lag → a 가 b 를 선행, 음수 → b 가 a 를 선행.
        """
        a, b = self._df[indicator_a], self._df[indicator_b]
        results = {}
        for lag in range(-max_lag, max_lag + 1):
            results[lag] = a.corr(b.shift(-lag)) if lag < 0 else a.shift(lag).corr(b)
        return pd.Series(results, name=f"{indicator_a}_lag_{indicator_b}")

    def relative_performance(self, base_period: Optional[str] = None) -> pd.DataFrame:
        """기준 시점 대비 각 지표의 상대 성과(%)."""
        base = self._df.loc[base_period] if base_period else self._df.iloc[0]
        return (self._df / base - 1) * 100

    def dispersion(self) -> pd.DataFrame:
        """시점별 지표 간 분산도 (std, range, cv)."""
        result = pd.DataFrame(index=self._df.index)
        result["std"]   = self._df.std(axis=1)
        result["range"] = self._df.max(axis=1) - self._df.min(axis=1)
        result["cv"]    = result["std"] / self._df.mean(axis=1) * 100
        return result

    def rolling_correlation(
        self,
        indicator_a: str,
        indicator_b: str,
        window: int = 4,
    ) -> pd.Series:
        """두 지표 간 이동 상관계수."""
        return self._df[indicator_a].rolling(window).corr(self._df[indicator_b])

    def pairwise_correlation_matrix(
        self,
        period: Optional[Tuple[str, str]] = None,
        method: str = "pearson",
    ) -> pd.DataFrame:
        """전체 / 특정 기간의 지표 간 상관행렬."""
        sub = self._df.loc[period[0]:period[1]] if period else self._df
        return sub.corr(method=method)
