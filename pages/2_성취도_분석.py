"""PAGE 02 — HOW ARE STUDENTS PERFORMING? : 성취도 KPI·분포·기술통계."""

import pandas as pd
import streamlit as st

from utils import charts
from utils import data_loader as dl
from utils import statistics as stats
from utils import styles

styles.setup_page("성취도 분석", "📊")

styles.page_header(
    "02", "PERFORMANCE ANALYTICS", "HOW ARE STUDENTS <mark>PERFORMING?</mark>",
    "과목별 평균과 점수 분포를 살펴봅니다. 사이드바 필터를 바꾸면 모든 숫자와 그래프가 즉시 갱신됩니다.",
    accent=styles.LIME,
)

df, fdf = dl.use_filtered_data()
dl.filter_bar(df, fdf)
dl.stop_if_empty(fdf)

values = dl.value_cols(df)
if not values:
    styles.empty_state("🔢", "숫자형 변수가 없어요", "성취도 분석에는 숫자형 열이 하나 이상 필요합니다.")
    st.stop()

student_scores = all(c in df.columns for c in dl.SCORE_COLS)
extra = [c for c in (dl.AVG_COL, dl.TOTAL_COL) if c in df.columns and c not in values]
dist_options = values + extra

# ---------------------------------------------------------------------------
# A. KPI overview

styles.section("A", "KPI Overview", "현재 필터 조건의 학생 수와 평균 점수", bg=styles.LIME)

kpi_cols = st.columns(5 if student_scores else min(5, len(values) + 1))
with kpi_cols[0]:
    styles.kpi("Students", f"{len(fdf):,}", f"전체 {len(df):,}명 중", bg=styles.LIME)
if student_scores:
    avg = fdf[dl.AVG_COL].dropna()
    with kpi_cols[1]:
        styles.kpi("Overall Avg", f"{avg.mean():.1f}" if len(avg) else "–",
                   f"3과목 평균 · n={len(avg):,}", bg=styles.YELLOW)
    kpi_vars = dl.SCORE_COLS
    kpi_bgs = [(styles.COBALT, styles.WHITE), (styles.PINK, styles.INK), (styles.VIOLET, styles.WHITE)]
    offset = 2
else:
    kpi_vars = values[: len(kpi_cols) - 1]
    kpi_bgs = [(styles.WHITE, styles.INK)] * len(kpi_vars)
    offset = 1
for i, (col, (bg, fg)) in enumerate(zip(kpi_vars, kpi_bgs)):
    s = fdf[col].dropna()
    with kpi_cols[offset + i]:
        styles.kpi(f"{dl.label(col)} 평균" if student_scores else str(col)[:24],
                   f"{s.mean():.1f}" if len(s) else "–", f"n={len(s):,}", bg=bg, fg=fg,
                   soft=not student_scores)

# ---------------------------------------------------------------------------
# B. Subject comparison + C. Distribution (bento row)

left, right = st.columns([2, 3], gap="medium")
with left:
    styles.section("B", "Subject Comparison", "과목별 평균 점수 (0점 기준 막대)", bg=styles.COBALT)
    with st.container(key="card-mean-bar"):
        mean_df = pd.DataFrame({
            "variable": values,
            "과목": [dl.label(c) for c in values],
            "mean": [fdf[c].mean() for c in values],
            "n": [int(fdf[c].notna().sum()) for c in values],
        }).dropna(subset=["mean"])
        if mean_df.empty:
            st.info("평균을 계산할 수 있는 값이 없습니다.")
        else:
            charts.show(charts.mean_bar(mean_df), "pg2_mean_bar")
            if not student_scores:
                styles.note("범용 모드: 변수마다 단위가 다를 수 있으니 막대 높이를 직접 비교할 때 주의하세요.")

with right:
    styles.section("C", "Score Distribution", "점수 구간별 학생 수 · 평균(실선)과 중앙값(점선)", bg=styles.PINK)
    with st.container(key="card-hist"):
        h1, h2 = st.columns([3, 2])
        with h1:
            hist_col = st.selectbox("과목 선택", dist_options, format_func=dl.label, key="pg2_hist_col")
        with h2:
            nbins = st.slider("구간 수", 5, 40, 20, key="pg2_bins")
        s = fdf[hist_col].dropna()
        if s.empty:
            st.info("선택한 변수에 유효한 값이 없습니다.")
        else:
            charts.show(charts.histogram(fdf, hist_col, nbins), "pg2_hist")
            styles.chips_row([f"평균 {s.mean():.1f}", f"중앙값 {s.median():.1f}",
                              f"표준편차 {s.std():.1f}" if len(s) > 1 else "표준편차 –",
                              f"유효 표본 {len(s):,}"])

# ---------------------------------------------------------------------------
# D. Box plot

styles.section("D", "Score Box Plot", "상자 = Q1~Q3, 가운데 선 = 중앙값, 수염 = 1.5×IQR 범위, 점 = 이상치", bg=styles.VIOLET)
with st.container(key="card-box"):
    box_cols = st.multiselect("비교할 변수", dist_options, default=values[:6], format_func=dl.label,
                              key="pg2_box_cols")
    if not box_cols:
        st.info("변수를 하나 이상 선택하세요.")
    else:
        charts.show(charts.box(fdf, box_cols), "pg2_box")

# ---------------------------------------------------------------------------
# E. Descriptive statistics

styles.section("E", "Descriptive Statistics", "결측 제외 · 표준편차는 표본 표준편차(n−1) · 소수점 첫째 자리", bg=styles.YELLOW)
with st.container(key="card-describe"):
    desc = stats.describe(fdf, dist_options)
    st.dataframe(desc, column_config={c: st.column_config.NumberColumn(c, format="%.1f")
                                      for c in stats.STAT_COLUMNS if c != "Count"})
    st.download_button("기술통계 CSV 다운로드", desc.to_csv().encode("utf-8-sig"),
                       file_name="descriptive_statistics.csv", mime="text/csv",
                       icon=":material/download:", key="pg2_dl_desc", on_click="ignore")

# ---------------------------------------------------------------------------
# F. Categorical frequency

_, categorical = dl.column_types(df)
cat_options = [c for c in categorical if fdf[c].nunique(dropna=True) <= 50]
styles.section("F", "Category Frequency", "범주형 변수의 빈도·비율·최빈값", bg=styles.LIME)
with st.container(key="card-freq"):
    if not cat_options:
        st.info("빈도 분석에 사용할 범주형 변수가 없습니다 (고유값 50개 이하인 범주형 열 필요).")
    else:
        fcol = st.selectbox("범주형 변수", cat_options, format_func=dl.label, key="pg2_freq_col")
        freq = stats.frequency(fdf, fcol)
        f1, f2 = st.columns([3, 2], gap="medium")
        with f1:
            charts.show(charts.frequency_bar(freq, fcol), "pg2_freq")
        with f2:
            st.dataframe(freq, hide_index=True)
            mode_vals = stats.modes(fdf[fcol])
            styles.chips_row([f"최빈값: {', '.join(map(str, mode_vals))}" if mode_vals else "최빈값 없음",
                              f"범주 수 {fdf[fcol].nunique(dropna=True)}"])
