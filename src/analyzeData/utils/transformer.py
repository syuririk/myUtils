"""
utils/transformer.py
데이터 변환 유틸리티.
"""

from __future__ import annotations

import pandas as pd
import numpy as np


class DataTransformer:
    """정적 메서드 기반 데이터 변환 유틸리티."""

    @staticmethod
    def normalize(df: pd.DataFrame, method: str = "minmax") -> pd.DataFrame:
        """
        정규화.
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
        base = df.loc[base_period]
        return df / base * 100

    @staticmethod
    def log_transform(df: pd.DataFrame) -> pd.DataFrame:
        return np.log(df)

    @staticmethod
    def diff(df: pd.DataFrame, periods: int = 1) -> pd.DataFrame:
        return df.diff(periods)

    @staticmethod
    def pct_change(df: pd.DataFrame, periods: int = 1) -> pd.DataFrame:
        return df.pct_change(periods) * 100
