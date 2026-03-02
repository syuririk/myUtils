# myUtils

# TODO
fred

ecos

krx

dart

sec



# queue
fred - parseTime

ecos

krx - lazy

process

analize

visualize



# DataFrame

경제지표 시계열 데이터를 위한 Python 분석·시각화 라이브러리.

---

## 📁 프로젝트 구조

```
DataFrame/
├── __init__.py                  # analyzeData, visualizeData 노출
├── core/                        # 내부 공통 기반 (외부 직접 접근 불필요)
│   ├── dataset.py               # EconDataset — 데이터 컨테이너
│   ├── indicator.py             # Indicator   — 단일 지표 래퍼
│   ├── transformer.py           # DataTransformer — 정규화·변환
│   └── validator.py             # DataValidator   — 로딩 시 자동 검증
├── analyzeData/                 # 분석 레이어
│   ├── descriptive.py           # DescriptiveAnalyzer
│   ├── timeseries.py            # TimeSeriesAnalyzer
│   ├── comparative.py           # ComparativeAnalyzer
│   └── forecaster.py            # Forecaster
└── visualizeData/               # 시각화 레이어 (Plotly)
    ├── base_chart.py            # BaseChart — 공통 레이아웃
    ├── line_chart.py            # LineChart
    ├── heatmap.py               # HeatmapChart
    ├── bar_chart.py             # BarChart
    └── dashboard.py             # Dashboard
```

---

## ⚙️ 설치

```bash
pip install pandas numpy scipy plotly statsmodels
```

> `arima()` 예측 메서드는 `statsmodels` 가 필요합니다.  
> 정적 이미지 저장(`save_image`)은 추가로 `kaleido` 가 필요합니다.

---

## 🚀 빠른 시작

```python
import pandas as pd
from DataFrame.core.dataset import EconDataset
from DataFrame.analyzeData.descriptive import DescriptiveAnalyzer
from DataFrame.visualizeData.line_chart import LineChart

# 데이터 로딩
df = pd.read_csv("cpi.csv")
ds = EconDataset(df, date_col="date", name="소비자물가지수")

# 분석
da = DescriptiveAnalyzer(ds)
print(da.summary())

# 시각화
lc = LineChart(ds)
fig = lc.multi_line()
fig.show()
```

### 패키지 수준 import

```python
from DataFrame import analyzeData, visualizeData

# 서브패키지 모듈 직접 접근
from DataFrame.analyzeData.descriptive import DescriptiveAnalyzer
from DataFrame.visualizeData.dashboard import Dashboard
```

---

## 📦 데이터 포맷

모든 클래스는 아래 형태의 `pd.DataFrame` 을 입력으로 받습니다.

| date       | 총지수  | 식료품및비주류음료 | 주류및담배 | … |
|------------|--------|---------------|---------|---|
| 2016-01-01 | 95.422 | 89.932        | 97.256  | … |
| 2016-04-01 | 95.605 | 88.981        | 97.334  | … |

- **index 또는 별도 컬럼**으로 날짜를 가집니다.
- 나머지 컬럼은 모두 **수치형** 경제지표입니다.
- 분기(`QS`), 월(`MS`), 연(`AS`) 등 다양한 주기를 지원합니다.

---

## 🔧 core

> `core` 는 `analyzeData` / `visualizeData` 내부에서만 사용하는 기반 레이어입니다.  
> 필요 시 직접 import 해서 사용할 수도 있습니다.

### EconDataset

```python
from DataFrame.core.dataset import EconDataset

ds = EconDataset(df, date_col="date", name="소비자물가지수")

# 프로퍼티
ds.indicators   # ['총지수', '식료품및비주류음료', ...]
ds.freq         # 'QS-OCT'
ds.start        # Timestamp('2016-01-01')
ds.end          # Timestamp('2025-01-01')
ds.shape        # (37, 5)
ds.df           # 정제된 DataFrame

# 지표 접근
ind = ds["총지수"]   # Indicator 객체 반환

# 필터링 (새 EconDataset 반환)
ds.slice("2020", "2022")
ds.select(["총지수", "식료품및비주류음료"])

# 변환 (새 EconDataset 반환, 원본 불변)
ds.normalize("minmax")    # min-max 정규화
ds.normalize("zscore")    # z-score 정규화
ds.normalize("base")      # 첫 시점 = 100
ds.rebase("2020-01-01")   # 특정 시점 = 100
ds.pct_change(4)          # 전년 동기 대비 변화율
ds.rolling(4, "mean")     # 4기 이동평균

# 파일 로딩
EconDataset.from_csv("path/to/file.csv", date_col="date")
EconDataset.from_excel("path/to/file.xlsx", date_col="date")
```

### Indicator

```python
ind = ds["총지수"]

ind.series          # pd.Series
ind.values          # np.ndarray
ind.index           # DatetimeIndex

# 변화율
ind.yoy(periods=4)               # 전년 동기 대비 변화율 (%)
ind.qoq()                        # 전분기 대비 변화율 (%)
ind.cumulative_change("2020")    # 기준 시점 대비 누적 변화율 (%)

# 이동 통계
ind.ma(4)              # 단순 이동평균
ind.ema(span=4)        # 지수 이동평균
ind.rolling_std(4)     # 이동 표준편차

# 기술 통계
ind.summary()          # dict (mean, std, min, max, latest, yoy_latest)
ind.outliers(threshold=2.0)   # Z-score 기준 이상값 Series
```

---

## 📊 analyzeData

### DescriptiveAnalyzer — 기술통계

```python
from DataFrame.analyzeData.descriptive import DescriptiveAnalyzer

da = DescriptiveAnalyzer(ds)

da.summary()                                      # 전체 지표 요약 DataFrame
da.describe()                                     # skewness, kurtosis 포함 확장 describe
da.yoy_table(periods=4)                           # 전년 동기 대비 변화율 테이블
da.qoq_table()                                    # 전분기 대비 변화율 테이블
da.cumulative_table(base_period="2020-01-01")     # 누적 변화율 테이블
da.correlation(method="pearson")                  # 상관계수 행렬
da.correlation_with_target("총지수", lag=0)       # 특정 지표와의 상관계수
da.rank_by_change(periods=4)                      # 최근 YoY 기준 순위
da.contribution(weights={"총지수": 0.4, ...})     # 가중치 기반 기여도
da.period_compare(("2020","2022"), ("2022","2024"), stat="mean")  # 구간 비교
```

### TimeSeriesAnalyzer — 시계열 분석

```python
from DataFrame.analyzeData.timeseries import TimeSeriesAnalyzer

tsa = TimeSeriesAnalyzer(ds)

# 추세 분해 → DecompositionResult (observed, trend, seasonal, residual)
result = tsa.decompose("총지수", model="additive", period=4)
result.strength_trend      # 추세 강도 (0~1)
result.strength_seasonal   # 계절성 강도 (0~1)

tsa.decompose_all()        # 전체 지표 일괄 분해

# 이상값 탐지
tsa.detect_outliers("총지수", method="zscore", threshold=2.5)
tsa.detect_outliers("총지수", method="iqr")
tsa.detect_outliers("총지수", method="rolling_zscore")

# 변곡점·계절성·변동성
tsa.changepoints("총지수", window=4, threshold_std=1.5)
tsa.seasonal_pattern("총지수")       # 분기별 mean, std, min, max
tsa.seasonal_adjustment("총지수")    # 계절 조정 시계열 (trend + residual)
tsa.rolling_volatility("총지수", window=4)
tsa.volatility_table(window=4)
```

### ComparativeAnalyzer — 비교 분석

```python
from DataFrame.analyzeData.comparative import ComparativeAnalyzer

ca = ComparativeAnalyzer(ds)

ca.normalized_comparison("minmax")                        # 정규화 후 비교
ca.lead_lag("총지수", "식료품및비주류음료", max_lag=4)   # 리드-래그 상관계수
ca.relative_performance(base_period="2020-01-01")         # 기준 시점 대비 상대 성과 (%)
ca.dispersion()                                           # 시점별 지표 간 std, range, cv
ca.rolling_correlation("총지수", "식료품및비주류음료", window=4)
ca.pairwise_correlation_matrix(period=("2020","2024"), method="pearson")
```

### Forecaster — 단기 예측

```python
from DataFrame.analyzeData.forecaster import Forecaster

fc = Forecaster(ds)

# 선형 추세 연장 → ForecastResult (forecast, lower, upper, method, confidence)
res = fc.linear_trend("총지수", steps=4, window=None, confidence=0.95)

# 이동평균 수평 연장
res = fc.ma_extension("총지수", window=4, steps=4)

# ARIMA (statsmodels 필요)
res = fc.arima("총지수", steps=4, order=(1,1,1), confidence=0.95)

# ForecastResult 속성
res.forecast    # 예측 Series
res.lower       # 신뢰 하한 Series
res.upper       # 신뢰 상한 Series
res.method      # 'linear_trend' | 'ma_extension' | 'arima'
res.confidence  # 0.95
```

---

## 📈 visualizeData

모든 차트는 `plotly.graph_objects.Figure` 를 반환합니다.

```python
fig.show()                    # 브라우저에서 인터랙티브 확인
chart.save_html(fig, "out.html")    # HTML 파일 저장 (인터랙티브 유지)
chart.save_image(fig, "out.png")   # 정적 이미지 저장 (kaleido 필요)
```

공통 생성자 옵션:

```python
LineChart(ds, theme="plotly_white", palette=["#2563EB", ...], width=1000, height=500)
```

---

### LineChart

```python
from DataFrame.visualizeData.line_chart import LineChart

lc = LineChart(ds)

lc.multi_line(indicators=None, normalize=False, ma_window=4)
lc.yoy_line(indicators=None, periods=4)
lc.qoq_line(indicators=None)
lc.forecast_line("총지수", forecast_result)
lc.decomposition_plot(decomp_result)          # 4분할 (관측·추세·계절성·잔차)
lc.cumulative_line(indicators=None, base_period="2020-01-01")
```

### HeatmapChart

```python
from DataFrame.visualizeData.heatmap import HeatmapChart

hm = HeatmapChart(ds)

hm.correlation_heatmap(method="pearson")
hm.seasonal_heatmap("총지수")               # 연도 × 분기 YoY 히트맵
hm.yoy_heatmap(periods=4)                   # 시점 × 지표 YoY 히트맵
hm.rolling_corr_heatmap("총지수", "식료품및비주류음료", windows=[2,3,4,6,8])
```

### BarChart

```python
from DataFrame.visualizeData.bar_chart import BarChart

bc = BarChart(ds)

bc.yoy_bar("총지수", periods=4)
bc.grouped_bar(indicators=None, periods=4)
bc.period_compare_bar(("2020","2022"), ("2022","2024"), stat="mean")
bc.contribution_bar(weights=None, periods=4)   # 기여도 스택 바
bc.rank_bar(periods=4)                         # 최신 YoY 순위 가로 바
```

### Dashboard

```python
from DataFrame.visualizeData.dashboard import Dashboard

db = Dashboard(ds)

db.overview(indicators=None)                            # 레벨·YoY·변동성 3행
db.compare_panel("총지수", "식료품및비주류음료")         # 2×2 상세 비교
db.lead_lag_panel("총지수", "식료품및비주류음료", max_lag=4)  # YoY + 리드-래그 바
```

---

## 🧪 실행 확인

```bash
# DataFrame 폴더의 상위 디렉토리에서 실행
python DataFrame/run_test.py
```

각 클래스·메서드별로 `[OK]` / `[FAIL]` 결과를 출력합니다.

---

## 🔑 설계 원칙

| 원칙 | 내용 |
|------|------|
| **단일 진입점** | 모든 분석·시각화 클래스가 `EconDataset` 하나를 입력으로 받음 |
| **불변성** | `slice`, `normalize` 등 변환 메서드는 항상 **새 EconDataset** 반환, 원본 보존 |
| **레이어 분리** | `core` → `analyzeData` → `visualizeData` 방향으로만 의존 |
| **캡슐화** | `core` 는 내부 구현. 외부에서는 `analyzeData` / `visualizeData` 만 노출 |