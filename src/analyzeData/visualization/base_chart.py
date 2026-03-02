"""
visualization/base_chart.py
모든 차트 클래스의 공통 기반.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from typing import Optional, Tuple


class BaseChart:
    """
    공통 차트 설정 및 유틸리티.

    Parameters
    ----------
    figsize : (width, height)
    style : matplotlib style string
    palette : 컬러 리스트
    """

    DEFAULT_PALETTE = [
        "#2563EB", "#DC2626", "#16A34A", "#D97706",
        "#7C3AED", "#0891B2", "#DB2777", "#65A30D",
    ]

    def __init__(
        self,
        figsize: Tuple[int, int] = (12, 6),
        style: str = "seaborn-v0_8-whitegrid",
        palette: Optional[list] = None,
        dpi: int = 100,
    ):
        self.figsize = figsize
        self.style = style
        self.palette = palette or self.DEFAULT_PALETTE
        self.dpi = dpi

    def _setup_figure(self, nrows: int = 1, ncols: int = 1, **kwargs):
        plt.style.use(self.style)
        fig, axes = plt.subplots(nrows, ncols, figsize=self.figsize, dpi=self.dpi, **kwargs)
        return fig, axes

    def _apply_common(self, ax, title: str = "", xlabel: str = "", ylabel: str = ""):
        if title:
            ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=10)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=10)
        ax.tick_params(axis="x", rotation=30)
        ax.legend(fontsize=9, framealpha=0.8)

    def save(self, fig, path: str, **kwargs):
        fig.savefig(path, bbox_inches="tight", **kwargs)
        print(f"저장 완료: {path}")

    def show(self, fig):
        plt.tight_layout()
        plt.show()
