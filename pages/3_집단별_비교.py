"""PAGE 03 — DO DIFFERENT GROUPS SHOW DIFFERENT PATTERNS? : 집단별 비교."""

from html import escape

import streamlit as st

from utils import charts
from utils import data_loader as dl
from utils import statistics as stats
from utils import styles

styles.setup_page("집단별 비교", "👥")

styles.page_header(
    "03", "GROUP COMPARISON", "DO DIFFERENT GROUPS SHOW <mark>DIFFERENT PATTERNS?</mark>",
    "비교 기준을 고르면 집단별 평균, 히트맵, 두 집단 비교, 자동 요약이 함께 바뀝니다.",
    accent=styles.PINK,
)

df, fdf_all = dl.use_filtered_data()
groups = dl.group_cols(df)
values = dl.value_cols(df)
if not groups or not values:
    styles.empty_state("🧩", "비교할 변수가 부족해요",
                       "집단 비교에는 범주형 변수(고유값 2~30개)와 숫자형 변수가 각각 하나 이상 필요합니다.")
    st.stop()

# ---------------------------------------------------------------------------
# Controls

with st.container(key="tint-controls"):
    c1, c2 = st.columns([1, 2], gap="medium")
    with c1:
        gcol = st.selectbox("비교 기준 (집단 변수)", groups, format_func=dl.label, key="pg3_group")
    with c2:
        extra = [c for c in (dl.AVG_COL,) if c in df.columns and c not in values]
        sel_values = st.multiselect("비교할 점수 변수", values + extra, default=values,
                                    format_func=dl.label, key="pg3_values")

    # 전역 필터가 비교 대상 집단을 잘라내는 경우 안내
    conflict = bool(st.session_state.get(f"flt_{gcol}"))
    ignore_own = False
    if conflict:
        ignore_own = st.toggle(f"'{dl.label(gcol)}' 전역 필터를 이 페이지에서 무시하고 모든 집단 비교",
                               value=True, key="pg3_ignore_own")
        if ignore_own:
            st.caption(f"사이드바에서 '{dl.label(gcol)}'를 선택했지만, 집단 비교를 위해 이 변수의 필터만 제외했습니다. 다른 필터는 그대로 적용됩니다.")
        else:
            st.caption(f"'{dl.label(gcol)}' 필터가 적용되어 선택한 집단만 비교합니다.")

ignore = (gcol,) if ignore_own else ()
fdf = dl.apply_filters(df, ignore=ignore) if ignore else fdf_all
dl.filter_bar(df, fdf, ignore)
dl.stop_if_empty(fdf)

if not sel_values:
    st.info("비교할 점수 변수를 하나 이상 선택하세요.")
    st.stop()

gm = stats.group_means(fdf, gcol, sel_values)
gtitle = dl.label(gcol)
target = dl.AVG_COL if dl.AVG_COL in sel_values else sel_values[0]

if len(gm) < 2:
    only = ", ".join(map(str, gm.index)) or "없음"
    styles.empty_state("☝️", "집단이 하나뿐이에요",
                       f"현재 조건에서 '{gtitle}'의 집단은 {only} 하나라 비교할 수 없습니다. 필터를 넓혀 보세요.")
    st.stop()

# ---------------------------------------------------------------------------
# Group insights (C 섹션에서 표시)

ins = stats.group_insights(gm, sel_values, target)

# ---------------------------------------------------------------------------
# A. Grouped bar + B. Heatmap (bento)

styles.section("A", "Grouped Bar Chart", f"{gtitle}별 평균 점수 · 막대에 마우스를 올리면 표본 수(n)가 보여요", bg=styles.PINK)
with st.container(key="card-grouped"):
    long = stats.to_long(gm, sel_values, gcol)
    charts.show(charts.grouped_bar(long, gtitle), "pg3_grouped")
    styles.chips_row([f"{g}: n={int(n):,}" for g, n in gm["n"].items()], prefix="표본 수 ·")

left, right = st.columns([3, 2], gap="medium")
with left:
    styles.section("B", "Group Heatmap", "X축 과목 · Y축 집단 · 색이 진할수록 평균이 높음", bg=styles.VIOLET)
    with st.container(key="card-heatmap"):
        charts.show(charts.heatmap(gm, sel_values, gtitle), "pg3_heatmap")
with right:
    styles.section("C", "Group Insights", "현재 조건에서 자동 계산된 특징", bg=styles.YELLOW)
    if ins:
        styles.insight(
            "HIGHEST GROUP", f"{ins['top_value']:.1f}",
            f"<b>{escape(str(ins['top']))}</b> 집단의 {escape(dl.label(target))}이(가) 가장 높습니다 (n={ins['top_n']:,}).",
            bg=styles.LIME, sticker="▲",
        )
        styles.insight(
            "LOWEST GROUP", f"{ins['bottom_value']:.1f}",
            f"<b>{escape(str(ins['bottom']))}</b> 집단의 {escape(dl.label(target))}이(가) 가장 낮습니다 (n={ins['bottom_n']:,}). "
            f"최고 집단과 <b>{ins['spread']:.1f}점</b> 차이입니다.",
            bg=styles.WHITE, sticker="▼",
        )
        if ins["widest_col"]:
            styles.insight(
                "WIDEST GAP", f"{ins['widest_gap']:.1f}",
                f"집단 간 평균 차이(최고−최저)가 가장 큰 변수는 <b>{escape(dl.label(ins['widest_col']))}</b>입니다.",
                bg=styles.YELLOW, sticker="↔",
            )
        styles.note("집단 간 평균 차이는 관찰된 경향이며, 해당 변수가 점수 차이의 원인이라는 뜻은 아닙니다.")
    else:
        st.info("인사이트를 계산하려면 평균이 있는 집단이 두 개 이상 필요합니다.")

summary = gm.round(1).rename(columns={c: dl.label(c) for c in sel_values})
st.download_button("집단별 요약 통계 CSV 다운로드", summary.to_csv().encode("utf-8-sig"),
                   file_name=f"group_summary_{gcol.replace('/', '_')}.csv", mime="text/csv",
                   icon=":material/download:", key="pg3_dl_summary", on_click="ignore")

# ---------------------------------------------------------------------------
# D. Compare two groups

styles.section("D", "Compare Two Groups", "두 집단을 골라 과목별 평균과 분포를 나란히 비교합니다", bg=styles.COBALT)
options = list(gm.index)
with st.container(key="brut-compare"):
    s1, s2, s3 = st.columns(3)
    with s1:
        a = st.selectbox("집단 A ●", options, index=0, key="pg3_a")
    with s2:
        b_options = [o for o in options if o != a]
        b = st.selectbox("집단 B ◆", b_options, index=len(b_options) - 1, key="pg3_b")
    with s3:
        dist_var = st.selectbox("분포 비교 변수", sel_values, format_func=dl.label, key="pg3_dist")

    a_row, b_row = gm.loc[a], gm.loc[b]
    k = st.columns(2 + len(sel_values[:3]))
    with k[0]:
        styles.kpi(f"A · {a}"[:28], f"{int(a_row['n']):,}", "학생 수", bg=styles.INK, fg=styles.WHITE)
    with k[1]:
        styles.kpi(f"B · {b}"[:28], f"{int(b_row['n']):,}", "학생 수", bg=styles.YELLOW)
    for i, c in enumerate(sel_values[:3]):
        diff = a_row[c] - b_row[c]
        with k[2 + i]:
            styles.kpi(f"{dl.label(c)} 차이 (A−B)", f"{diff:+.1f}",
                       f"A {a_row[c]:.1f} · B {b_row[c]:.1f}", soft=True)

    d1, d2 = st.columns(2, gap="medium")
    with d1:
        styles.card_title("평균 비교 (Dumbbell)", "선의 길이 = 두 집단의 평균 차이")
        charts.show(charts.dumbbell(a, a_row, b, b_row, sel_values), "pg3_dumbbell")
    with d2:
        styles.card_title(f"{dl.label(dist_var)} 분포 비교", "집단 크기가 달라 집단 내 비율(%)로 표시")
        charts.show(charts.compare_hist(fdf, gcol, a, b, dist_var), "pg3_compare_hist")
