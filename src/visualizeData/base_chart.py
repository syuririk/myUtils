"""
visualizeData/base_chart.py
모든 Plotly 차트 클래스의 공통 기반.
"""

from __future__ import annotations

import plotly.graph_objects as go
from typing import Optional


class BaseChart:
    """
    공통 Plotly 차트 설정 및 저장 유틸리티.

    Parameters
    ----------
    theme   : plotly 테마. 'plotly_white' | 'plotly_dark' | 'ggplot2' | 'seaborn'
    palette : 컬러 리스트 (hex)
    width   : 차트 너비 (px)
    height  : 차트 높이 (px)
    """

    DEFAULT_PALETTE = [
        "#2563EB", "#DC2626", "#16A34A", "#D97706",
        "#7C3AED", "#0891B2", "#DB2777", "#65A30D",
    ]

    def __init__(
        self,
        theme: str = "plotly_white",
        palette: Optional[list] = None,
        width: int = 1000,
        height: int = 500,
    ):
        self.theme   = theme
        self.palette = palette or self.DEFAULT_PALETTE
        self.width   = width
        self.height  = height

    def _base_layout(
        self,
        title: str = "",
        xaxis_title: str = "",
        yaxis_title: str = "",
    ) -> dict:
        """공통 레이아웃 딕셔너리 반환."""
        return dict(
            title=dict(text=title, font=dict(size=16, color="#1e293b"), x=0.02),
            xaxis=dict(title=xaxis_title, showgrid=True, gridcolor="#e2e8f0", zeroline=False),
            yaxis=dict(title=yaxis_title, showgrid=True, gridcolor="#e2e8f0", zeroline=False),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Arial, sans-serif", size=12, color="#334155"),
            legend=dict(
                orientation="h",
                yanchor="bottom", y=1.02,
                xanchor="left",  x=0,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#e2e8f0", borderwidth=1,
            ),
            width=self.width,
            height=self.height,
            hovermode="x unified",
            margin=dict(l=60, r=40, t=80, b=60),
            template=self.theme,
        )

    def show(self, fig: go.Figure):
        """차트를 브라우저에서 표시."""
        fig.show()

    def save_html(self, fig: go.Figure, path: str):
        """HTML 파일로 저장 (인터랙티브 유지)."""
        fig.write_html(path)
        print(f"저장 완료 (HTML): {path}")

    def save_image(self, fig: go.Figure, path: str, scale: int = 2):
        """정적 이미지로 저장 (PNG/SVG/PDF). kaleido 패키지 필요."""
        fig.write_image(path, scale=scale)
        print(f"저장 완료 (Image): {path}")
