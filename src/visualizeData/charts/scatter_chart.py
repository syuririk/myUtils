"""
visualizeData/scatter_chart.py
Plotly 기반 산포도 함수 집합 — 두 지표 간 산점도, 산점도 매트릭스, 상관계수 표시.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Optional

from visualizeData.charts.base_chart import BaseChart
from core.econData.EconDataset import EconDataset


class ScatterChart(BaseChart):
    """산포도 관련 그래프를 그리는 클래스.

    Methods
    -------
    scatter(x, y, color=None, title=None, add_trend=False)
        두 지표 간 산점도. 색상 변수를 지정할 수 있고, 선형 추세선 추가 가능.
    correlation_scatter(indicator_a, indicator_b, title=None, add_trend=True)
        두 지표 간 상관계수를 제목에 포함한 산점도.
    scatter_matrix(indicators=None, title="지표 산점도 매트릭스")
        여러 지표에 대한 페어와이즈 산점도 행렬.
    """

    def __init__(self, dataset: EconDataset, **kwargs):
        super().__init__(**kwargs)
        self.dataset = dataset
        self._df = dataset.df

    # ------------------------------------------------------------------
    # 단일 산점도
    # ------------------------------------------------------------------

    def scatter(
        self,
        x: str,
        y: str,
        color: Optional[str] = None,
        title: Optional[str] = None,
        add_trend: bool = False,
    ) -> go.Figure:
        """지정한 두 지표의 산점도.

        Parameters
        ----------
        x : str
            x축 사용할 지표명
        y : str
            y축 사용할 지표명
        color : Optional[str]
            컬러바에 사용할 추가 지표명 (값이 있으면 연속형 컬러바가 추가됨)
        title : Optional[str]
            그래프 제목
        add_trend : bool
            True면 최소제곱 선형회귀 추세선을 함께 그림
        """
        df = self._df[[x, y] + ([color] if color else [])].dropna()
        fig = go.Figure()
        marker_kwargs = {}
        if color:
            marker_kwargs = dict(
                color=df[color], colorscale="Viridis", showscale=True,
                colorbar=dict(title=color), size=6,
            )
        else:
            marker_kwargs = dict(color=self.palette[0], size=6)

        fig.add_trace(go.Scatter(
            x=df[x], y=df[y], mode="markers", marker=marker_kwargs,
            hovertemplate=f"<b>%{{text}}</b><br>{x}: %{{x:.2f}}<br>{y}: %{{y:.2f}}<extra></extra>",
            text=df.index.strftime("%Y-%m"),
        ))

        if add_trend and len(df) >= 2:
            # linear fit
            a, b = np.polyfit(df[x], df[y], 1)
            xs = np.array([df[x].min(), df[x].max()])
            ys = a * xs + b
            fig.add_trace(go.Scatter(
                x=xs, y=ys, mode="lines",
                line=dict(color=self.palette[1], dash="dash"),
                name="trend",
                hoverinfo="skip",
            ))

        corr = df[x].corr(df[y])
        t = title or f"{x} vs {y}"
        fig.update_layout(
            **self._base_layout(title=f"{t} (corr={corr:.2f})"),
            xaxis_title=x,
            yaxis_title=y,
        )
        return fig

    # ------------------------------------------------------------------
    # 상관계수가 제목에 들어간 산점도
    # ------------------------------------------------------------------

    def correlation_scatter(
        self,
        indicator_a: str,
        indicator_b: str,
        title: Optional[str] = None,
        add_trend: bool = True,
    ) -> go.Figure:
        """두 지표 간 산점도이며 상관계수를 제목에 포함.

        이 함수는 내부적으로 ``scatter``를 호출한다.
        """
        return self.scatter(
            x=indicator_a,
            y=indicator_b,
            title=title,
            add_trend=add_trend,
        )

    # ------------------------------------------------------------------
    # 산점도 매트릭스
    # ------------------------------------------------------------------

    def scatter_matrix(
        self,
        indicators: Optional[List[str]] = None,
        title: str = "지표 산점도 매트릭스",
    ) -> go.Figure:
        """여러 지표에 대한 페어와이즈 산점도 행렬.

        빈 값은 dropna 처리된다.
        """
        cols = indicators or self.dataset.indicators
        df = self._df[cols].dropna()
        fig = px.scatter_matrix(df, dimensions=cols, title=title, template=self.theme)
        fig.update_layout(width=self.width, height=self.height)
        return fig
