"""
core/indicator.py
단일 경제지표 시리즈 래퍼.
EconDataset['지표명'] 으로 접근한다.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from typing import Optional


class Indicator:
    """
    단일 경제지표 시계열 래퍼.

    Examples
    --------
    >>> ind = ds['총지수']
    >>> ind.yoy()            # 전년 동기 대비 변화율 Series
    >>> ind.qoq()            # 전분기 대비 변화율 Series
    >>> ind.ma(4)            # 4기 이동평균
    >>> ind.summary()        # 기초 통계 dict
    >>> ind.outliers()       # Z-score 기준 이상값
    """

    def __init__(self, name: str, series: pd.Series):
        self.name = name
        self._s = series.copy().sort_index()

    # ------------------------------------------------------------------
    # 프로퍼티
    # ------------------------------------------------------------------

    @property
    def series(self) -> pd.Series:
        return self._s

    @property
    def values(self) -> np.ndarray:
        return self._s.values

    @property
    def index(self) -> pd.DatetimeIndex:
        return self._s.index

    def __repr__(self) -> str:
        return (
            f"Indicator('{self.name}', "
            f"{self._s.index.min().date()}~{self._s.index.max().date()}, "
            f"n={len(self._s)})"
        )

    # ------------------------------------------------------------------
    # 변화율
    # ------------------------------------------------------------------

    def yoy(self, periods: int = 4) -> pd.Series:
        """전년 동기 대비 변화율 (%). 분기 기준 periods=4."""
        return self._s.pct_change(periods=periods) * 100

    def qoq(self) -> pd.Series:
        """전분기 대비 변화율 (%)."""
        return self._s.pct_change(periods=1) * 100

    def cumulative_change(self, base_period: Optional[str] = None) -> pd.Series:
        """기준 시점 대비 누적 변화율. 미지정 시 시작점 기준."""
        base = self._s.loc[base_period] if base_period else self._s.iloc[0]
        return (self._s / base - 1) * 100

    # ------------------------------------------------------------------
    # 이동 통계
    # ------------------------------------------------------------------

    def ma(self, window: int) -> pd.Series:
        """단순 이동평균."""
        return self._s.rolling(window).mean()

    def ema(self, span: int) -> pd.Series:
        """지수 이동평균."""
        return self._s.ewm(span=span, adjust=False).mean()

    def rolling_std(self, window: int) -> pd.Series:
        """이동 표준편차 (변동성)."""
        return self._s.rolling(window).std()

    # ------------------------------------------------------------------
    # 기술 통계
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        return {
            "name":       self.name,
            "start":      self._s.index.min(),
            "end":        self._s.index.max(),
            "n":          len(self._s),
            "mean":       self._s.mean(),
            "std":        self._s.std(),
            "min":        self._s.min(),
            "max":        self._s.max(),
            "latest":     self._s.iloc[-1],
            "yoy_latest": self.yoy().iloc[-1],
        }

    # ------------------------------------------------------------------
    # 이상값
    # ------------------------------------------------------------------

    def outliers(self, threshold: float = 2.0) -> pd.Series:
        """Z-score 기준 이상값 반환."""
        z = (self._s - self._s.mean()) / self._s.std()
        return self._s[z.abs() > threshold]
