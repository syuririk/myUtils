"""
utils/validator.py
데이터 유효성 검사.
"""

from __future__ import annotations

import pandas as pd
import numpy as np


class DataValidator:
    """EconDataset 로딩 시 자동으로 실행되는 검증기."""

    @staticmethod
    def validate(df: pd.DataFrame) -> None:
        DataValidator._check_index(df)
        DataValidator._check_numeric(df)
        DataValidator._warn_missing(df)
        DataValidator._warn_duplicates(df)

    @staticmethod
    def _check_index(df: pd.DataFrame):
        if not isinstance(df.index, pd.DatetimeIndex):
            raise TypeError("index가 DatetimeIndex 여야 합니다.")

    @staticmethod
    def _check_numeric(df: pd.DataFrame):
        non_num = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
        if non_num:
            raise ValueError(f"수치형이 아닌 컬럼 발견: {non_num}")

    @staticmethod
    def _warn_missing(df: pd.DataFrame):
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if not missing.empty:
            print(f"[경고] 결측값 존재:\n{missing}")

    @staticmethod
    def _warn_duplicates(df: pd.DataFrame):
        dupes = df.index.duplicated().sum()
        if dupes > 0:
            print(f"[경고] 중복 날짜 {dupes}개 발견. 마지막 값 유지 권장.")
