"""PAGE 01 — DROP YOUR DATA! : CSV 업로드와 데이터 점검."""

import hashlib

import streamlit as st

from utils import data_loader as dl
from utils import statistics as stats
from utils import styles

styles.setup_page("데이터 업로드", "📂")

styles.page_header(
    "01", "DATA UPLOAD", "DROP YOUR <mark>DATA!</mark>",
    "CSV 파일을 올리면 자료형을 자동으로 분류하고, 모든 분석 페이지에서 같은 데이터를 공유합니다.",
    accent=styles.LIME,
)

# ---------------------------------------------------------------------------
# Upload area

up_col, side_col = st.columns([3, 2], gap="large")
with up_col:
    uploaded = st.file_uploader(
        "CSV 파일을 끌어다 놓거나 클릭해서 선택하세요",
        type=["csv"],
        key="uploader",
        help="UTF-8, CP949(EUC-KR) 인코딩을 자동으로 인식합니다.",
    )
with side_col:
    with st.container(key="tint-sample"):
        styles.card_title("NO FILE? NO PROBLEM.", "과제 기본 데이터로 바로 시작할 수 있어요.")
        st.button("샘플 데이터 사용 (StudentsPerformance.csv)", type="primary",
                  on_click=dl.load_sample, key="use_sample", width="stretch")
        if dl.get_df() is not None:
            st.button("데이터 비우기", on_click=dl.clear_data, key="clear_data", width="stretch")

# 새 파일이 올라왔을 때만 읽는다 (같은 파일로 재실행될 때는 기존 상태 유지)
if uploaded is not None:
    raw = uploaded.getvalue()
    sig = hashlib.md5(raw).hexdigest() + uploaded.name
    if st.session_state.get("last_upload_sig") != sig:
        st.session_state["last_upload_sig"] = sig
        st.session_state.pop("load_error", None)
        with st.spinner("CSV를 읽고 있어요..."):
            try:
                dl.load_bytes(raw, uploaded.name)
                st.toast(f"{uploaded.name} 업로드 완료! 이전 필터와 분석 설정을 초기화했어요.", icon="✅")
            except dl.DataError as e:
                st.session_state["load_error"] = str(e)
            except Exception as e:  # 예상하지 못한 형식도 앱 전체가 멈추지 않도록
                st.session_state["load_error"] = f"파일을 처리하는 중 오류가 발생했습니다: {e}"

if st.session_state.get("load_error"):
    st.error(st.session_state["load_error"], icon=":material/error:")

df = dl.get_df()
if df is None:
    styles.empty_state("⬆️", "데이터를 기다리는 중", "CSV를 업로드하거나 샘플 데이터 버튼을 눌러 주세요.")
    st.stop()

# ---------------------------------------------------------------------------
# Status

numeric, categorical = dl.column_types(df)
info = st.session_state.get("data_info", {})
student = dl.is_student(df)
n_missing = int(df.isna().sum().sum())
n_dup = int(df.duplicated().sum())

badges = styles.pill("UPLOAD OK", bg=styles.LIME)
badges += styles.pill("STUDENT SCHEMA ✓" if student else "GENERIC CSV MODE",
                      bg=styles.YELLOW if student else styles.WHITE)
badges += styles.pill(f"ENCODING · {st.session_state.get('data_encoding', '-')}", bg=styles.WHITE)
styles._html(f'<div style="margin:18px 0 6px">{badges}</div>')
styles.note(f"현재 데이터: {st.session_state.get('data_name', '')}")

if not student:
    missing = dl.missing_required(df)
    st.info(
        "학생 성적 데이터의 필수 열 일부가 없어 범용 분석 모드로 동작합니다. "
        "숫자형 변수 기술통계·범주형 빈도·분포·상관관계 분석은 그대로 사용할 수 있고, "
        "05 인사이트 탐구의 학생 전용 질문은 비활성화됩니다.\n\n"
        f"누락된 열: {', '.join(missing)}",
        icon=":material/info:",
    )
if info.get("coerced"):
    detail = ", ".join(f"{dl.label(c)} {n}건" for c, n in info["coerced"].items())
    st.warning(f"점수 열에서 숫자가 아닌 값을 결측으로 처리했습니다: {detail}", icon=":material/warning:")

k1, k2, k3, k4 = st.columns(4)
with k1:
    styles.kpi("Rows", f"{len(df):,}", "행 개수", bg=styles.LIME)
with k2:
    styles.kpi("Columns", f"{df.shape[1]}", f"원본 {df.shape[1] - len(info.get('derived', []))} + 파생 {len(info.get('derived', []))}",
               bg=styles.WHITE)
with k3:
    styles.kpi("Missing", f"{n_missing:,}", "결측값 개수 (전체 셀)", bg=styles.PINK)
with k4:
    styles.kpi("Duplicates", f"{n_dup:,}", "완전히 같은 행", bg=styles.VIOLET, fg=styles.WHITE)

# ---------------------------------------------------------------------------
# Preview + variable summary (Bento)

styles.section("A", "데이터 미리보기", "처음 100행을 표시합니다. 열 머리글을 눌러 정렬할 수 있어요.", bg=styles.LIME)
with st.container(key="card-preview"):
    st.dataframe(df.head(100), height=320, hide_index=False)

styles.section("B", "변수 자동 분류", "숫자형과 범주형 변수를 자동으로 나눴습니다.", bg=styles.PINK)
v1, v2 = st.columns([1, 1], gap="medium")
with v1:
    with st.container(key="brut-numeric"):
        styles.card_title(f"NUMERIC · {len(numeric)}", "평균·분포·상관관계 분석에 사용")
        styles.chips_row([dl.label(c) if c in dl.LABELS else c for c in numeric] or ["없음"])
        if info.get("derived"):
            styles.note("파생 변수: " + ", ".join(f"{c} ({dl.label(c)})" for c in info["derived"]))
        if info.get("converted"):
            styles.note("텍스트 → 숫자형 변환: " + ", ".join(info["converted"]))
        if not numeric:
            st.warning("숫자형 변수가 없어 평균·분포·상관관계 분석을 할 수 없습니다.")
with v2:
    with st.container(key="brut-categorical"):
        styles.card_title(f"CATEGORICAL · {len(categorical)}", "빈도 분석과 집단 비교에 사용")
        styles.chips_row([dl.label(c) if c in dl.LABELS else c for c in categorical] or ["없음"])
        groupable = dl.group_cols(df)
        styles.note(f"집단 비교 가능(고유값 2~30개): {len(groupable)}개")
        if not categorical:
            st.warning("범주형 변수가 없어 집단 비교와 빈도 분석을 할 수 없습니다.")

styles.section("C", "변수별 자료형·결측·고유값", bg=styles.YELLOW)
with st.container(key="card-quality"):
    st.dataframe(stats.quality_report(df), hide_index=True)
    if n_missing:
        styles.note("결측값은 각 분석에서 해당 변수의 값이 없는 행만 제외하고 계산하며, 각 화면에 유효 표본 수를 함께 표시합니다.")

st.page_link("pages/2_성취도_분석.py", label="다음: 성취도 분석 →", icon=":material/arrow_forward:")
