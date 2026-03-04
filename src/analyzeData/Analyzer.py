from analyzeData.analysis.comparative import ComparativeAnalyzer
from analyzeData.analysis.descriptive import DescriptiveAnalyzer
from analyzeData.analysis.forecaster import Forecaster
from analyzeData.analysis.timeseries import TimeSeriesAnalyzer


class Analyzer:
    """
    편리한 분석기 접근을 위한 래퍼 클래스.

    Parameters
    ----------
    dataset : EconDataset
        분석할 데이터셋.

    Attributes
    ----------
    comparative : ComparativeAnalyzer
    descriptive : DescriptiveAnalyzer
    forecaster : Forecaster
    timeseries : TimeSeriesAnalyzer

    Methods
    -------
    lead_lag(...)             # comparative.lead_lag 호출
    summary(...)              # descriptive.summary 호출
    linear_trend(...)         # forecaster.linear_trend 호출
    decompose(...)            # timeseries.decompose 호출
    ...                       # 내부 분석기 메서드 자동 프록시

    Examples
    --------
    >>> from analyzeData import Analyzer
    >>> an = Analyzer(ds)
    >>> df = an.summary()
    >>> df = an.lead_lag('총지수','식료품')
    >>> res = an.linear_trend('총지수', steps=4)
    >>> res = an.decompose('총지수')
    """

    def __init__(self, dataset, **kwargs):
        self.dataset = dataset
        self.comparative = ComparativeAnalyzer(dataset)
        self.descriptive = DescriptiveAnalyzer(dataset)
        self.forecaster = Forecaster(dataset)
        self.timeseries = TimeSeriesAnalyzer(dataset)

        self._analyzers = [
            self.comparative,
            self.descriptive,
            self.forecaster,
            self.timeseries,
        ]

        # create direct proxies for each analyzer method so that
        # an.method() works without needing to reference sub-analyzer
        for ana in self._analyzers:
            for attr_name in dir(ana):
                if attr_name.startswith("_"):
                    continue
                if hasattr(self, attr_name):
                    continue
                attr = getattr(ana, attr_name)
                if callable(attr):
                    setattr(self, attr_name, attr)

    def __getattr__(self, name):
        # allow direct access to named analyzers
        for attr in ("comparative", "descriptive", "forecaster", "timeseries"):
            if name == attr:
                return object.__getattribute__(self, attr)

        # proxy individual methods
        for ana in self._analyzers:
            if hasattr(ana, name):
                return getattr(ana, name)

        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
