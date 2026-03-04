"""
visualizeData/line_chart.py
Plotly 기반 라인 차트 — 추세선, YoY/QoQ 변화율, 예측, 시계열 분해, 누적 변화율.
"""

from __future__ import annotations

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Optional

from visualizeData.charts.base_chart import BaseChart
from core.econData.EconDataset import EconDataset
from analyzeData.analysis.forecaster import ForecastResult


class LineChart(BaseChart):
    """
    Plotly 기반 라인 차트 모음.

    Examples
    --------
    >>> lc = LineChart(ds)
    >>> fig = lc.multi_line(['총지수', '식료품'])
    >>> fig = lc.yoy_line()
    >>> fig = lc.qoq_line()
    >>> fig = lc.forecast_line('총지수', forecast_result)
    >>> fig = lc.decomposition_plot(decomp_result)
    >>> fig = lc.cumulative_line()
    >>> fig.show()
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
    ) -> go.Figure:
        """여러 지표 동시 라인 플롯."""
        cols = indicators or self.dataset.indicators
        df = self._df[cols].copy()
        if normalize:
            df = (df - df.iloc[0]) / df.iloc[0] * 100

        fig = go.Figure()
        for i, col in enumerate(cols):
            color = self.palette[i % len(self.palette)]
            fig.add_trace(go.Scatter(
                x=df.index, y=df[col], name=col, mode="lines",
                line=dict(color=color, width=2),
                hovertemplate=f"<b>{col}</b><br>%{{x|%Y-%m}}: %{{y:.2f}}<extra></extra>",
            ))
            if ma_window:
                fig.add_trace(go.Scatter(
                    x=df.index, y=df[col].rolling(ma_window).mean(),
                    name=f"{col} MA{ma_window}", mode="lines",
                    line=dict(color=color, width=1.5, dash="dash"),
                    opacity=0.6,
                    hovertemplate=f"<b>{col} MA{ma_window}</b><br>%{{y:.2f}}<extra></extra>",
                ))

        ylabel = "기준 대비 변화(%)" if normalize else "지수"
        fig.update_layout(**self._base_layout(title=title, yaxis_title=ylabel))
        return fig

    # ------------------------------------------------------------------
    # YoY 변화율 라인
    # ------------------------------------------------------------------

    def yoy_line(
        self,
        indicators: Optional[List[str]] = None,
        periods: int = 4,
        title: str = "전년 동기 대비 변화율 (%)",
    ) -> go.Figure:
        cols = indicators or self.dataset.indicators
        yoy = self._df[cols].pct_change(periods=periods) * 100

        fig = go.Figure()
        fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#94a3b8")
        for i, col in enumerate(cols):
            fig.add_trace(go.Scatter(
                x=yoy.index, y=yoy[col], name=col, mode="lines",
                line=dict(color=self.palette[i % len(self.palette)], width=2),
                hovertemplate=f"<b>{col}</b><br>%{{x|%Y-%m}}: %{{y:.2f}}%<extra></extra>",
            ))
        fig.update_layout(**self._base_layout(title=title, yaxis_title="YoY 변화율 (%)"))
        return fig

    # ------------------------------------------------------------------
    # QoQ 변화율 라인
    # ------------------------------------------------------------------

    def qoq_line(
        self,
        indicators: Optional[List[str]] = None,
        title: str = "전분기 대비 변화율 (%)",
    ) -> go.Figure:
        cols = indicators or self.dataset.indicators
        qoq = self._df[cols].pct_change(periods=1) * 100

        fig = go.Figure()
        fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#94a3b8")
        for i, col in enumerate(cols):
            fig.add_trace(go.Scatter(
                x=qoq.index, y=qoq[col], name=col, mode="lines+markers",
                line=dict(color=self.palette[i % len(self.palette)], width=2),
                marker=dict(size=5),
                hovertemplate=f"<b>{col}</b><br>%{{x|%Y-%m}}: %{{y:.2f}}%<extra></extra>",
            ))
        fig.update_layout(**self._base_layout(title=title, yaxis_title="QoQ 변화율 (%)"))
        return fig

    # ------------------------------------------------------------------
    # 예측 포함 라인
    # ------------------------------------------------------------------

    def forecast_line(
        self,
        indicator: str,
        forecast_result: ForecastResult,
        title: Optional[str] = None,
    ) -> go.Figure:
        """실제값 + 예측값 + 신뢰구간."""
        s  = self._df[indicator].dropna()
        fr = forecast_result
        t  = title or f"{indicator} — {fr.method} 예측"

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=s.index, y=s, name="실제값", mode="lines",
            line=dict(color=self.palette[0], width=2.5),
            hovertemplate="<b>실제값</b><br>%{x|%Y-%m}: %{y:.2f}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=list(fr.upper.index) + list(fr.lower.index[::-1]),
            y=list(fr.upper.values) + list(fr.lower.values[::-1]),
            fill="toself", fillcolor="rgba(220,38,38,0.15)",
            line=dict(color="rgba(255,255,255,0)"),
            name=f"{int(fr.confidence*100)}% 신뢰구간",
            hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=fr.forecast.index, y=fr.forecast, name="예측값",
            mode="lines+markers",
            line=dict(color=self.palette[1], width=2, dash="dash"),
            marker=dict(size=6, symbol="circle-open"),
            hovertemplate="<b>예측값</b><br>%{x|%Y-%m}: %{y:.2f}<extra></extra>",
        ))
        fig.update_layout(**self._base_layout(title=t, yaxis_title="지수"))
        return fig

    # ------------------------------------------------------------------
    # 시계열 분해 플롯
    # ------------------------------------------------------------------

    def decomposition_plot(self, decomp_result) -> go.Figure:
        """DecompositionResult — 관측값 / 추세 / 계절성 / 잔차 4분할 차트."""
        dr = decomp_result
        components = [
            (dr.observed, "관측값"),
            (dr.trend,    "추세"),
            (dr.seasonal, "계절성"),
            (dr.residual, "잔차"),
        ]
        fig = make_subplots(
            rows=4, cols=1, shared_xaxes=True,
            subplot_titles=[label for _, label in components],
            vertical_spacing=0.06,
        )
        for row, (data, label) in enumerate(components, start=1):
            fig.add_trace(go.Scatter(
                x=data.index, y=data, name=label, mode="lines",
                line=dict(color=self.palette[row - 1], width=1.8),
                hovertemplate=f"<b>{label}</b><br>%{{x|%Y-%m}}: %{{y:.3f}}<extra></extra>",
            ), row=row, col=1)

        fig.update_layout(
            title=dict(
                text=(
                    f"{dr.indicator} — 시계열 분해 "
                    f"(추세 강도: {dr.strength_trend:.2f}, "
                    f"계절성 강도: {dr.strength_seasonal:.2f})"
                ),
                font=dict(size=15, color="#1e293b"), x=0.02,
            ),
            height=self.height * 2, width=self.width,
            showlegend=False, template=self.theme,
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(family="Arial, sans-serif", size=12),
            margin=dict(l=60, r=40, t=80, b=60),
        )
        return fig

    # ------------------------------------------------------------------
    # 누적 변화율
    # ------------------------------------------------------------------

    def cumulative_line(
        self,
        indicators: Optional[List[str]] = None,
        base_period: Optional[str] = None,
        title: str = "기준 시점 대비 누적 변화율 (%)",
    ) -> go.Figure:
        cols = indicators or self.dataset.indicators
        df   = self._df[cols].copy()
        base = df.loc[base_period] if base_period else df.iloc[0]
        cumul = (df / base - 1) * 100

        fig = go.Figure()
        fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#94a3b8")
        for i, col in enumerate(cols):
            fig.add_trace(go.Scatter(
                x=cumul.index, y=cumul[col], name=col, mode="lines",
                line=dict(color=self.palette[i % len(self.palette)], width=2),
                hovertemplate=f"<b>{col}</b><br>%{{x|%Y-%m}}: %{{y:.2f}}%<extra></extra>",
            ))
        fig.update_layout(**self._base_layout(title=title, yaxis_title="누적 변화율 (%)"))
        return fig
