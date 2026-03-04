"""
visualizeData/heatmap.py
Plotly 기반 히트맵 — 상관관계, 계절성, YoY 전체, Rolling 상관계수.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Optional, List

from visualizeData.charts.base_chart import BaseChart
from core.econData.EconDataset import EconDataset


class HeatmapChart(BaseChart):
    """
    Plotly 기반 히트맵 시각화.

    Examples
    --------
    >>> hm = HeatmapChart(ds)
    >>> fig = hm.correlation_heatmap()
    >>> fig = hm.seasonal_heatmap('총지수')
    >>> fig = hm.yoy_heatmap()
    >>> fig = hm.rolling_corr_heatmap('총지수', '식료품및비주류음료')
    >>> fig.show()
    """

    def __init__(self, dataset: EconDataset, **kwargs):
        super().__init__(**kwargs)
        self.dataset = dataset
        self._df = dataset.df

    # ------------------------------------------------------------------
    # 상관관계 히트맵
    # ------------------------------------------------------------------

    def correlation_heatmap(
        self,
        method: str = "pearson",
        title: str = "지표 간 상관관계",
    ) -> go.Figure:
        corr   = self._df.corr(method=method).round(3)
        labels = corr.columns.tolist()
        h      = max(400, len(labels) * 80)

        fig = go.Figure(go.Heatmap(
            z=corr.values, x=labels, y=labels,
            colorscale="RdYlGn", zmin=-1, zmax=1,
            text=corr.values.round(2),
            texttemplate="%{text}",
            textfont=dict(size=11),
            hovertemplate="<b>%{y}</b> vs <b>%{x}</b><br>상관계수: %{z:.3f}<extra></extra>",
            colorbar=dict(title="상관계수", thickness=15),
        ))
        fig.update_layout(**self._base_layout(title=title, height=h))
        fig.update_xaxes(tickangle=30)
        return fig

    # ------------------------------------------------------------------
    # 계절성 히트맵 (연도 × 분기)
    # ------------------------------------------------------------------

    def seasonal_heatmap(
        self,
        indicator: str,
        title: Optional[str] = None,
    ) -> go.Figure:
        """연도 × 분기 YoY 변화율(%) 히트맵."""
        s   = self._df[indicator].dropna()
        yoy = s.pct_change(4) * 100
        pivot = (
            pd.DataFrame({"value": yoy, "year": yoy.index.year, "quarter": yoy.index.quarter})
            .pivot(index="year", columns="quarter", values="value")
        )
        pivot.columns = [f"Q{q}" for q in pivot.columns]
        z    = pivot.values.round(2)
        text = [[f"{v:.1f}%" if not np.isnan(v) else "" for v in row] for row in z]
        h    = max(400, len(pivot) * 45)

        fig = go.Figure(go.Heatmap(
            z=z, x=pivot.columns.tolist(), y=pivot.index.tolist(),
            colorscale="RdYlGn", zmid=0,
            text=text, texttemplate="%{text}", textfont=dict(size=11),
            hovertemplate="<b>%{y}년 %{x}</b><br>YoY: %{z:.2f}%<extra></extra>",
            colorbar=dict(title="YoY (%)", thickness=15),
        ))
        fig.update_layout(**self._base_layout(
            title=title or f"{indicator} — 연도×분기 YoY 변화율 (%)",
            xaxis_title="분기",
            yaxis_title="연도",
            height=h,
        ))
        return fig

    # ------------------------------------------------------------------
    # 전체 YoY 히트맵 (시점 × 지표)
    # ------------------------------------------------------------------

    def yoy_heatmap(
        self,
        periods: int = 4,
        title: str = "지표별 YoY 변화율 히트맵",
    ) -> go.Figure:
        yoy  = self._df.pct_change(periods) * 100
        z    = yoy.T.values.round(2)
        text = [[f"{v:.1f}%" if not np.isnan(v) else "" for v in row] for row in z]
        h    = max(300, len(yoy.columns) * 60)

        fig = go.Figure(go.Heatmap(
            z=z,
            x=yoy.index.strftime("%Y-%m").tolist(),
            y=yoy.columns.tolist(),
            colorscale="RdYlGn", zmid=0,
            text=text, texttemplate="%{text}", textfont=dict(size=9),
            hovertemplate="<b>%{y}</b><br>%{x}<br>YoY: %{z:.2f}%<extra></extra>",
            colorbar=dict(title="YoY (%)", thickness=15),
        ))
        fig.update_layout(**self._base_layout(
            title=title,
            height=h,
            xaxis_title="날짜",
        ))
        fig.update_xaxes(tickangle=45)
        return fig

    # ------------------------------------------------------------------
    # Rolling 상관계수 히트맵 (window × 시점)
    # ------------------------------------------------------------------

    def rolling_corr_heatmap(
        self,
        indicator_a: str,
        indicator_b: str,
        windows: Optional[List[int]] = None,
        title: Optional[str] = None,
    ) -> go.Figure:
        """다양한 window 크기에 따른 두 지표 간 이동 상관계수 히트맵."""
        windows = windows or [2, 3, 4, 6, 8]
        z = [
            self._df[indicator_a].rolling(w).corr(self._df[indicator_b]).round(3).values
            for w in windows
        ]
        h = max(300, len(windows) * 60)

        fig = go.Figure(go.Heatmap(
            z=z,
            x=self._df.index.strftime("%Y-%m").tolist(),
            y=[f"window={w}" for w in windows],
            colorscale="RdYlGn", zmid=0, zmin=-1, zmax=1,
            hovertemplate="%{y}<br>%{x}<br>상관계수: %{z:.3f}<extra></extra>",
            colorbar=dict(title="상관계수", thickness=15),
        ))
        fig.update_layout(**self._base_layout(
            title=title or f"{indicator_a} × {indicator_b} — Rolling 상관계수",
            xaxis_title="날짜",
            yaxis_title="Window",
            height=h,
        ))
        fig.update_xaxes(tickangle=45)
        return fig