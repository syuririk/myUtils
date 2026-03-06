"""
core/dataset.py
경제지표 데이터셋 핵심 컨테이너.
모든 analyzeData · visualizeData 클래스의 입력으로 사용된다.
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path
from typing import Union, List, Optional, Dict

from .EconDatavalidator import EconDataValidator
from .EconStats import EconStats

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
    >>> ds = EconDataset(df, date_col='date')
    >>> ds.indicators               # ['총지수', '식료품', ...]
    >>> ds['총지수']                # EconCalculator 객체 반환
    >>> ds.slice('2020', '2022')   # 기간 필터 → 새 EconDataset
    >>> ds.normalize('minmax')     # 정규화 → 새 EconDataset
    """

    def __init__(
        self,
        df: pd.DataFrame,
        date_col: Optional[str] = 'date',
    ):
        # 기본적인 데이터 준비만 수행
        self._raw = df.copy()
        self._df = self._prepare(df, date_col)
        self._df_full = self._df.copy().reindex(
            pd.date_range(self._df.index.min(), self._df.index.max())
        )

        EconDataValidator.validate(self._df)

        self._stats = {col: EconStats(self._df[[col]]) for col in self._df.columns}
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
        out = out.apply(pd.to_numeric, errors='coerce')
        out = out.select_dtypes(include="number")
        out = out.dropna(axis=0, how='all')
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
    def start(self) -> pd.Timestamp:
        return self._df.index.min()

    @property
    def end(self) -> pd.Timestamp:
        return self._df.index.max()

    @property
    def shape(self):
        return self._df.shape
    
    @property
    def stats(self) -> Dict[str, EconStats]:
        return self._stats

    # ------------------------------------------------------------------
    # 접근
    # ------------------------------------------------------------------

    def __getitem__(self, key: Union[str, list]) -> pd.Series:
        if isinstance(key, list):
            missing = [k for k in key if k not in self._df.columns]
            dfs = [self._df[k] for k in key]
            if missing:
                raise KeyError(f"'{missing}' 지표 없음. 가능한 지표: {self.indicators}")
            return pd.concat(dfs, axis=1)
        
        if key not in self._df.columns:
            raise KeyError(f"'{key}' 지표 없음. 가능한 지표: {self.indicators}")
        return self._df[key]

    def __repr__(self) -> str:
        pd.set_option('display.expand_frame_repr', False)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        return self._df.__repr__()

    # ------------------------------------------------------------------
    # 연산자 오버로딩
    # ------------------------------------------------------------------

    def __add__(self, other: Union["EconDataset", pd.DataFrame]) -> "EconDataset":
        """+ 연산자: 데이터셋 병합 (pd.concat axis=1)."""
        if isinstance(other, EconDataset):
            merged_df = pd.concat([self._df, other._df], axis=1)
        elif isinstance(other, pd.DataFrame):
            merged_df = pd.concat([self._df, other], axis=1)
        else:
            return NotImplemented
        
        return self._clone_with(merged_df)
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
    # 변화율 계산
    # ------------------------------------------------------------------

    def pct_change(self, periods: int = 1) -> pd.DataFrame:
        """기간별 백분율 변화율 계산. self._df_full을 기준으로 계산 후 self._df 인덱스로 필터."""
        pct = self._df_full.pct_change(periods)
        return pct.loc[self._df.index]

    def diff(self, periods: int = 1) -> pd.DataFrame:
        """기간별 차이 계산. self._df_full을 기준으로 계산 후 self._df 인덱스로 필터."""
        diff = self._df_full.diff(periods)
        return diff.loc[self._df.index]

    def rolling_std(self, window: int, offset: int = 1) -> pd.DataFrame:
        """롤링 표준편차 계산. offset일 차이를 기준으로 window일 롤링. self._df_full 기준 계산 후 필터."""
        diff = self._df_full.diff(offset)
        rolling_std = diff.rolling(window).std()
        return rolling_std.loc[self._df.index]

    def mom(self) -> pd.DataFrame:
        """Month-over-month 변화율 (%). _df_full 기준으로 30일 전 대비."""
        return self.pct_change(30) * 100

    def qoq(self) -> pd.DataFrame:
        """Quarter-over-quarter 변화율 (%). _df_full 기준으로 90일 전 대비."""
        return self.pct_change(90) * 100

    def yoy(self) -> pd.DataFrame:
        """Year-over-year 변화율 (%). _df_full 기준으로 365일 전 대비."""
        return self.pct_change(365) * 100

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
        new_ds._raw = new_df
        new_ds._df = new_df
        new_ds._df_full = new_df.copy().reindex(
            pd.date_range(new_df.index.min(), new_df.index.max())
        )
        new_ds._stats = {col: EconStats(new_df[col]) for col in new_df.columns}
        return new_ds
