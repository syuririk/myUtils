"""
analyzeData/forecaster.py
단기 예측 모델 — 선형 추세, 이동평균 연장, ARIMA.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Optional

from core.dataset import EconDataset


@dataclass
class ForecastResult:
    """예측 결과 컨테이너."""
    indicator:  str
    forecast:   pd.Series
    lower:      pd.Series
    upper:      pd.Series
    method:     str
    confidence: float = 0.95


class Forecaster:
    """
    경제지표 단기 예측기.

    Examples
    --------
    >>> fc = Forecaster(ds)
    >>> res = fc.linear_trend('총지수', steps=4)   # 선형 추세 연장
    >>> res = fc.arima('총지수', steps=4)          # ARIMA
    >>> res = fc.ma_extension('총지수', steps=4)   # 이동평균 수평 연장
    >>> res.forecast   # 예측 Series
    >>> res.lower      # 신뢰 하한
    >>> res.upper      # 신뢰 상한
    """

    def __init__(self, dataset: EconDataset):
        self.dataset = dataset
        self._df = dataset.df

    # ------------------------------------------------------------------
    # 선형 추세
    # ------------------------------------------------------------------

    def linear_trend(
        self,
        indicator: str,
        steps: int = 4,
        window: Optional[int] = None,
        confidence: float = 0.95,
    ) -> ForecastResult:
        """
        선형 회귀 추세선 연장 예측.
        window: 최근 N 포인트만 사용. None 이면 전체.
        """
        s = self._df[indicator].dropna()
        if window:
            s = s.iloc[-window:]

        x = np.arange(len(s))
        slope, intercept = np.polyfit(x, s.values, 1)

        future_idx = pd.date_range(s.index[-1], periods=steps + 1, freq=self.dataset.freq)[1:]
        x_future   = np.arange(len(s), len(s) + steps)
        forecast_vals = slope * x_future + intercept

        residuals = s.values - (slope * x + intercept)
        se = residuals.std()
        from scipy.stats import t as t_dist
        t_val  = t_dist.ppf((1 + confidence) / 2, df=len(s) - 2)
        margin = t_val * se * np.sqrt(1 + 1 / len(s))

        forecast = pd.Series(forecast_vals, index=future_idx, name=f"{indicator}_forecast")
        return ForecastResult(
            indicator=indicator,
            forecast=forecast,
            lower=forecast - margin,
            upper=forecast + margin,
            method="linear_trend",
            confidence=confidence,
        )

    # ------------------------------------------------------------------
    # ARIMA
    # ------------------------------------------------------------------

    def arima(
        self,
        indicator: str,
        steps: int = 4,
        order: tuple = (1, 1, 1),
        confidence: float = 0.95,
    ) -> ForecastResult:
        """ARIMA 예측. statsmodels 필요."""
        try:
            from statsmodels.tsa.arima.model import ARIMA
        except ImportError:
            raise ImportError("pip install statsmodels 를 먼저 실행하세요.")

        s = self._df[indicator].dropna()
        pred = ARIMA(s, order=order).fit().get_forecast(steps=steps)
        ci   = pred.conf_int(alpha=1 - confidence)
        future_idx = pd.date_range(s.index[-1], periods=steps + 1, freq=self.dataset.freq)[1:]

        return ForecastResult(
            indicator=indicator,
            forecast=pd.Series(pred.predicted_mean.values, index=future_idx),
            lower=pd.Series(ci.iloc[:, 0].values, index=future_idx),
            upper=pd.Series(ci.iloc[:, 1].values, index=future_idx),
            method="arima",
            confidence=confidence,
        )

    # ------------------------------------------------------------------
    # 이동평균 수평 연장
    # ------------------------------------------------------------------

    def ma_extension(
        self,
        indicator: str,
        window: int = 4,
        steps: int = 4,
    ) -> ForecastResult:
        """마지막 이동평균값을 수평으로 연장하는 단순 예측."""
        s = self._df[indicator].dropna()
        last_ma  = s.rolling(window).mean().iloc[-1]
        roll_std = s.rolling(window).std().iloc[-1]
        future_idx = pd.date_range(s.index[-1], periods=steps + 1, freq=self.dataset.freq)[1:]
        forecast = pd.Series([last_ma] * steps, index=future_idx)

        return ForecastResult(
            indicator=indicator,
            forecast=forecast,
            lower=forecast - 2 * roll_std,
            upper=forecast + 2 * roll_std,
            method="ma_extension",
        )
