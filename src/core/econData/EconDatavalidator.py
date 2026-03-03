"""
core/validator.py
EconDataset 로딩 시 자동 실행되는 데이터 유효성 검사기.
"""

from __future__ import annotations

import pandas as pd


class EconDataValidator:

    @staticmethod
    def validate(df: pd.DataFrame) -> None:
        DataValidator._check_index(df)
        DataValidator._check_numeric(df)
        DataValidator._warn_missing(df)
        DataValidator._warn_duplicates(df)

    @staticmethod
    def _check_index(df: pd.DataFrame) -> None:
        if not isinstance(df.index, pd.DatetimeIndex):
            raise TypeError("index 가 DatetimeIndex 여야 합니다.")

    @staticmethod
    def _check_numeric(df: pd.DataFrame) -> None:
        non_num = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
        if non_num:
            raise ValueError(f"수치형이 아닌 컬럼 발견: {non_num}")

    @staticmethod
    def _warn_missing(df: pd.DataFrame) -> None:
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if not missing.empty:
            print(f"[경고] 결측값 존재:\n{missing}")

    @staticmethod
    def _warn_duplicates(df: pd.DataFrame) -> None:
        dupes = df.index.duplicated().sum()
        if dupes:
            print(f"[경고] 중복 날짜 {dupes}개 발견.")
