"""
analyzeData/timeseries.py
시계열 분석기 — 추세 분해, 계절성, 이상값 탐지, 변곡점, 변동성.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List

from core.econData.EconDataset import EconDataset


@dataclass
class DecompositionResult:
    """seasonal_decompose 결과 컨테이너."""
    indicator:         str
    observed:          pd.Series
    trend:             pd.Series
    seasonal:          pd.Series
    residual:          pd.Series
    strength_trend:    float = field(init=False)
    strength_seasonal: float = field(init=False)

    def __post_init__(self):
        var_r = self.residual.var()
        self.strength_trend    = max(0, 1 - var_r / (self.trend    + self.residual).var())
        self.strength_seasonal = max(0, 1 - var_r / (self.seasonal + self.residual).var())


class TimeSeriesAnalyzer:
    """
    시계열 분석기.

    Examples
    --------
    >>> tsa = TimeSeriesAnalyzer(ds)
    >>> result = tsa.decompose('총지수')          # DecompositionResult
    >>> tsa.decompose_all()                       # 전체 지표 일괄 분해
    >>> tsa.detect_outliers('총지수')             # 이상값 Series
    >>> tsa.changepoints('총지수')                # 변곡점 DatetimeIndex
    >>> tsa.seasonal_pattern('총지수')            # 분기별 평균·표준편차
    >>> tsa.seasonal_adjustment('총지수')         # 계절 조정 시계열
    >>> tsa.rolling_volatility('총지수', 4)       # 이동 변동성
    >>> tsa.volatility_table(4)                   # 전체 지표 이동 변동성 테이블
    """

    def __init__(self, dataset: EconDataset):
        self.dataset = dataset
        self._df = dataset.df

    # ------------------------------------------------------------------
    # 추세 분해
    # ------------------------------------------------------------------

    def decompose(
        self,
        indicator: str,
        model: str = "additive",
        period: Optional[int] = None,
    ) -> DecompositionResult:
        """
        Classical 시계열 분해.
        model: 'additive' | 'multiplicative'
        period: 계절 주기 (분기=4, 월=12). 미지정 시 자동 추론.
        """
        try:
            from statsmodels.tsa.seasonal import seasonal_decompose
        except ImportError:
            raise ImportError("pip install statsmodels 를 먼저 실행하세요.")

        s = self._df[indicator].dropna()
        p = period or self._infer_period()
        r = seasonal_decompose(s, model=model, period=p, extrapolate_trend="freq")
        return DecompositionResult(
            indicator=indicator,
            observed=r.observed,
            trend=r.trend,
            seasonal=r.seasonal,
            residual=r.resid,
        )

    def decompose_all(self, **kwargs) -> dict[str, DecompositionResult]:
        """전체 지표 일괄 분해."""
        return {name: self.decompose(name, **kwargs) for name in self.dataset.indicators}

    # ------------------------------------------------------------------
    # 이상값 탐지
    # ------------------------------------------------------------------

    def detect_outliers(
        self,
        indicator: str,
        method: str = "zscore",
        threshold: float = 2.5,
    ) -> pd.Series:
        """
        이상값 탐지.
        method: 'zscore' | 'iqr' | 'rolling_zscore'
        """
        s = self._df[indicator].dropna()

        if method == "zscore":
            mask = ((s - s.mean()) / s.std()).abs() > threshold

        elif method == "iqr":
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            mask = (s < q1 - threshold * iqr) | (s > q3 + threshold * iqr)

        elif method == "rolling_zscore":
            rm = s.rolling(4).mean()
            rs = s.rolling(4).std()
            mask = ((s - rm) / rs).abs() > threshold

        else:
            raise ValueError(f"지원하지 않는 method: {method}")

        return s[mask]

    # ------------------------------------------------------------------
    # 변곡점 탐지
    # ------------------------------------------------------------------

    def changepoints(
        self,
        indicator: str,
        window: int = 4,
        threshold_std: float = 1.5,
    ) -> pd.DatetimeIndex:
        """Rolling std 기준 급변 시점 반환."""
        s = self._df[indicator].dropna()
        diff = self.dataset.diff(1)[indicator]
        rolling_std_series = self.dataset.rolling_std(window, offset=1)[indicator]
        mask = rolling_std_series.abs() > threshold_std * diff.std()
        return s.index[mask.fillna(False)]

    # ------------------------------------------------------------------
    # 계절성
    # ------------------------------------------------------------------

    def seasonal_pattern(self, indicator: str) -> pd.DataFrame:
        """분기(또는 월)별 평균·표준편차·최솟값·최댓값 패턴."""
        s = self._df[indicator].dropna()
        freq_unit = "quarter" if "Q" in (self.dataset.freq or "") else "month"
        tmp = pd.DataFrame({"value": s, "period": getattr(s.index, freq_unit)})
        return tmp.groupby("period")["value"].agg(["mean", "std", "min", "max"])

    def seasonal_adjustment(self, indicator: str) -> pd.Series:
        """계절 조정 시계열 반환 (trend + residual)."""
        dec = self.decompose(indicator)
        return dec.trend + dec.residual

    # ------------------------------------------------------------------
    # 이동 변동성
    # ------------------------------------------------------------------

    def rolling_volatility(self, indicator: str, window: int = 4) -> pd.Series:
        """이동 표준편차 기반 변동성."""
        return self._df[indicator].rolling(window).std()

    def volatility_table(self, window: int = 4) -> pd.DataFrame:
        """전체 지표 이동 변동성 테이블."""
        return self._df.rolling(window).std()

    # ------------------------------------------------------------------
    # 내부 헬퍼
    # ------------------------------------------------------------------

    def _infer_period(self) -> int:
        freq = self.dataset.freq or ""
        if "Q" in freq: return 4
        if "M" in freq: return 12
        return 4
