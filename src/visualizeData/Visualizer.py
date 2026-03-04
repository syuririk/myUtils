from visualizeData.charts.bar_chart import BarChart
from visualizeData.charts.heatmap import HeatmapChart
from visualizeData.charts.dashboard import Dashboard
from visualizeData.charts.line_chart import LineChart


class Visualizer:
    """
    편리한 차트 접근을 위한 래퍼 클래스.

    Parameters
    ----------
    dataset : EconDataset
        시각화할 데이터셋.
    **kwargs
        공통 차트 생성자에 전달되는 옵션 (theme, palette, width, height 등).

    Attributes
    ----------
    bar : BarChart
    heatmap : HeatmapChart
    dashboard : Dashboard
    line : LineChart

    Methods
    -------
    overview(...)              # dashboard.overview 호출
    correlation_heatmap(...)   # heatmap.correlation_heatmap 호출
    yoy_bar(...)               # bar.yoy_bar 호출
    ...                        # 내부 차트에 정의된 모든 메서드 자동 프록시

    Examples
    --------
    >>> from visualizeData import Visualizer
    >>> vis = Visualizer(ds, theme='plotly_dark')
    >>> fig = vis.overview()                  # dashboard method
    >>> fig = vis.correlation_heatmap()       # heatmap method
    >>> fig = vis.yoy_bar('총지수')            # direct proxy to bar.yoy_bar
    >>> fig = vis.bar.yoy_bar('총지수')        # equivalent form
    """

    def __init__(self, dataset, **kwargs):


        self.dataset = dataset
        self.bar = BarChart(dataset, **kwargs)
        self.heatmap = HeatmapChart(dataset, **kwargs)
        self.dashboard = Dashboard(dataset, **kwargs)
        self.line = LineChart(dataset, **kwargs)

        self._charts = [self.bar, self.heatmap, self.dashboard, self.line]

        for chart in self._charts:
            for attr_name in dir(chart):
                if attr_name.startswith("_"):
                    continue
                if hasattr(self, attr_name):
                    continue
                attr = getattr(chart, attr_name)
                if callable(attr):
                    setattr(self, attr_name, attr)

    def __getattr__(self, name):
        for attr in ('bar', 'heatmap', 'dashboard', 'line'):
            if name == attr:
                return object.__getattribute__(self, attr)

        for chart in self._charts:
            if hasattr(chart, name):
                return getattr(chart, name)

        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

