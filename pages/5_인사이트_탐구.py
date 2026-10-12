"""PAGE 05 — BE A DATA DETECTIVE! : 탐구 질문 + 규칙 기반 자동 인사이트."""

from html import escape

import pandas as pd
import streamlit as st

from utils import charts
from utils import data_loader as dl
from utils import statistics as stats
from utils import styles

styles.setup_page("인사이트 탐구", "🔎")

styles.page_header(
    "05", "INSIGHT EXPLORER", "BE A DATA <mark>DETECTIVE!</mark>",
    "탐구 질문을 고르고, 조건을 바꿔 가며 데이터가 말해 주는 사실을 확인해 보세요. 모든 문장은 현재 데이터로 계산됩니다.",
    accent=styles.YELLOW,
)

df = dl.require_data()
if not dl.is_student(df):
    dl.render_filters(df)
    dl.sidebar_download(dl.apply_filters(df))
    styles.empty_state(
        "🕵️", "학생 성적 데이터 전용 페이지예요",
        "탐구 질문은 StudentsPerformance.csv 구조(성별·부모 교육 수준·점심·시험 준비·3과목 점수)가 있을 때만 활성화됩니다. "
        "현재 데이터는 02~04 페이지의 범용 분석을 이용하세요.",
    )
    st.caption("누락된 필수 열: " + ", ".join(dl.missing_required(df)))
    st.stop()

dl.render_filters(df)
dl.sidebar_download(dl.apply_filters(df))

QUESTIONS = [
    {"id": "prep", "emoji": "📝", "short": "시험 준비 효과?", "group": "test preparation course",
     "text": "시험 준비 과정 이수 여부에 따라 성적 차이가 있을까?"},
    {"id": "parent", "emoji": "🎓", "short": "부모 교육 수준?", "group": "parental level of education",
     "text": "부모 교육 수준에 따라 학생들의 성적 패턴은 달라질까?"},
    {"id": "corr", "emoji": "🔗", "short": "수학 × 읽기?", "group": None,
     "text": "수학 점수와 읽기 점수 사이에는 어떤 관계가 있을까?"},
    {"id": "gender", "emoji": "⚖️", "short": "성별 분포?", "group": "gender",
     "text": "성별에 따라 과목별 점수 분포가 다를까?"},
    {"id": "lunch", "emoji": "🥪", "short": "점심 지원 유형?", "group": "lunch",
     "text": "점심 지원 유형별 평균 성적은 어떻게 다를까?"},
]
SUBJECTS = [dl.AVG_COL] + dl.SCORE_COLS


def pick(qid: str) -> None:
    st.session_state["pg5_q"] = qid


current = st.session_state.get("pg5_q", "prep")
q = next(item for item in QUESTIONS if item["id"] == current)

# ---------------------------------------------------------------------------
# STEP 1. Question cards

styles.section("1", "STEP 1 · 탐구 질문 선택", "카드를 눌러 질문을 고르세요", bg=styles.YELLOW)
qcols = st.columns(len(QUESTIONS), gap="small")
for col, item in zip(qcols, QUESTIONS):
    selected = item["id"] == current
    with col:
        with st.container(key=f"{'brut' if selected else 'card'}-q-{item['id']}"):
            styles._html(
                f'<div style="font-size:30px;line-height:1">{item["emoji"]}</div>'
                f'<div class="sil-card-title" style="margin-top:8px">Q{QUESTIONS.index(item) + 1}. {escape(item["short"])}</div>'
                f'<p class="sil-card-desc" style="min-height:42px">{escape(item["text"])}</p>'
            )
            st.button("탐구 중 ✓" if selected else "이 질문 탐구하기", key=f"pg5_btn_{item['id']}",
                      type="primary" if selected else "secondary", on_click=pick, args=(item["id"],),
                      width="stretch")

# ---------------------------------------------------------------------------
# STEP 2. Variables & filters

styles.section("2", "STEP 2 · 변수와 조건 설정",
               "사이드바의 전역 필터도 함께 적용됩니다", bg=styles.LIME)

gcol = q["group"]
ignore = (gcol,) if gcol else ()
fdf = dl.apply_filters(df, ignore=ignore)

with st.container(key="tint-step2"):
    styles._html(f'<div class="sil-card-title">Q. {escape(q["text"])}</div>')
    if q["id"] == "corr":
        c1, c2, c3 = st.columns(3)
        with c1:
            x = st.selectbox("X축 과목", dl.SCORE_COLS, index=0, format_func=dl.label, key="pg5_x")
        with c2:
            y_opts = [c for c in dl.SCORE_COLS if c != x]
            y = st.selectbox("Y축 과목", y_opts, index=0, format_func=dl.label, key="pg5_y")
        with c3:
            color = st.selectbox("색상 구분", [None] + dl.GROUP_COLS,
                                 format_func=lambda c: "없음" if c is None else dl.label(c), key="pg5_color")
    else:
        subject = st.radio("분석할 점수", SUBJECTS, format_func=dl.label, horizontal=True, key="pg5_subject")
    if gcol and st.session_state.get(f"flt_{gcol}"):
        st.caption(f"비교 기준인 '{dl.label(gcol)}'의 전역 필터는 이 질문에서 제외했습니다. 다른 필터는 그대로 적용됩니다.")

dl.filter_bar(df, fdf, ignore)
dl.stop_if_empty(fdf)


def group_table(data: pd.DataFrame, group: str, value: str) -> pd.DataFrame:
    rows = []
    for g in dl.order_values(group, data[group].dropna().unique()):
        s = data.loc[data[group] == g, value].dropna()
        rows.append({dl.label(group): g, "n": len(s), "Mean": s.mean(), "Median": s.median(),
                     "Std": s.std() if len(s) > 1 else float("nan"), "Min": s.min(), "Max": s.max()})
    return pd.DataFrame(rows).round(1)


def josa(word: str, with_final: str, without_final: str) -> str:
    """앞 글자의 받침 유무에 맞는 조사 (은/는, 과/와)."""
    last = word.strip()[-1:] or " "
    if "가" <= last <= "힣":
        return with_final if (ord(last) - 0xAC00) % 28 else without_final
    return f"{with_final}({without_final})"


def diff_sentence(a_desc: str, b_desc: str, diff: float, what: str) -> str:
    topic = f"{a_desc}의 {what}{josa(what, '은', '는')}"
    if round(diff, 1) == 0:
        return f"현재 선택된 데이터에서 {topic} {b_desc}{josa(b_desc, '과', '와')} 거의 같습니다 (차이 0.0점)."
    word = "높습니다" if diff > 0 else "낮습니다"
    return f"현재 선택된 데이터에서 {topic} {b_desc}보다 <b>{abs(diff):.1f}점 {word}</b>."


def two_group_insight(data, group, a, b, a_desc, b_desc, value):
    """두 집단 평균 차이 인사이트. 한쪽 집단이 없으면 None."""
    sa = data.loc[data[group] == a, value].dropna()
    sb = data.loc[data[group] == b, value].dropna()
    if sa.empty or sb.empty:
        return None
    diff = sa.mean() - sb.mean()
    return diff, sentence_with_n(diff_sentence(a_desc, b_desc, diff, mean_label(value)), len(sa), len(sb))


def mean_label(value: str) -> str:
    return "3과목 평균 점수" if value == dl.AVG_COL else f"{dl.label(value)} 평균"


def sentence_with_n(text: str, na: int, nb: int) -> str:
    return f"{text} (n={na:,} vs {nb:,})"


# ---------------------------------------------------------------------------
# STEP 3~5 per question

CAUSAL_NOTE = "이 결과는 관찰된 차이이며, 해당 변수가 성적 차이의 원인이라고 단정할 수 없습니다."

styles.section("3", "STEP 3 · 그래프 확인", "Hover로 세부 값, 드래그로 확대, 범례 클릭으로 집단 켜고 끄기", bg=styles.COBALT)

if q["id"] == "corr":
    res = stats.pearson(fdf, x, y)
    fit = stats.linear_fit(fdf, x, y)
    order = dl.order_values(color, fdf[color].dropna().unique()) if color else None
    with st.container(key="card-q-chart"):
        charts.show(charts.scatter(fdf, x, y, color, fit, order), "pg5_scatter")

    styles.section("4", "STEP 4 · 기술통계 결과", bg=styles.PINK)
    with st.container(key="card-q-stats"):
        st.dataframe(stats.describe(fdf, [x, y]))

    styles.section("5", "STEP 5 · 데이터 기반 인사이트", bg=styles.YELLOW)
    if res["r"] is None:
        st.warning(res["reason"])
    else:
        direction, level = stats.strength(res["r"])
        i1, i2 = st.columns(2, gap="medium")
        with i1:
            styles.insight(
                "PEARSON r", f"{res['r']:.3f}",
                f"현재 선택된 데이터에서 {dl.label(x)} 점수와 {dl.label(y)} 점수는 <b>{direction} {level} 상관관계</b>를 보입니다 "
                f"(n={res['n']:,}).", bg=styles.YELLOW, sticker="r")
        with i2:
            if fit:
                styles.insight(
                    "SLOPE", f"{fit[0] * 10:+.1f}점",
                    f"추세선 기준으로 {dl.label(x)} 점수가 10점 높을 때 {dl.label(y)} 점수는 평균적으로 "
                    f"약 <b>{abs(fit[0] * 10):.1f}점 {'높은' if fit[0] > 0 else '낮은'}</b> 경향이 있습니다.",
                    bg=styles.LIME, sticker="↗")
    styles.note("상관관계가 높다고 해서 한 변수가 다른 변수의 원인이라는 의미는 아닙니다.")

else:
    table = group_table(fdf, gcol, subject)
    present = table[table["n"] > 0]

    with st.container(key="card-q-chart"):
        if q["id"] == "gender":
            g1, g2 = st.columns(2, gap="medium")
            with g1:
                styles.card_title(f"{dl.label(subject)} 분포 (Box)")
                charts.show(charts.group_box(fdf, gcol, subject, present[dl.label(gcol)].tolist()), "pg5_box")
            with g2:
                levels = present[dl.label(gcol)].tolist()
                if len(levels) >= 2:
                    styles.card_title(f"{dl.label(subject)} 분포 (집단 내 비율)")
                    charts.show(charts.compare_hist(fdf, gcol, levels[0], levels[1], subject), "pg5_hist")
                else:
                    st.info("분포를 비교하려면 두 성별 집단이 모두 필요합니다.")
        else:
            gm = stats.group_means(fdf, gcol, dl.SCORE_COLS + [dl.AVG_COL])
            show_cols = dl.SCORE_COLS if subject == dl.AVG_COL else [subject]
            long = stats.to_long(gm, show_cols + ([dl.AVG_COL] if subject == dl.AVG_COL else []), gcol)
            charts.show(charts.grouped_bar(long, dl.label(gcol)), f"pg5_bar_{q['id']}")

    styles.section("4", "STEP 4 · 기술통계 결과", f"{dl.label(gcol)}별 {dl.label(subject)}", bg=styles.PINK)
    with st.container(key="card-q-stats"):
        st.dataframe(table, hide_index=True)

    styles.section("5", "STEP 5 · 데이터 기반 인사이트", "규칙 기반으로 자동 생성된 문장입니다 (외부 AI 미사용)", bg=styles.YELLOW)

    cards = []  # (tag, big, html, bg, sticker)
    if len(present) < 2:
        st.warning(f"현재 조건에서 '{dl.label(gcol)}' 집단이 2개 미만이라 비교 인사이트를 만들 수 없습니다. 필터를 넓혀 보세요.")
    elif q["id"] == "prep":
        r = two_group_insight(fdf, gcol, "completed", "none", "시험 준비 과정을 이수한 학생 집단",
                              "미이수 집단", subject)
        if r:
            cards.append(("PREP vs NONE", f"{r[0]:+.1f}점", r[1], styles.YELLOW, "📝"))
        per = [(c, two_group_insight(fdf, gcol, "completed", "none", "", "", c)) for c in dl.SCORE_COLS]
        per = [(c, v[0]) for c, v in per if v]
        if per:
            c_max = max(per, key=lambda t: t[1])
            cards.append(("BIGGEST GAP SUBJECT", dl.label(c_max[0]),
                          f"세 과목 중 이수·미이수 집단의 평균 차이가 가장 큰 과목은 <b>{dl.label(c_max[0])}</b>"
                          f"({c_max[1]:+.1f}점)입니다.", styles.LIME, "★"))
    elif q["id"] == "lunch":
        r = two_group_insight(fdf, gcol, "standard", "free/reduced", "일반(standard) 급식 학생 집단",
                              "무료·할인(free/reduced) 급식 집단", subject)
        if r:
            cards.append(("STANDARD vs FREE/REDUCED", f"{r[0]:+.1f}점", r[1], styles.YELLOW, "🥪"))
        share = (fdf[gcol] == "free/reduced").mean() * 100
        cards.append(("SHARE", f"{share:.1f}%",
                      f"현재 선택된 데이터에서 무료·할인 급식 학생의 비율은 <b>{share:.1f}%</b>입니다.",
                      styles.LIME, "%"))
    elif q["id"] == "gender":
        r = two_group_insight(fdf, gcol, "female", "male", "여학생(female) 집단", "남학생(male) 집단", subject)
        if r:
            cards.append(("FEMALE vs MALE", f"{r[0]:+.1f}점", r[1], styles.YELLOW, "⚖"))
        sd = present.set_index(dl.label(gcol))["Std"]
        if {"female", "male"} <= set(sd.index) and sd.notna().all():
            wider = "female" if sd["female"] > sd["male"] else "male"
            cards.append(("SPREAD (STD)", f"{sd['female']:.1f} / {sd['male']:.1f}",
                          f"표준편차는 female {sd['female']:.1f}, male {sd['male']:.1f}로 "
                          f"<b>{wider}</b> 집단의 점수가 더 넓게 퍼져 있습니다.", styles.LIME, "↔"))
    elif q["id"] == "parent":
        ranked = present.set_index(dl.label(gcol))["Mean"]
        top, bottom = ranked.idxmax(), ranked.idxmin()
        cards.append(("HIGHEST", f"{ranked.max():.1f}",
                      f"{dl.label(subject)} 평균이 가장 높은 집단은 부모 교육 수준 <b>{escape(str(top))}</b>입니다.",
                      styles.LIME, "▲"))
        cards.append(("LOWEST", f"{ranked.min():.1f}",
                      f"가장 낮은 집단은 <b>{escape(str(bottom))}</b>이며, 최고 집단과 <b>{ranked.max() - ranked.min():.1f}점</b> 차이입니다.",
                      styles.WHITE, "▼"))
        if {"master's degree", "some high school"} <= set(ranked.index):
            d = ranked["master's degree"] - ranked["some high school"]
            cards.append(("MASTER'S vs SOME HIGH SCHOOL", f"{d:+.1f}점",
                          diff_sentence("부모가 석사 학위(master's degree)인 학생 집단",
                                        "고교 미졸업(some high school) 집단", d, mean_label(subject)),
                          styles.YELLOW, "🎓"))

    if cards:
        icols = st.columns(len(cards), gap="medium")
        for col, (tag, big, text, bg, sticker) in zip(icols, cards):
            with col:
                styles.insight(tag, big, text, bg=bg, sticker=sticker)
        styles.note(CAUSAL_NOTE)
    elif len(present) >= 2:
        st.info("현재 조건에서는 계산 가능한 인사이트가 없습니다 (비교 대상 집단 중 일부가 비어 있음).")
