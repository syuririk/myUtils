"""
processingData/FactorComputer.py
팩터 계산 — computeFactors, cross-sectional Z-score 등.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from typing import Optional, Callable, Dict

from core.econData.EconDataset import EconDataset


class FactorComputer:
    """
    경제지표 팩터 계산기.

    Examples
    --------
    >>> fc = FactorComputer(ds)
    >>> factor_dict = {
    ...     'ratio_factor': lambda data: data['col1'] / data['col2'],
    ...     'diff_factor': lambda data: data['col1'] - data['col2'],
    ... }
    >>> ds = fc.compute_factors(factor_dict, zscore=True)
    """

    def __init__(self, dataset: EconDataset):
        self.dataset = dataset
        self._df = dataset.df

    def compute_factors(
        self,
        factor_dict: Dict[str, Callable],
        zscore: bool = True,
        zscore_method: str = "rolling",  # 'rolling' or 'cross'
        rolling_window: int = 4,
        date_col: str = "date",
    ) -> EconDataset:
        """팩터를 계산하여 EconDataset._df에 추가.
        
        Parameters
        ----------
        factor_dict : dict
            {name: func} 형태. func는 EconDataset을 받아 Series 반환.
            예) lambda data: data['col1'] / data['col2']
        zscore : bool
            Z-score 표준화 여부 (기본 True; 기본 방식은 ``rolling``)
        zscore_method : str
            'rolling' 또는 'cross' 중 하나. ``rolling``은 이동 윈도우
            (default window=4)로 마지막 값의 zscore를 계산하고,
            ``cross``는 동일 날짜별 횡단면 zscore.
        rolling_window : int
            ``rolling`` 방식을 사용할 때의 창 크기.
        date_col : str
            날짜 컬럼명 (횡단면 계산에 사용)
        
        Returns
        -------
        EconDataset
            팩터가 추가된 EconDataset
        """
        from core.econData.EconStats import EconStats
        
        for name, func in factor_dict.items():
            result = func(self.dataset)
            self._df[name] = result.astype("float32")

            if zscore:
                zname = f"{name}_Z"
                if zscore_method == "cross":
                    self._df[zname] = self._cs_zscore(name, date_col=date_col).astype("float32")
                elif zscore_method == "rolling":
                    self._df[zname] = self._rolling_zscore(name, window=rolling_window).astype("float32")
                else:
                    raise ValueError(f"지원하지 않는 zscore_method: {zscore_method}")

        for col in self._df.columns:
            if col not in self.dataset.stats:
                self.dataset._stats[col] = EconStats(self._df[col])

        return self.dataset

    def _cs_zscore(
        self,
        col: str,
        eps: float = 1e-8,
        date_col: str = "date",
    ) -> pd.Series:
        """cross-sectional Z-score 계산 헬퍼."""
        return self._df.groupby(date_col)[col].transform(
            lambda x: (x - x.mean()) / (x.std() + eps)
        )

    def _rolling_zscore(
        self,
        col: str,
        window: int = 4,
        eps: float = 1e-8,
    ) -> pd.Series:
        """이전 `window`개 값 기반 이동 Z-score 계산.

        각 위치에서 해당 윈도우 전체에 대한 zscore를 마지막 값 기준으로 반환한다.
        """
        s = self._df[col]
        def score(x):
            mu = x.mean()
            sigma = x.std() + eps
            return (x.iloc[-1] - mu) / sigma
        return s.rolling(window).apply(score, raw=False)
