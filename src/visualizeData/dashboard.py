"""
visualizeData/dashboard.py
Plotly 기반 대화형 대시보드 — 여러 차트를 서브플롯으로 결합.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Optional

from visualizeData.base_chart import BaseChart
from core.econData.EconDataset import EconDataset


class Dashboard(BaseChart):
    """
    대화형 Plotly 대시보드.

    Examples
    --------
    >>> db = Dashboard(ds)
    >>> fig = db.overview()
    >>> fig = db.compare_panel('총지수', '식료품')
    >>> fig = db.lead_lag_panel('총지수', '식료품')
    >>> fig.show()
    >>> db.save_html(fig, 'dashboard.html')
    """

    def __init__(self, dataset: EconDataset, **kwargs):
        super().__init__(**kwargs)
        self.dataset = dataset
        self._df = dataset.df

    # ------------------------------------------------------------------
    # 전체 개요 (3행)
    # ------------------------------------------------------------------

    def overview(
        self,
        indicators: Optional[List[str]] = None,
        title: str = "경제지표 종합 개요",
    ) -> go.Figure:
        """
        Row 1 : 지수 레벨 추이
        Row 2 : YoY 변화율
        Row 3 : 이동 변동성 (4기 rolling std)
        """
        cols = indicators or self.dataset.indicators
        yoy  = self._df[cols].pct_change(4) * 100
        vol  = self._df[cols].rolling(4).std()

        fig = make_subplots(
            rows=3, cols=1, shared_xaxes=True,
            subplot_titles=["지수 레벨", "YoY 변화율 (%)", "이동 변동성 (4기 rolling std)"],
            vertical_spacing=0.07,
            row_heights=[0.4, 0.35, 0.25],
        )
        for i, col in enumerate(cols):
            color = self.palette[i % len(self.palette)]
            fig.add_trace(go.Scatter(
                x=self._df.index, y=self._df[col], name=col, mode="lines",
                line=dict(color=color, width=2),
                legendgroup=col,
                hovertemplate=f"<b>{col}</b><br>%{{x|%Y-%m}}: %{{y:.2f}}<extra></extra>",
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=yoy.index, y=yoy[col], name=col, mode="lines",
                line=dict(color=color, width=2),
                legendgroup=col, showlegend=False,
                hovertemplate=f"<b>{col}</b><br>%{{x|%Y-%m}}: %{{y:.2f}}%<extra></extra>",
            ), row=2, col=1)
            fig.add_trace(go.Scatter(
                x=vol.index, y=vol[col], name=col, mode="lines",
                line=dict(color=color, width=1.5, dash="dot"),
                legendgroup=col, showlegend=False,
                hovertemplate=f"<b>{col}</b><br>%{{x|%Y-%m}}: %{{y:.3f}}<extra></extra>",
            ), row=3, col=1)

        fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#94a3b8", row=2, col=1)
        fig.update_layout(
            title=dict(text=title, font=dict(size=16, color="#1e293b"), x=0.02),
            height=self.height * 2, width=self.width,
            template=self.theme, paper_bgcolor="white", plot_bgcolor="white",
            hovermode="x unified",
            font=dict(family="Arial, sans-serif", size=12),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(l=60, r=40, t=100, b=60),
        )
        return fig

    # ------------------------------------------------------------------
    # 두 지표 상세 비교 (2×2)
    # ------------------------------------------------------------------

    def compare_panel(
        self,
        indicator_a: str,
        indicator_b: str,
        title: Optional[str] = None,
    ) -> go.Figure:
        """
        (1,1) 레벨 비교      (1,2) 누적 변화율 비교
        (2,1) YoY 비교       (2,2) Rolling 상관계수 (4기)
        """
        df   = self._df[[indicator_a, indicator_b]]
        yoy  = df.pct_change(4) * 100
        norm = (df - df.iloc[0]) / df.iloc[0] * 100
        rc   = df[indicator_a].rolling(4).corr(df[indicator_b])
        ca, cb = self.palette[0], self.palette[1]

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                "지수 레벨", "기준 시점 대비 누적 변화율 (%)",
                "YoY 변화율 (%)", "Rolling 상관계수 (4기)",
            ],
            vertical_spacing=0.14, horizontal_spacing=0.1,
        )
        for (row, source) in [(1, df), (2, yoy)]:
            for col, color in [(indicator_a, ca), (indicator_b, cb)]:
                fig.add_trace(go.Scatter(
                    x=source.index, y=source[col], name=col, mode="lines",
                    line=dict(color=color, width=2),
                    legendgroup=col, showlegend=(row == 1),
                    hovertemplate=f"<b>{col}</b><br>%{{x|%Y-%m}}: %{{y:.2f}}<extra></extra>",
                ), row=row, col=1)

        for col, color in [(indicator_a, ca), (indicator_b, cb)]:
            fig.add_trace(go.Scatter(
                x=norm.index, y=norm[col], name=col, mode="lines",
                line=dict(color=color, width=2),
                legendgroup=col, showlegend=False,
                hovertemplate=f"<b>{col}</b><br>%{{x|%Y-%m}}: %{{y:.2f}}%<extra></extra>",
            ), row=1, col=2)

        fig.add_trace(go.Scatter(
            x=rc.index, y=rc, name="Rolling 상관계수", mode="lines",
            line=dict(color=self.palette[2], width=2),
            fill="tozeroy", fillcolor="rgba(37,99,235,0.08)",
            showlegend=False,
            hovertemplate="Rolling 상관계수<br>%{x|%Y-%m}: %{y:.3f}<extra></extra>",
        ), row=2, col=2)

        fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#94a3b8", row=2, col=1)
        fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#94a3b8", row=2, col=2)
        fig.update_layout(
            title=dict(
                text=title or f"{indicator_a} vs {indicator_b} 비교 분석",
                font=dict(size=16, color="#1e293b"), x=0.02,
            ),
            height=self.height * 2, width=self.width,
            template=self.theme, paper_bgcolor="white", plot_bgcolor="white",
            hovermode="x unified",
            font=dict(family="Arial, sans-serif", size=12),
            legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="left", x=0),
            margin=dict(l=60, r=40, t=100, b=60),
        )
        return fig

    # ------------------------------------------------------------------
    # 리드-래그 패널 (1×2)
    # ------------------------------------------------------------------

    def lead_lag_panel(
        self,
        indicator_a: str,
        indicator_b: str,
        max_lag: int = 4,
        title: Optional[str] = None,
    ) -> go.Figure:
        """
        (1,1) 두 지표 YoY 오버레이
        (1,2) lag별 상관계수 바 차트
        """
        yoy_a = self._df[indicator_a].pct_change(4) * 100
        yoy_b = self._df[indicator_b].pct_change(4) * 100

        lags  = list(range(-max_lag, max_lag + 1))
        corrs = [
            yoy_a.corr(yoy_b.shift(-lag)) if lag < 0 else yoy_a.shift(lag).corr(yoy_b)
            for lag in lags
        ]
        best_lag   = lags[int(np.argmax(np.abs(corrs)))]
        bar_colors = [self.palette[0] if v >= 0 else self.palette[1] for v in corrs]

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=[
                "YoY 변화율 오버레이",
                f"Lag별 상관계수 (best lag={best_lag})",
            ],
            horizontal_spacing=0.12,
        )
        for series, label, color in [
            (yoy_a, indicator_a, self.palette[0]),
            (yoy_b, indicator_b, self.palette[1]),
        ]:
            fig.add_trace(go.Scatter(
                x=series.index, y=series, name=label, mode="lines",
                line=dict(color=color, width=2),
                hovertemplate=f"<b>{label}</b><br>%{{x|%Y-%m}}: %{{y:.2f}}%<extra></extra>",
            ), row=1, col=1)

        fig.add_trace(go.Bar(
            x=lags, y=corrs, marker_color=bar_colors, name="상관계수", showlegend=False,
            hovertemplate="lag=%{x}<br>상관계수: %{y:.3f}<extra></extra>",
        ), row=1, col=2)

        fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#94a3b8", row=1, col=1)
        fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="#94a3b8", row=1, col=2)
        fig.update_layout(
            title=dict(
                text=title or f"{indicator_a} ↔ {indicator_b} 리드-래그 분석",
                font=dict(size=16, color="#1e293b"), x=0.02,
            ),
            height=self.height, width=self.width,
            template=self.theme, paper_bgcolor="white", plot_bgcolor="white",
            hovermode="x unified",
            font=dict(family="Arial, sans-serif", size=12),
            legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="left", x=0),
            margin=dict(l=60, r=40, t=100, b=60),
        )
        return fig
