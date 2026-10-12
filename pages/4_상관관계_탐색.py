"""PAGE 04 — EVERYTHING IS CONNECTED? : 상관관계 탐색."""

from html import escape

import streamlit as st

from utils import charts
from utils import data_loader as dl
from utils import statistics as stats
from utils import styles

styles.setup_page("상관관계 탐색", "🔗")

styles.page_header(
    "04", "CORRELATION LAB", "EVERYTHING IS <mark>CONNECTED?</mark>",
    "두 숫자형 변수가 함께 움직이는지 피어슨 상관계수와 산점도로 확인합니다.",
    accent=styles.COBALT,
)

df, fdf = dl.use_filtered_data()
dl.filter_bar(df, fdf)
dl.stop_if_empty(fdf)

numeric, _ = dl.column_types(df)
if len(numeric) < 2:
    styles.empty_state("📉", "숫자형 변수가 부족해요", "상관관계 분석에는 숫자형 변수가 2개 이상 필요합니다.")
    st.stop()

base = [c for c in dl.SCORE_COLS if c in numeric] or numeric[:6]

# ---------------------------------------------------------------------------
# A. Correlation matrix

left, right = st.columns([3, 2], gap="medium")
with left:
    styles.section("A", "Correlation Matrix", "피어슨 상관계수 r (−1 ~ +1) · 소수점 셋째 자리", bg=styles.COBALT)
    with st.container(key="card-corr"):
        mat_cols = st.multiselect("행렬에 넣을 변수", numeric, default=base, format_func=dl.label,
                                  key="pg4_mat_cols")
        if len(mat_cols) < 2:
            st.info("변수를 2개 이상 선택하세요.")
        else:
            corr = stats.corr_matrix(fdf, mat_cols)
            charts.show(charts.corr_heatmap(corr), "pg4_corr")
            if corr.isna().to_numpy().any():
                styles.note("빈칸(NaN)은 값이 모두 같거나 유효 표본이 부족해 계산할 수 없는 조합입니다.")
            n_valid = len(fdf[mat_cols].dropna())
            styles.note(f"결측이 없는 행 기준 유효 표본: {n_valid:,}행 (각 쌍은 해당 두 변수가 모두 있는 행으로 계산)")

with right:
    styles.section("B", "Pick Two Variables", "X축과 Y축 변수를 고르세요", bg=styles.PINK)
    with st.container(key="tint-pick"):
        x = st.selectbox("X축", numeric, index=numeric.index(base[0]), format_func=dl.label, key="pg4_x")
        y_default = base[1] if len(base) > 1 and base[1] != x else next(c for c in numeric if c != x)
        y_opts = [c for c in numeric if c != x]
        y = st.selectbox("Y축", y_opts, index=y_opts.index(y_default) if y_default in y_opts else 0,
                         format_func=dl.label, key="pg4_y")
        color_opts = [None] + dl.group_cols(df)
        color = st.selectbox("색상 구분 (범주형)", color_opts,
                             format_func=lambda c: "없음" if c is None else dl.label(c), key="pg4_color")
        trend = st.toggle("회귀 추세선 표시", value=True, key="pg4_trend")

    # C. Correlation insight
    res = stats.pearson(fdf, x, y)
    if res["r"] is None:
        styles.insight("CORRELATION", "N/A", escape(res["reason"]), bg=styles.WHITE, sticker="?")
    else:
        direction, level = stats.strength(res["r"])
        trend_text = ("한 변수가 높을수록 다른 변수도 높은 경향" if res["r"] > 0
                      else "한 변수가 높을수록 다른 변수는 낮은 경향" if res["r"] < 0 else "뚜렷한 경향이 없음")
        styles.insight(
            f"r · {dl.label(x)} × {dl.label(y)}", f"{res['r']:.3f}",
            f"<b>{direction} {level}</b> 상관관계입니다. 현재 데이터에서는 {trend_text}이 나타납니다. "
            f"(유효 표본 n={res['n']:,})",
            bg=styles.YELLOW if abs(res["r"]) >= 0.5 else styles.LIME, sticker="r",
        )

# ---------------------------------------------------------------------------
# B. Scatter

styles.section("C", "Interactive Scatter Plot",
               "드래그해서 확대 · 더블클릭으로 원래 크기 · 범례를 눌러 집단을 켜고 끌 수 있어요", bg=styles.VIOLET)
with st.container(key="card-scatter"):
    fit = stats.linear_fit(fdf, x, y) if trend else None
    order = dl.order_values(color, fdf[color].dropna().unique()) if color else None
    charts.show(charts.scatter(fdf, x, y, color, fit, order), "pg4_scatter")
    if trend and fit:
        styles.note(f"선형 추세선(최소제곱법): {dl.label(y)} = {fit[0]:.2f} × {dl.label(x)} + {fit[1]:.2f}")
    elif trend:
        styles.note("추세선을 계산할 수 없습니다 (X 값이 모두 같거나 표본이 부족함).")

# ---------------------------------------------------------------------------
# D. Statistical notes

styles.section("D", "Statistical Notes", bg=styles.YELLOW)
n1, n2 = st.columns(2, gap="medium")
with n1:
    styles.insight("REMEMBER", "",
                   "상관관계가 높다고 해서 한 변수가 다른 변수의 원인이라는 의미는 아닙니다.",
                   bg=styles.YELLOW, sticker="!")
with n2:
    with st.container(key="card-guide"):
        styles.card_title("상관계수 읽는 법", "이 앱에서 사용하는 강도 기준 (|r|)")
        styles.chips_row(["< 0.1 거의 없음", "0.1–0.3 약함", "0.3–0.5 중간", "0.5–0.7 강함", "≥ 0.7 매우 강함"])
        styles.note("피어슨 r은 직선 관계만 측정합니다. 곡선 관계나 이상치의 영향은 산점도로 함께 확인하세요.")
