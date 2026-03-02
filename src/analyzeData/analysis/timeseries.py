"""
analysis/timeseries.py
시계열 분석기 — 추세 분해, 계절성, 이상값 탐지, 변곡점.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from typing import Optional, List, Tuple
from dataclasses import dataclass, field

from ..core.dataset import EconDataset


@dataclass
class DecompositionResult:
    """seasonal_decompose 결과 컨테이너."""
    indicator: str
    observed: pd.Series
    trend: pd.Series
    seasonal: pd.Series
    residual: pd.Series
    strength_trend: float = field(init=False)
    strength_seasonal: float = field(init=False)

    def __post_init__(self):
        var_resid = self.residual.var()
        self.strength_trend = max(0, 1 - var_resid / (self.trend + self.residual).var())
        self.strength_seasonal = max(0, 1 - var_resid / (self.seasonal + self.residual).var())


class TimeSeriesAnalyzer:
    """
    시계열 분석기.

    Examples
    --------
    >>> tsa = TimeSeriesAnalyzer(ds)
    >>> result = tsa.decompose('총지수')      # DecompositionResult
    >>> tsa.detect_outliers('총지수')         # 이상값 Series
    >>> tsa.changepoints('총지수')            # 변화율 급변 시점
    >>> tsa.rolling_volatility('총지수', 4)   # 이동 변동성
    >>> tsa.seasonal_pattern('총지수')        # 분기별 평균 패턴
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
        STL/classical 분해.

        Parameters
        ----------
        model : 'additive' | 'multiplicative'
        period : 계절 주기 (분기=4, 월=12). 미지정 시 자동 추론.
        """
        try:
            from statsmodels.tsa.seasonal import seasonal_decompose
        except ImportError:
            raise ImportError("pip install statsmodels 를 먼저 실행하세요.")

        s = self._df[indicator].dropna()
        p = period or self._infer_period()
        result = seasonal_decompose(s, model=model, period=p, extrapolate_trend="freq")
        return DecompositionResult(
            indicator=indicator,
            observed=result.observed,
            trend=result.trend,
            seasonal=result.seasonal,
            residual=result.resid,
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

        Parameters
        ----------
        method : 'zscore' | 'iqr' | 'rolling_zscore'
        threshold : z-score 임계값 또는 IQR 배수
        """
        s = self._df[indicator].dropna()

        if method == "zscore":
            z = (s - s.mean()) / s.std()
            mask = z.abs() > threshold
        elif method == "iqr":
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            mask = (s < q1 - threshold * iqr) | (s > q3 + threshold * iqr)
        elif method == "rolling_zscore":
            roll_mean = s.rolling(4).mean()
            roll_std = s.rolling(4).std()
            z = (s - roll_mean) / roll_std
            mask = z.abs() > threshold
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
        """
        변화율의 급격한 변동 시점 반환.
        rolling std를 기준으로 급변 구간 탐지.
        """
        s = self._df[indicator].dropna()
        diff = s.diff()
        roll_std = diff.rolling(window).std()
        global_std = diff.std()
        mask = roll_std.abs() > threshold_std * global_std
        return s.index[mask.fillna(False)]

    # ------------------------------------------------------------------
    # 계절성
    # ------------------------------------------------------------------

    def seasonal_pattern(self, indicator: str) -> pd.DataFrame:
        """분기(또는 월)별 평균·표준편차 패턴."""
        s = self._df[indicator].dropna()
        freq_unit = "quarter" if "Q" in (self.dataset.freq or "") else "month"
        period_func = getattr(s.index, freq_unit)
        tmp = pd.DataFrame({"value": s, "period": period_func})
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
        if "Q" in freq:
            return 4
        if "M" in freq:
            return 12
        if "A" in freq or "Y" in freq:
            return 1
        return 4  # 기본값
