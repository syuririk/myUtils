"""
core/dataset.py
경제지표 데이터셋의 핵심 관리 클래스.
모든 분석·시각화 클래스의 입력으로 사용된다.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Union, List, Optional, Dict

from .indicator import Indicator
from ..utils.validator import DataValidator
from ..utils.transformer import DataTransformer


class EconDataset:
    """
    경제지표 시계열 데이터셋 컨테이너.

    Parameters
    ----------
    df : pd.DataFrame
        - index 또는 'date' 컬럼에 날짜
        - 나머지 컬럼이 각각 경제지표
    date_col : str | None
        날짜 컬럼명. None이면 index를 날짜로 사용.
    freq : str
        pandas offset alias ('QS', 'MS', 'AS' 등). 미지정 시 자동 추론.

    Examples
    --------
    >>> ds = EconDataset(df, date_col='date')
    >>> ds.indicators          # ['총지수', '식료품', ...]
    >>> ds['총지수']           # Indicator 객체 반환
    >>> ds.slice('2020', '2022')  # 기간 필터
    """

    def __init__(
        self,
        df: pd.DataFrame,
        date_col: Optional[str] = None,
        freq: Optional[str] = None,
        name: str = "EconDataset",
    ):
        self.name = name
        self._raw = df.copy()
        self._df = self._prepare(df, date_col)
        self._freq = freq or pd.infer_freq(self._df.index) or "QS"

        # 검증
        DataValidator.validate(self._df)

        # 지표별 Indicator 객체 캐시
        self._indicators: Dict[str, Indicator] = {
            col: Indicator(col, self._df[col]) for col in self._df.columns
        }

    # ------------------------------------------------------------------
    # 내부 준비
    # ------------------------------------------------------------------

    def _prepare(self, df: pd.DataFrame, date_col: Optional[str]) -> pd.DataFrame:
        """날짜를 DatetimeIndex로 설정하고 numeric 컬럼만 유지."""
        out = df.copy()
        if date_col:
            out[date_col] = pd.to_datetime(out[date_col])
            out = out.set_index(date_col)
        elif not isinstance(out.index, pd.DatetimeIndex):
            out.index = pd.to_datetime(out.index)
        out = out.select_dtypes(include="number")
        out = out.sort_index()
        return out

    # ------------------------------------------------------------------
    # 프로퍼티
    # ------------------------------------------------------------------

    @property
    def df(self) -> pd.DataFrame:
        """정제된 DataFrame 반환 (read-only 의도)."""
        return self._df

    @property
    def indicators(self) -> List[str]:
        """지표명 목록."""
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

    # ------------------------------------------------------------------
    # 접근
    # ------------------------------------------------------------------

    def __getitem__(self, key: str) -> "Indicator":
        if key not in self._indicators:
            raise KeyError(f"'{key}' 지표를 찾을 수 없습니다. 가능한 지표: {self.indicators}")
        return self._indicators[key]

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
        new_ds = object.__new__(EconDataset)
        new_ds.name = self.name
        new_ds._raw = sub
        new_ds._df = sub
        new_ds._freq = self._freq
        new_ds._indicators = {col: Indicator(col, sub[col]) for col in sub.columns}
        return new_ds

    def select(self, indicators: List[str]) -> "EconDataset":
        """특정 지표만 선택한 새 EconDataset 반환."""
        return self.slice(indicators=indicators)

    # ------------------------------------------------------------------
    # 변환 (DataTransformer 위임)
    # ------------------------------------------------------------------

    def normalize(self, method: str = "minmax") -> "EconDataset":
        """정규화된 새 EconDataset 반환. method: 'minmax' | 'zscore' | 'base'"""
        normed = DataTransformer.normalize(self._df, method=method)
        return self._clone_with(normed)

    def rebase(self, base_period: str) -> "EconDataset":
        """특정 시점을 100으로 환산한 새 EconDataset 반환."""
        rebased = DataTransformer.rebase(self._df, base_period)
        return self._clone_with(rebased)

    def pct_change(self, periods: int = 1) -> "EconDataset":
        """변화율(%) DataFrame을 담은 새 EconDataset 반환."""
        changed = self._df.pct_change(periods=periods) * 100
        return self._clone_with(changed.dropna())

    def rolling(self, window: int, func: str = "mean") -> "EconDataset":
        """이동 통계량 (mean | std | sum) 새 EconDataset 반환."""
        r = getattr(self._df.rolling(window), func)()
        return self._clone_with(r.dropna())

    # ------------------------------------------------------------------
    # 클래스메서드 — 팩토리
    # ------------------------------------------------------------------

    @classmethod
    def from_csv(cls, path: Union[str, Path], date_col: str = "date", **kwargs) -> "EconDataset":
        df = pd.read_csv(path, **kwargs)
        return cls(df, date_col=date_col)

    @classmethod
    def from_excel(cls, path: Union[str, Path], date_col: str = "date", **kwargs) -> "EconDataset":
        df = pd.read_excel(path, **kwargs)
        return cls(df, date_col=date_col)

    # ------------------------------------------------------------------
    # 내부 헬퍼
    # ------------------------------------------------------------------

    def _clone_with(self, new_df: pd.DataFrame) -> "EconDataset":
        new_ds = object.__new__(EconDataset)
        new_ds.name = self.name
        new_ds._raw = new_df
        new_ds._df = new_df
        new_ds._freq = self._freq
        new_ds._indicators = {col: Indicator(col, new_df[col]) for col in new_df.columns}
        return new_ds
