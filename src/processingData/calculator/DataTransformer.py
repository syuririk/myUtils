"""
processingData/DataTransformer.py
데이터 정규화 & 변환 — normalize, rebase, log_transform, diff, pct_change 등.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from typing import Optional

from core.econData.EconDataset import EconDataset


class DataTransformer:
    """
    데이터 정규화 및 변환 유틸리티.

    Examples
    --------
    >>> dt = DataTransformer(ds)
    >>> normalized = dt.normalize(method='minmax')
    >>> rebased = dt.rebase(base_period='2020-01')
    >>> log_data = dt.log_transform()
    >>> diff_data = dt.diff(periods=1)
    >>> pct = dt.pct_change(periods=4)
    """

    def __init__(self, dataset: EconDataset):
        self.dataset = dataset
        self._df = dataset.df

    def _check_columns(self, columns: Optional[list[str]]):
        """검증: 요청된 컬럼이 데이터프레임에 있는지 확인."""
        if columns is None:
            return list(self._df.columns)
        missing = [c for c in columns if c not in self._df.columns]
        if missing:
            raise KeyError(f"다음 컬럼을 찾을 수 없습니다: {missing}")
        return columns

    def normalize(
        self,
        method: str = "minmax",
        columns: Optional[list[str]] = None,
    ) -> pd.DataFrame:
        """
        정규화 메서드.
        method: 'minmax' | 'zscore' | 'base' (첫 시점=100)
        columns: 처리할 컬럼 목록. None이면 전체.
        """
        cols = self._check_columns(columns)
        sub = self._df[cols]

        if method == "minmax":
            res = (sub - sub.min()) / (sub.max() - sub.min())
            suffix = "minmax"
        elif method == "zscore":
            res = (sub - sub.mean()) / sub.std()
            suffix = "zscore"
        elif method == "base":
            res = sub / sub.iloc[0] * 100
            suffix = "base"
        else:
            raise ValueError(f"지원하지 않는 method: {method}")

        # write back to original dataset with suffixes
        for col in res.columns:
            new_col = f"{col}_{suffix}"
            self._df[new_col] = res[col].astype("float32")

        return res

    def rebase(
        self,
        base_period: str,
        columns: Optional[list[str]] = None,
    ) -> pd.DataFrame:
        """특정 시점을 100으로 환산.

        columns: 처리할 컬럼 목록. None이면 전체.
        """
        cols = self._check_columns(columns)
        sub = self._df[cols]
        res = sub / self._df.loc[base_period, cols] * 100
        # include base period in suffix to avoid overwriting
        safe_bp = str(base_period).replace("/", "_").replace("-", "_")
        for col in res.columns:
            new_col = f"{col}_rebase_{safe_bp}"
            self._df[new_col] = res[col].astype("float32")
        return res

    def log_transform(
        self,
        columns: Optional[list[str]] = None,
    ) -> pd.DataFrame:
        """로그 변환.

        columns: 처리할 컬럼 목록. None이면 전체.
        """
        cols = self._check_columns(columns)
        res = np.log(self._df[cols])
        for col in res.columns:
            new_col = f"{col}_log"
            self._df[new_col] = res[col].astype("float32")
        return res

    def diff(
        self,
        periods: int = 1,
        columns: Optional[list[str]] = None,
    ) -> pd.DataFrame:
        """차분.

        columns: 처리할 컬럼 목록. None이면 전체.
        """
        cols = self._check_columns(columns)
        res = self.dataset.diff(periods)[cols]
        for col in res.columns:
            new_col = f"{col}_diff{periods}"
            self._df[new_col] = res[col].astype("float32")
        return res

    def pct_change(
        self,
        periods: int = 1,
        columns: Optional[list[str]] = None,
    ) -> pd.DataFrame:
        """백분율 변화.

        columns: 처리할 컬럼 목록. None이면 전체.
        """
        cols = self._check_columns(columns)
        res = self.dataset.pct_change(periods)[cols] * 100
        for col in res.columns:
            new_col = f"{col}_pct{periods}"
            self._df[new_col] = res[col].astype("float32")
        return res
