"""
core/transformer.py
데이터 변환 유틸리티 — EconDataset 내부에서 위임 호출된다.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from typing import Optional


class EconCalculator:

    def __init__(self, Dataset):
        self._Dataset = Dataset
        self._df = Dataset.df

    # ------------------------------------------------------------------
    # 기술 통계
    # ------------------------------------------------------------------


    @staticmethod
    def normalize(df: pd.DataFrame, method: str = "minmax") -> pd.DataFrame:
        """
        method: 'minmax' | 'zscore' | 'base' (첫 시점=100)
        """
        if method == "minmax":
            return (df - df.min()) / (df.max() - df.min())
        elif method == "zscore":
            return (df - df.mean()) / df.std()
        elif method == "base":
            return df / df.iloc[0] * 100
        else:
            raise ValueError(f"지원하지 않는 method: {method}")

    @staticmethod
    def rebase(df: pd.DataFrame, base_period: str) -> pd.DataFrame:
        """특정 시점을 100으로 환산."""
        return df / df.loc[base_period] * 100

    @staticmethod
    def log_transform(df: pd.DataFrame) -> pd.DataFrame:
        return np.log(df)

    @staticmethod
    def diff(df: pd.DataFrame, periods: int = 1) -> pd.DataFrame:
        return df.diff(periods)

    @staticmethod
    def pct_change(df: pd.DataFrame, periods: int = 1) -> pd.DataFrame:
        return df.pct_change(periods) * 100

    # ------------------------------------------------------------------
    # 팩터 계산
    # ------------------------------------------------------------------

    def computeFactors(self, factor_dict: dict, zscore: bool = True, date_col: str = "date"):
        """팩터를 계산하여 EconDataset._df에 추가.
        
        Parameters
        ----------
        factor_dict : dict
            {name: func} 형태. func는 EconDataset을 받아 Series 반환.
            예) lambda data: data['col1'] / data['col2']
        zscore : bool
            Z-score 표준화 여부
        date_col : str
            날짜 컬럼명
        
        Returns
        -------
        EconDataset
            팩터가 추가된 EconDataset
        
        Examples
        --------
        >>> factor_dict = {
        ...     'ratio_factor': lambda data: data['col1'] / data['col2'],
        ...     'diff_factor': lambda data: data['col1'] - data['col2'],
        ... }
        >>> ds.calculator.computeFactors(factor_dict)
        """
        from .EconStats import EconStats
        
        for i, (name, func) in enumerate(factor_dict.items(), 1):

            result = func(self._Dataset)
            self._df[name] = result.astype("float32")

            if zscore:
                zname = f"{name}_Z"
                self._df[zname] = self._csZscore(name, date_col=date_col).astype("float32")

        for col in self._df.columns:
            if col not in self._Dataset.stats:
                self._Dataset._stats[col] = EconStats(self._df[col])

        return self._Dataset

    def _csZscore(self, col: str, eps: float = 1e-8, date_col: str = "date") -> pd.Series:
        """cross-sectional Z-score 계산 헬퍼."""
        return self._df.groupby(date_col)[col].transform(
            lambda x: (x - x.mean()) / (x.std() + eps)
        )

    # def __repr__(self) -> str:
    #     return (
    #         f"Indicator('{self.name}', "
    #         f"{self._s.index.min().date()}~{self._s.index.max().date()}, "
    #         f"n={len(self._s)})"
    #     )


