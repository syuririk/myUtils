"""
example_usage.py
EconIndex 라이브러리 사용 예시.
"""

import pandas as pd
from econindex import (
    EconDataset,
    DescriptiveAnalyzer,
    TimeSeriesAnalyzer,
    ComparativeAnalyzer,
    Forecaster,
    LineChart,
    HeatmapChart,
)

# ── 1. 데이터 로딩 ─────────────────────────────────────────────────────
raw = {
    "date": pd.date_range("2016-01-01", periods=37, freq="QS"),
    "총지수": [95.422, 95.605, 95.785, 96.319, 97.521, 97.442, 97.910, 97.707, 98.571, 98.896, 99.424, 99.453, 99.105, 99.541, 99.469, 99.747, 100.060, 99.550, 100.190, 100.200, 101.490, 102.030, 102.730, 103.750, 105.460, 107.510, 108.730, 109.160, 110.310, 111.020, 112.140, 112.890, 113.630, 113.980, 114.440, 114.670, 116.030],
    "식료품및비주류음료": [89.932, 88.981, 89.982, 91.396, 94.129, 92.189, 94.126, 92.092, 94.612, 93.967, 97.533, 96.755, 95.913, 95.634, 95.349, 96.153, 97.290, 98.260, 101.910, 102.530, 104.970, 105.020, 106.270, 107.270, 109.510, 110.990, 114.540, 113.570, 115.910, 116.060, 120.100, 121.070, 123.460, 121.780, 123.080, 123.150, 126.280],
    "주류및담배": [97.256, 97.334, 97.304, 97.456, 98.426, 98.841, 99.032, 98.919, 99.073, 99.003, 99.093, 99.083, 99.067, 99.602, 99.995, 100.063, 100.070, 99.910, 100.010, 100.000, 100.080, 100.440, 100.660, 100.540, 101.540, 102.850, 103.050, 103.030, 103.190, 103.380, 103.470, 104.490, 104.390, 104.570, 104.590, 104.690, 104.670],
    "의류및신발": [96.512, 97.097, 97.027, 97.481, 97.662, 97.853, 98.174, 98.638, 98.924, 99.206, 99.133, 99.413, 99.216, 99.038, 99.124, 99.702, 99.730, 99.750, 100.260, 100.260, 100.230, 100.310, 100.380, 101.310, 102.180, 103.040, 103.660, 105.970, 107.580, 110.280, 111.650, 113.130, 113.630, 114.070, 114.420, 115.250, 115.730],
}
df = pd.DataFrame(raw)

ds = EconDataset(df, date_col="date", name="소비자물가지수")
print(ds)

# ── 2. 기술통계 ────────────────────────────────────────────────────────
da = DescriptiveAnalyzer(ds)

print("\n== 요약 ==")
print(da.summary())

print("\n== 최근 변화율 순위 ==")
print(da.rank_by_change())

print("\n== 2020~2022 vs 2022~2024 구간 비교 ==")
print(da.period_compare(("2020", "2022"), ("2022", "2024")))

# ── 3. 시계열 분석 ────────────────────────────────────────────────────
tsa = TimeSeriesAnalyzer(ds)

seasonal = tsa.seasonal_pattern("총지수")
print("\n== 총지수 계절 패턴 ==")
print(seasonal)

outliers = tsa.detect_outliers("식료품및비주류음료", method="iqr")
print(f"\n== 이상값 ({len(outliers)}개) ==")
print(outliers)

# ── 4. 비교 분석 ─────────────────────────────────────────────────────
ca = ComparativeAnalyzer(ds)

print("\n== 리드-래그 (총지수 vs 식료품) ==")
print(ca.lead_lag("총지수", "식료품및비주류음료"))

# ── 5. 예측 ──────────────────────────────────────────────────────────
fc = Forecaster(ds)
result = fc.linear_trend("총지수", steps=4)
print(f"\n== 총지수 선형 추세 예측 (4분기) ==")
print(result.forecast)

# ── 6. 시각화 ─────────────────────────────────────────────────────────
lc = LineChart(ds)
fig1 = lc.multi_line(title="소비자물가지수 추이")
fig1.savefig("output_multiline.png", bbox_inches="tight")

fig2 = lc.yoy_line()
fig2.savefig("output_yoy.png", bbox_inches="tight")

fig3 = lc.forecast_line("총지수", result)
fig3.savefig("output_forecast.png", bbox_inches="tight")

hm = HeatmapChart(ds)
fig4 = hm.correlation_heatmap()
fig4.savefig("output_corr_heatmap.png", bbox_inches="tight")

fig5 = hm.seasonal_heatmap("총지수")
fig5.savefig("output_seasonal_heatmap.png", bbox_inches="tight")

print("\n✅ 모든 차트 저장 완료!")
