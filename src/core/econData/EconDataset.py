"""
core/dataset.py
경제지표 데이터셋 핵심 컨테이너.
모든 analyzeData · visualizeData 클래스의 입력으로 사용된다.
"""

from __future__ import annotations

import pandas as pd
import numpy as np   
from pathlib import Path
from typing import Union, List, Optional, Dict

from .EconDatavalidator import EconDataValidator
from .EconStats import EconStats
from .EconCalculator import EconCalculator

class EconDataset:
    """
    경제지표 시계열 데이터셋 컨테이너.

    Parameters
    ----------
    df : pd.DataFrame
        - index 또는 date_col 컬럼에 날짜
        - 나머지 컬럼이 각각 경제지표 (수치형)
    date_col : str | None
        날짜 컬럼명. None 이면 index 를 날짜로 사용.
    freq : str | None
        pandas offset alias ('QS', 'MS', 'AS' 등). 미지정 시 자동 추론.
    name : str
        데이터셋 식별 이름.

    Examples
    --------
    >>> ds = EconDataset(df, date_col='date', name='소비자물가지수')
    >>> ds.indicators               # ['총지수', '식료품', ...]
    >>> ds['총지수']                # EconCalculator 객체 반환
    >>> ds.slice('2020', '2022')   # 기간 필터 → 새 EconDataset
    >>> ds.normalize('minmax')     # 정규화 → 새 EconDataset
    """

    def __init__(
        self,
        df: pd.DataFrame,
        name: str = "EconDataset",
        date_col: Optional[str] = 'date',
        freq: Optional[str] = None
    ):
        self.name = name
        self._raw = df.copy()
        self._df = self._prepare(df, date_col)
        self._freq = freq or pd.infer_freq(self._df.index) or "QS"

        EconDataValidator.validate(self._df)

        self._stats: Dict[str, EconStats] = {
            col: EconStats(self._df[col]) for col in self._df.columns
        }

        self._calculator = EconCalculator(self)
    # ------------------------------------------------------------------
    # 내부 준비
    # ------------------------------------------------------------------

    def _prepare(self, df: pd.DataFrame, date_col: Optional[str]) -> pd.DataFrame:
        out = df.copy()
        if date_col:
            out[date_col] = pd.to_datetime(out[date_col])
            out = out.set_index(date_col)
        elif not isinstance(out.index, pd.DatetimeIndex):
            out.index = pd.to_datetime(out.index)
        out = out.select_dtypes(include="number")
        return out.sort_index()

    # ------------------------------------------------------------------
    # 프로퍼티
    # ------------------------------------------------------------------

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    @property
    def indicators(self) -> List[str]: 
        return list(self._df.columns)

    @property
    def freq(self) -> str:
        return self._freq

    @property
    def start(self) -> pd.Timestamp:
        return self._df.index.min()

    @property
    def end(self) -> pd.Timestamp:
        return self._df.index.max()

    @property
    def shape(self):
        return self._df.shape

    @property
    def calculator(self) -> EconCalculator:
        return self._calculator

    @property
    def stats(self) -> Dict[str, EconStats]:
        return self._stats

    # ------------------------------------------------------------------
    # 접근
    # ------------------------------------------------------------------

    def __getitem__(self, key: str) -> pd.Series:
        if key not in self._df.columns:
            raise KeyError(f"'{key}' 지표 없음. 가능한 지표: {self.indicators}")
        return self._df[key]

    def __repr__(self) -> str:
        return (
            f"EconDataset(name='{self.name}', "
            f"기간={self.start.date()}~{self.end.date()}, "
            f"지표수={len(self.indicators)}, freq='{self.freq}')"
        )

    # ------------------------------------------------------------------
    # 필터링
    # ------------------------------------------------------------------

    def slice(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        indicators: Optional[List[str]] = None,
    ) -> "EconDataset":
        """기간 및 지표를 필터링한 새 EconDataset 반환."""
        sub = self._df.loc[start:end]
        if indicators:
            sub = sub[indicators]
        return self._clone_with(sub)

    def select(self, indicators: List[str]) -> "EconDataset":
        """특정 지표만 선택한 새 EconDataset 반환."""
        return self._clone_with(self._df[indicators])


    # ------------------------------------------------------------------
    # 팩토리
    # ------------------------------------------------------------------

    @classmethod
    def from_csv(cls, path: Union[str, Path], date_col: str = "date", **kwargs) -> "EconDataset":
        return cls(pd.read_csv(path, **kwargs), date_col=date_col)

    @classmethod
    def from_excel(cls, path: Union[str, Path], date_col: str = "date", **kwargs) -> "EconDataset":
        return cls(pd.read_excel(path, **kwargs), date_col=date_col)

    # ------------------------------------------------------------------
    # 내부 헬퍼
    # ------------------------------------------------------------------

    def _clone_with(self, new_df: pd.DataFrame) -> "EconDataset":
        new_ds = object.__new__(EconDataset)
        new_ds.name = self.name
        new_ds._raw = new_df
        new_ds._df = new_df
        new_ds._freq = self._freq
        new_ds._stats = {col: EconStats(new_df[col]) for col in new_df.columns}
        new_ds._calculator = EconCalculator(new_ds)
        return new_ds
