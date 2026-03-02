"""
visualization/heatmap.py
상관관계·계절성 히트맵 차트.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List

from .base_chart import BaseChart
from ..core.dataset import EconDataset


class HeatmapChart(BaseChart):
    """
    히트맵 시각화.

    Examples
    --------
    >>> hm = HeatmapChart(ds)
    >>> fig = hm.correlation_heatmap()
    >>> fig = hm.seasonal_heatmap('총지수')
    >>> fig = hm.yoy_heatmap()
    """

    def __init__(self, dataset: EconDataset, **kwargs):
        super().__init__(**kwargs)
        self.dataset = dataset
        self._df = dataset.df

    def correlation_heatmap(
        self,
        method: str = "pearson",
        title: str = "지표 간 상관관계",
        annot: bool = True,
    ):
        """지표 간 상관계수 히트맵."""
        corr = self._df.corr(method=method)
        fig, ax = self._setup_figure(figsize=(8, 6))
        sns.heatmap(
            corr, annot=annot, fmt=".2f", cmap="RdYlGn",
            vmin=-1, vmax=1, ax=ax, linewidths=0.5,
            annot_kws={"size": 9},
        )
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.tick_params(axis="x", rotation=30)
        ax.tick_params(axis="y", rotation=0)
        return fig

    def seasonal_heatmap(
        self,
        indicator: str,
        title: Optional[str] = None,
    ):
        """연도 × 분기(월) YoY 변화율 히트맵."""
        s = self._df[indicator].dropna()
        yoy = s.pct_change(4) * 100
        df = pd.DataFrame({"value": yoy, "year": yoy.index.year, "quarter": yoy.index.quarter})
        pivot = df.pivot(index="year", columns="quarter", values="value")
        pivot.columns = [f"Q{q}" for q in pivot.columns]

        fig, ax = self._setup_figure(figsize=(8, max(4, len(pivot) * 0.5)))
        sns.heatmap(
            pivot, annot=True, fmt=".1f", cmap="RdYlGn",
            center=0, ax=ax, linewidths=0.5, annot_kws={"size": 9},
        )
        ax.set_title(title or f"{indicator} — 연도×분기 YoY 변화율 (%)", fontsize=13, fontweight="bold")
        return fig

    def yoy_heatmap(self, periods: int = 4, title: str = "지표별 YoY 변화율 히트맵"):
        """시점 × 지표 YoY 변화율 히트맵."""
        yoy = self._df.pct_change(periods) * 100
        yoy.index = yoy.index.strftime("%Y-%m")
        fig, ax = self._setup_figure(figsize=(14, max(6, len(yoy) * 0.4)))
        sns.heatmap(
            yoy.T, annot=True, fmt=".1f", cmap="RdYlGn",
            center=0, ax=ax, linewidths=0.3, annot_kws={"size": 8},
        )
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.tick_params(axis="x", rotation=45)
        return fig
