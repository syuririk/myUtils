from visualizeData.charts.bar_chart import BarChart
from visualizeData.charts.heatmap import HeatmapChart
from visualizeData.charts.dashboard import Dashboard
from visualizeData.charts.line_chart import LineChart
from visualizeData.charts.scatter_chart import ScatterChart


class Visualizer:
    """
    Parameters
    ----------
    dataset : EconDataset
    **kwargs
        options (theme, palette, width, height etc.).

    Attributes
    ----------
    bar : BarChart
    heatmap : HeatmapChart
    dashboard : Dashboard
    line : LineChart
    scatter : ScatterChart

    Methods
    -------
    overview(...)              # dashboard.overview 
    correlation_heatmap(...)   # heatmap.correlation_heatmap 

    Examples
    --------
    >>> from visualizeData import Visualizer
    >>> vis = Visualizer(ds, theme='plotly_dark')
    >>> fig = vis.overview()                  # dashboard method
    >>> fig = vis.correlation_heatmap()       # heatmap method
    >>> fig = vis.scatter.scatter('총지수','식료품')  # scatter method
    >>> fig = vis.correlation_scatter('총지수','식료품')
    >>> fig = vis.yoy_bar('총지수')            # direct proxy to bar.yoy_bar
    >>> fig = vis.bar.yoy_bar('총지수')        # equivalent form
    """

    def __init__(self, dataset, **kwargs):


        self.dataset = dataset
        self.bar = BarChart(dataset, **kwargs)
        self.heatmap = HeatmapChart(dataset, **kwargs)
        self.dashboard = Dashboard(dataset, **kwargs)
        self.line = LineChart(dataset, **kwargs)
        self.scatter = ScatterChart(dataset, **kwargs)

        self._charts = [self.bar, self.heatmap, self.dashboard, self.line, self.scatter]

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

