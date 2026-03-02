"""
analyzeData/descriptive.py
기술통계 분석기.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from typing import List, Optional, Tuple

from core.dataset import EconDataset


class DescriptiveAnalyzer:
    """
    경제지표 기술통계 분석.

    Examples
    --------
    >>> da = DescriptiveAnalyzer(ds)
    >>> da.summary()                              # 전체 지표 요약 DataFrame
    >>> da.describe()                             # 확장 describe (skewness, kurtosis 포함)
    >>> da.yoy_table()                            # 전년 동기 대비 변화율 테이블
    >>> da.qoq_table()                            # 전분기 대비 변화율 테이블
    >>> da.cumulative_table()                     # 기준 시점 대비 누적 변화율 테이블
    >>> da.correlation()                          # 지표 간 상관계수 행렬
    >>> da.correlation_with_target('총지수')      # 특정 지표와의 상관계수
    >>> da.rank_by_change()                       # 최근 YoY 기준 순위
    >>> da.contribution()                         # 가중치 기반 기여도
    >>> da.period_compare(('2020','2022'), ('2022','2024'))  # 구간 비교
    """

    def __init__(self, dataset: EconDataset):
        self.dataset = dataset
        self._df = dataset.df

    # ------------------------------------------------------------------
    # 요약 통계
    # ------------------------------------------------------------------

    def summary(self) -> pd.DataFrame:
        """각 지표의 기초통계량 + 최신값 + 최신 YoY 변화율."""
        rows = [self.dataset[name].summary() for name in self.dataset.indicators]
        return pd.DataFrame(rows).set_index("name")

    def describe(self) -> pd.DataFrame:
        """pandas describe() + skewness + kurtosis."""
        base = self._df.describe().T
        base["skewness"] = self._df.skew()
        base["kurtosis"] = self._df.kurt()
        return base

    # ------------------------------------------------------------------
    # 변화율 테이블
    # ------------------------------------------------------------------

    def yoy_table(self, periods: int = 4) -> pd.DataFrame:
        """전년 동기 대비 변화율(%) 테이블."""
        return self._df.pct_change(periods=periods) * 100

    def qoq_table(self) -> pd.DataFrame:
        """전분기 대비 변화율(%) 테이블."""
        return self._df.pct_change(periods=1) * 100

    def cumulative_table(self, base_period: Optional[str] = None) -> pd.DataFrame:
        """기준 시점 대비 누적 변화율(%) 테이블."""
        base = self._df.loc[base_period] if base_period else self._df.iloc[0]
        return (self._df / base - 1) * 100

    # ------------------------------------------------------------------
    # 상관관계
    # ------------------------------------------------------------------

    def correlation(self, method: str = "pearson") -> pd.DataFrame:
        """지표 간 상관계수 행렬. method: 'pearson' | 'spearman' | 'kendall'"""
        return self._df.corr(method=method)

    def correlation_with_target(self, target: str, lag: int = 0) -> pd.Series:
        """특정 지표와 나머지 지표 간 상관계수 (lag 적용 가능)."""
        return self._df.shift(lag).corrwith(self._df[target]).drop(target)

    # ------------------------------------------------------------------
    # 순위 / 기여도
    # ------------------------------------------------------------------

    def rank_by_change(self, periods: int = 4, ascending: bool = False) -> pd.DataFrame:
        """최근 YoY 변화율 기준 지표 순위."""
        latest_yoy = self.yoy_table(periods).iloc[-1]
        return latest_yoy.sort_values(ascending=ascending).to_frame("yoy_change_%")

    def contribution(self, weights: Optional[dict] = None) -> pd.DataFrame:
        """
        가중치 기반 지표 기여도.
        weights: {'지표명': 가중치} — 미지정 시 균등 가중치.
        """
        cols = self.dataset.indicators
        w = weights or {c: 1 / len(cols) for c in cols}
        yoy = self.yoy_table()
        return yoy.apply(lambda row: pd.Series({c: row[c] * w.get(c, 0) for c in cols}), axis=1)

    # ------------------------------------------------------------------
    # 구간 비교
    # ------------------------------------------------------------------

    def period_compare(
        self,
        period_a: Tuple[str, str],
        period_b: Tuple[str, str],
        stat: str = "mean",
    ) -> pd.DataFrame:
        """
        두 기간의 통계량 비교.
        stat: 'mean' | 'std' | 'max' | 'min'
        """
        a = getattr(self._df.loc[period_a[0]:period_a[1]], stat)()
        b = getattr(self._df.loc[period_b[0]:period_b[1]], stat)()
        return pd.DataFrame({
            "period_a": a,
            "period_b": b,
            "diff":     b - a,
            "pct_diff": (b / a - 1) * 100,
        })
