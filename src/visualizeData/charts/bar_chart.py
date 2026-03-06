"""
visualizeData/bar_chart.py
Plotly 기반 바 차트 — YoY 단일, 그룹 비교, 구간 비교, 기여도 스택, 순위.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import List, Optional, Tuple

from visualizeData.charts.base_chart import BaseChart
from core.econData.EconDataset import EconDataset


class BarChart(BaseChart):
    def __init__(self, dataset: EconDataset, **kwargs):
        super().__init__(**kwargs)
        self.dataset = dataset
        self._df = dataset.df

    # ------------------------------------------------------------------
    # 단일 지표 YoY 바
    # ------------------------------------------------------------------

    def yoy_bar(
        self,
        indicator: str,
        periods: int = 4,
        title: Optional[str] = None,
    ) -> go.Figure:
        """단일 지표 YoY 변화율 바 차트 (양수=파랑, 음수=빨강)."""
        yoy    = self.dataset.pct_change(periods)[indicator] * 100
        colors = [self.palette[0] if v >= 0 else self.palette[1] for v in yoy]

        fig = go.Figure(go.Bar(
            x=yoy.index, y=yoy, marker_color=colors,
            hovertemplate=f"<b>{indicator}</b><br>%{{x|%Y-%m}}: %{{y:.2f}}%<extra></extra>",
        ))
        fig.add_hline(y=0, line_width=1, line_color="#94a3b8")
        fig.update_layout(**self._base_layout(
            title=title or f"{indicator} — YoY 변화율 (%)",
            yaxis_title="YoY 변화율 (%)",
        ))
        return fig

    # ------------------------------------------------------------------
    # 그룹 바 (여러 지표)
    # ------------------------------------------------------------------

    def grouped_bar(
        self,
        indicators: Optional[List[str]] = None,
        periods: int = 4,
        title: str = "지표별 YoY 변화율 비교",
    ) -> go.Figure:
        cols = indicators or self.dataset.indicators
        yoy  = self._df[cols].pct_change(periods) * 100

        fig = go.Figure()
        for i, col in enumerate(cols):
            fig.add_trace(go.Bar(
                x=yoy.index, y=yoy[col], name=col,
                marker_color=self.palette[i % len(self.palette)],
                hovertemplate=f"<b>{col}</b><br>%{{x|%Y-%m}}: %{{y:.2f}}%<extra></extra>",
            ))
        fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#94a3b8")
        fig.update_layout(
            **self._base_layout(title=title, yaxis_title="YoY 변화율 (%)"),
            barmode="group",
        )
        return fig

    # ------------------------------------------------------------------
    # 구간 평균 비교 바
    # ------------------------------------------------------------------

    def period_compare_bar(
        self,
        period_a: Tuple[str, str],
        period_b: Tuple[str, str],
        stat: str = "mean",
        title: Optional[str] = None,
    ) -> go.Figure:
        """두 기간의 지표별 통계량 비교 그룹 바."""
        a  = getattr(self._df.loc[period_a[0]:period_a[1]], stat)()
        b  = getattr(self._df.loc[period_b[0]:period_b[1]], stat)()
        la = f"{period_a[0]} ~ {period_a[1]}"
        lb = f"{period_b[0]} ~ {period_b[1]}"

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=self.dataset.indicators, y=a, name=la,
            marker_color=self.palette[0],
            hovertemplate=f"<b>%{{x}}</b><br>{la}: %{{y:.2f}}<extra></extra>",
        ))
        fig.add_trace(go.Bar(
            x=self.dataset.indicators, y=b, name=lb,
            marker_color=self.palette[1],
            hovertemplate=f"<b>%{{x}}</b><br>{lb}: %{{y:.2f}}<extra></extra>",
        ))
        fig.update_layout(
            **self._base_layout(title=title or f"기간 비교 ({stat})", yaxis_title="지수"),
            barmode="group",
        )
        return fig

    # ------------------------------------------------------------------
    # 기여도 스택 바
    # ------------------------------------------------------------------

    def contribution_bar(
        self,
        weights: Optional[dict] = None,
        periods: int = 4,
        title: str = "지표별 YoY 기여도",
    ) -> go.Figure:
        """가중치 기반 YoY 기여도 스택 바."""
        cols = self.dataset.indicators
        w    = weights or {c: 1 / len(cols) for c in cols}
        yoy  = self._df[cols].pct_change(periods) * 100

        fig = go.Figure()
        for i, col in enumerate(cols):
            fig.add_trace(go.Bar(
                x=yoy.index, y=yoy[col] * w.get(col, 0), name=col,
                marker_color=self.palette[i % len(self.palette)],
                hovertemplate=f"<b>{col}</b><br>%{{x|%Y-%m}}: %{{y:.2f}}%p<extra></extra>",
            ))
        fig.add_hline(y=0, line_width=1, line_color="#94a3b8")
        fig.update_layout(
            **self._base_layout(title=title, yaxis_title="기여도 (%p)"),
            barmode="relative",
        )
        return fig

    # ------------------------------------------------------------------
    # 최신 시점 순위 가로 바
    # ------------------------------------------------------------------

    def rank_bar(
        self,
        periods: int = 4,
        title: str = "최근 YoY 변화율 순위",
    ) -> go.Figure:
        """최신 시점 YoY 변화율 기준 가로 순위 바."""
        yoy_sorted = (self._df.pct_change(periods).iloc[-1] * 100).sort_values()
        colors     = [self.palette[0] if v >= 0 else self.palette[1] for v in yoy_sorted]
        h          = max(300, len(yoy_sorted) * 50)

        fig = go.Figure(go.Bar(
            x=yoy_sorted.values, y=yoy_sorted.index,
            orientation="h", marker_color=colors,
            hovertemplate="<b>%{y}</b><br>YoY: %{x:.2f}%<extra></extra>",
        ))
        fig.add_vline(x=0, line_width=1, line_color="#94a3b8")
        fig.update_layout(**self._base_layout(
            title=title,
            xaxis_title="YoY 변화율 (%)",
            height=h,
        ))
        return fig