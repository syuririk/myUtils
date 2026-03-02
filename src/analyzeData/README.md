# EconIndex — 경제지표 분석 라이브러리

## 프로젝트 구조

```
econindex/
├── core/
│   ├── __init__.py
│   ├── dataset.py          # EconDataset  — 데이터 로딩·검증·관리
│   └── indicator.py        # Indicator    — 단일 지표 래퍼
├── analysis/
│   ├── __init__.py
│   ├── descriptive.py      # DescriptiveAnalyzer  — 기술통계
│   ├── timeseries.py       # TimeSeriesAnalyzer   — 시계열 분석
│   ├── comparative.py      # ComparativeAnalyzer  — 지표 간 비교
│   └── forecaster.py       # Forecaster           — 예측 모델
├── visualization/
│   ├── __init__.py
│   ├── base_chart.py       # BaseChart    — 공통 차트 설정
│   ├── line_chart.py       # LineChart    — 추세선
│   ├── heatmap.py          # HeatmapChart — 상관/계절성 히트맵
│   └── dashboard.py        # Dashboard    — Plotly 대화형
├── utils/
│   ├── __init__.py
│   ├── transformer.py      # DataTransformer — 정규화·변환
│   └── validator.py        # DataValidator   — 데이터 검증
├── tests/
│   └── ...
└── README.md
```

## 클래스 관계도

```
EconDataset
  ├── [Indicator, ...]          # 지표 목록 관리
  ├── DataValidator             # 자동 검증
  └── DataTransformer           # 변환 유틸

DescriptiveAnalyzer(dataset)    # 기술통계
TimeSeriesAnalyzer(dataset)     # 시계열
ComparativeAnalyzer(dataset)    # 비교
Forecaster(dataset)             # 예측

BaseChart
  ├── LineChart(dataset)
  ├── HeatmapChart(dataset)
  └── Dashboard(dataset)        # 여러 차트 조합
```
