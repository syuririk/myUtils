"""
processingData/EconCalculator.py
데이터 계산 래퍼 — 정규화, 변환, 팩터 계산 통합 인터페이스.
"""

from __future__ import annotations

from processingData.calculator.DataTransformer import DataTransformer
from processingData.calculator.FactorComputer import FactorComputer


class EconCalculator:
    """
    편리한 계산 접근을 위한 래퍼 클래스.

    Parameters
    ----------
    dataset : EconDataset
        계산할 데이터셋.

    Attributes
    ----------
    transformer : DataTransformer
        정규화 & 변환 메서드
    factor_computer : FactorComputer
        팩터 계산 메서드

    Methods
    -------
    normalize(...)      # transformer.normalize 호출
    rebase(...)         # transformer.rebase 호출
    log_transform(...)  # transformer.log_transform 호출
    pct_change(...)     # transformer.pct_change 호출
    compute_factors(...) # factor_computer.compute_factors 호출
    ...                 # 내부 계산기 메서드 자동 프록시

    Examples
    --------
    >>> from processingData import EconCalculator
    >>> calc = EconCalculator(ds)
    >>> normalized = calc.normalize(method='minmax')
    >>> pct = calc.pct_change(periods=4)
    >>> ds = calc.compute_factors({...})
    """

    def __init__(self, dataset):
        self.dataset = dataset
        self.transformer = DataTransformer(dataset)
        self.factor_computer = FactorComputer(dataset)

        self._calculators = [self.transformer, self.factor_computer]

        # create direct proxies for each calculator method
        # so that calc.method() works without accessing sub-calculators first
        for calc in self._calculators:
            for attr_name in dir(calc):
                if attr_name.startswith("_"):
                    continue
                if hasattr(self, attr_name):
                    continue
                attr = getattr(calc, attr_name)
                if callable(attr):
                    setattr(self, attr_name, attr)

    def __getattr__(self, name):
        # allow direct access to named calculators
        for attr in ("transformer", "factor_computer"):
            if name == attr:
                return object.__getattribute__(self, attr)

        # proxy individual methods
        for calc in self._calculators:
            if hasattr(calc, name):
                return getattr(calc, name)

        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


