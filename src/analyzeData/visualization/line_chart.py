"""
visualization/line_chart.py
추세선, 변화율, 예측 포함 라인 차트.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import List, Optional

from .base_chart import BaseChart
from ..core.dataset import EconDataset
from ..analysis.forecaster import ForecastResult


class LineChart(BaseChart):
    """
    경제지표 라인 차트 모음.

    Examples
    --------
    >>> lc = LineChart(ds)
    >>> fig = lc.multi_line(['총지수', '식료품'])
    >>> fig = lc.yoy_line(['총지수', '식료품'])
    >>> fig = lc.forecast_line('총지수', forecast_result)
    >>> fig = lc.area_stack()
    """

    def __init__(self, dataset: EconDataset, **kwargs):
        super().__init__(**kwargs)
        self.dataset = dataset
        self._df = dataset.df

    # ------------------------------------------------------------------
    # 멀티 라인
    # ------------------------------------------------------------------

    def multi_line(
        self,
        indicators: Optional[List[str]] = None,
        title: str = "경제지표 추이",
        normalize: bool = False,
        ma_window: Optional[int] = None,
    ):
        """여러 지표 동시 라인 플롯."""
        cols = indicators or self.dataset.indicators
        df = self._df[cols].copy()

        if normalize:
            df = (df - df.iloc[0]) / df.iloc[0] * 100  # base=0에서 누적 변화율

        fig, ax = self._setup_figure()

        for i, col in enumerate(cols):
            color = self.palette[i % len(self.palette)]
            ax.plot(df.index, df[col], label=col, color=color, linewidth=2)
            if ma_window:
                ax.plot(df.index, df[col].rolling(ma_window).mean(),
                        linestyle="--", color=color, alpha=0.6, linewidth=1.2,
                        label=f"{col} MA{ma_window}")

        self._apply_common(ax, title=title, ylabel="지수" if not normalize else "기준 대비 변화(%)")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        return fig

    # ------------------------------------------------------------------
    # YoY 변화율 라인
    # ------------------------------------------------------------------

    def yoy_line(
        self,
        indicators: Optional[List[str]] = None,
        periods: int = 4,
        title: str = "전년 동기 대비 변화율 (%)",
    ):
        cols = indicators or self.dataset.indicators
        yoy = self._df[cols].pct_change(periods=periods) * 100

        fig, ax = self._setup_figure()
        ax.axhline(0, color="black", linewidth=0.8, linestyle="--")

        for i, col in enumerate(cols):
            ax.plot(yoy.index, yoy[col], label=col,
                    color=self.palette[i % len(self.palette)], linewidth=2)

        self._apply_common(ax, title=title, ylabel="YoY 변화율 (%)")
        return fig

    # ------------------------------------------------------------------
    # 예측 포함 라인
    # ------------------------------------------------------------------

    def forecast_line(
        self,
        indicator: str,
        forecast_result: ForecastResult,
        title: Optional[str] = None,
    ):
        """실제값 + 예측값 + 신뢰구간 플롯."""
        s = self._df[indicator].dropna()
        fr = forecast_result
        t = title or f"{indicator} — {fr.method} 예측"

        fig, ax = self._setup_figure()
        ax.plot(s.index, s, label="실제값", color=self.palette[0], linewidth=2)
        ax.plot(fr.forecast.index, fr.forecast, label="예측값",
                color=self.palette[1], linestyle="--", linewidth=2)
        ax.fill_between(fr.forecast.index, fr.lower, fr.upper,
                        alpha=0.2, color=self.palette[1],
                        label=f"{int(fr.confidence*100)}% 신뢰구간")

        self._apply_common(ax, title=t, ylabel="지수")
        return fig

    # ------------------------------------------------------------------
    # 분해 플롯
    # ------------------------------------------------------------------

    def decomposition_plot(self, decomp_result):
        """DecompositionResult 4분할 플롯."""
        from ..analysis.timeseries import DecompositionResult
        dr = decomp_result
        fig, axes = self._setup_figure(nrows=4, ncols=1, figsize=(12, 12), sharex=True)

        components = [
            (dr.observed, "관측값"),
            (dr.trend, "추세"),
            (dr.seasonal, "계절성"),
            (dr.residual, "잔차"),
        ]
        for ax, (data, label) in zip(axes, components):
            ax.plot(data.index, data, color=self.palette[0], linewidth=1.5)
            ax.set_ylabel(label, fontsize=10)
            ax.grid(True, alpha=0.3)

        fig.suptitle(f"{dr.indicator} — 시계열 분해 (추세 강도: {dr.strength_trend:.2f}, 계절성 강도: {dr.strength_seasonal:.2f})",
                     fontsize=13, fontweight="bold")
        return fig
