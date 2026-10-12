"""CSV 로드·전처리, 페이지 간 데이터 공유(session_state), 전역 필터."""

from __future__ import annotations

import hashlib
import io
import math
from pathlib import Path

import pandas as pd
import streamlit as st

from utils import styles

# ---------------------------------------------------------------------------
# Dataset schema

SCORE_COLS = ["math score", "reading score", "writing score"]
GROUP_COLS = [
    "gender",
    "race/ethnicity",
    "parental level of education",
    "lunch",
    "test preparation course",
]
AVG_COL = "average score"
TOTAL_COL = "total score"

SAMPLE_PATH = Path(__file__).resolve().parent.parent / "data" / "StudentsPerformance.csv"

LABELS = {
    "gender": "성별",
    "race/ethnicity": "인종·민족 그룹",
    "parental level of education": "부모 교육 수준",
    "lunch": "점심 지원 유형",
    "test preparation course": "시험 준비 과정",
    "math score": "수학",
    "reading score": "읽기",
    "writing score": "쓰기",
    AVG_COL: "3과목 평균",
    TOTAL_COL: "3과목 총점",
}

# 순서가 의미 있는 범주(원본 값은 그대로 두고 표시 순서만 정한다)
CATEGORY_ORDER = {
    "gender": ["female", "male"],
    "parental level of education": [
        "some high school",
        "high school",
        "some college",
        "associate's degree",
        "bachelor's degree",
        "master's degree",
    ],
    "lunch": ["standard", "free/reduced"],
    "test preparation course": ["none", "completed"],
}

ENCODINGS = ("utf-8-sig", "cp949", "euc-kr", "latin-1")

# 데이터에 종속된 세션 키 접두사 (새 데이터가 들어오면 모두 초기화)
_DATA_KEY_PREFIXES = ("flt_", "_w_", "pg")


class DataError(Exception):
    """사용자에게 그대로 보여줄 수 있는 데이터 오류."""


def label(col: str) -> str:
    return LABELS.get(col, col)


def order_values(col: str, values) -> list:
    """알려진 범주는 의미 순서로, 나머지는 문자열 순으로 정렬."""
    values = list(values)
    known = [v for v in CATEGORY_ORDER.get(col, []) if v in values]
    rest = sorted((v for v in values if v not in known), key=str)
    return known + rest


# ---------------------------------------------------------------------------
# Loading & preprocessing

@st.cache_data(show_spinner=False)
def _read_csv(raw: bytes) -> tuple[pd.DataFrame, str]:
    if not raw or not raw.strip():
        raise DataError("빈 파일입니다. 내용이 있는 CSV 파일을 업로드하세요.")
    for enc in ENCODINGS:
        try:
            return pd.read_csv(io.BytesIO(raw), encoding=enc), enc
        except UnicodeDecodeError:
            continue
        except pd.errors.EmptyDataError:
            raise DataError("CSV에서 읽을 수 있는 열이나 행이 없습니다.") from None
        except pd.errors.ParserError as e:
            raise DataError(f"CSV 형식을 해석할 수 없습니다. 구분자와 따옴표를 확인하세요. ({e})") from None
    raise DataError("지원하는 인코딩(UTF-8, CP949, EUC-KR)으로 파일을 읽을 수 없습니다.")


def _is_text(s: pd.Series) -> bool:
    return not (
        pd.api.types.is_numeric_dtype(s)
        or pd.api.types.is_bool_dtype(s)
        or pd.api.types.is_datetime64_any_dtype(s)
    )


def prepare(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """원본 값은 바꾸지 않고, 자료형 정리와 파생 변수(평균·총점)만 추가."""
    df = raw_df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    if df.shape[1] == 0 or df.empty:
        raise DataError("데이터 행이 없습니다. 헤더 아래에 데이터가 있는지 확인하세요.")

    # 모든 값이 숫자로 해석되는 텍스트 열만 숫자형으로 변환 (값 손실 없음)
    converted = []
    for col in df.columns:
        s = df[col]
        if not _is_text(s) or s.dropna().empty:
            continue
        stripped = s.astype("string").str.strip()
        num = pd.to_numeric(stripped, errors="coerce")
        if num[stripped.notna()].notna().all():
            df[col] = num.astype("float64")
            converted.append(col)

    # 점수 열은 숫자형으로 강제 변환 (숫자가 아닌 값은 결측 처리)
    coerced = {}
    derived = []
    if all(c in df.columns for c in SCORE_COLS):
        for c in SCORE_COLS:
            before = df[c].notna().sum()
            df[c] = pd.to_numeric(df[c], errors="coerce")
            lost = int(before - df[c].notna().sum())
            if lost:
                coerced[c] = lost
        if AVG_COL not in df.columns:
            df[AVG_COL] = df[SCORE_COLS].mean(axis=1, skipna=False)
            derived.append(AVG_COL)
        if TOTAL_COL not in df.columns:
            df[TOTAL_COL] = df[SCORE_COLS].sum(axis=1, min_count=len(SCORE_COLS))
            derived.append(TOTAL_COL)

    return df, {"converted": converted, "coerced": coerced, "derived": derived}


def column_types(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    numeric = [c for c in df.columns
               if pd.api.types.is_numeric_dtype(df[c]) and not pd.api.types.is_bool_dtype(df[c])]
    categorical = [c for c in df.columns if c not in numeric]
    return numeric, categorical


def is_student(df: pd.DataFrame) -> bool:
    """학생 성적 데이터 전용 기능을 켤 수 있는지 (필수 열 존재 여부)."""
    return all(c in df.columns for c in SCORE_COLS + GROUP_COLS)


def missing_required(df: pd.DataFrame) -> list[str]:
    return [c for c in SCORE_COLS + GROUP_COLS if c not in df.columns]


def value_cols(df: pd.DataFrame) -> list[str]:
    """분석 대상 숫자형 변수: 학생 데이터면 3과목, 아니면 모든 숫자형 열."""
    if all(c in df.columns for c in SCORE_COLS):
        return list(SCORE_COLS)
    return column_types(df)[0]


def group_cols(df: pd.DataFrame) -> list[str]:
    """집단 비교에 쓸 범주형 변수 (고유값 2~30개)."""
    if is_student(df):
        return list(GROUP_COLS)
    _, cats = column_types(df)
    return [c for c in cats if 2 <= df[c].nunique(dropna=True) <= 30]


# ---------------------------------------------------------------------------
# Session state

def _reset_data_state() -> None:
    for key in list(st.session_state.keys()):
        if str(key).startswith(_DATA_KEY_PREFIXES):
            del st.session_state[key]


def load_bytes(raw: bytes, name: str) -> None:
    """CSV 바이트를 읽어 세션에 저장. 실패 시 DataError."""
    raw_df, encoding = _read_csv(raw)
    df, info = prepare(raw_df)
    _reset_data_state()
    st.session_state["df"] = df
    st.session_state["data_name"] = name
    st.session_state["data_encoding"] = encoding
    st.session_state["data_info"] = info
    st.session_state["data_sig"] = hashlib.md5(raw).hexdigest()


def load_sample() -> None:
    """버튼 콜백: 프로젝트에 포함된 샘플 CSV 사용."""
    st.session_state.pop("load_error", None)
    if not SAMPLE_PATH.exists():
        st.session_state["load_error"] = "샘플 파일(data/StudentsPerformance.csv)을 찾을 수 없습니다. CSV를 직접 업로드하세요."
        return
    try:
        load_bytes(SAMPLE_PATH.read_bytes(), SAMPLE_PATH.name)
    except DataError as e:
        st.session_state["load_error"] = str(e)


def clear_data() -> None:
    _reset_data_state()
    for key in ("df", "data_name", "data_encoding", "data_info", "data_sig", "load_error"):
        st.session_state.pop(key, None)


def get_df() -> pd.DataFrame | None:
    return st.session_state.get("df")


def require_data() -> pd.DataFrame:
    """데이터가 없으면 Empty State를 보여주고 페이지 실행을 멈춘다."""
    df = get_df()
    if df is not None:
        return df
    styles.empty_state("📂", "아직 데이터가 없어요", "CSV를 업로드하거나 샘플 데이터로 바로 시작해 보세요.")
    c1, c2, _ = st.columns([1, 1, 2])
    with c1:
        st.page_link("pages/1_데이터_업로드.py", label="CSV 업로드하러 가기", icon=":material/upload_file:")
    with c2:
        st.button("샘플 데이터로 시작", type="primary", on_click=load_sample, key="sample_from_empty")
    if st.session_state.get("load_error"):
        st.error(st.session_state["load_error"])
    st.stop()


# ---------------------------------------------------------------------------
# Global filters (AND between filters, OR within a filter)

def filter_columns(df: pd.DataFrame) -> list[str]:
    return group_cols(df)[:6]


def _range_spec(df: pd.DataFrame):
    """점수 범위 슬라이더 대상 열과 경계값."""
    if AVG_COL in df.columns:
        col = AVG_COL
    else:
        nums = value_cols(df)
        if not nums:
            return None
        col = nums[0]
    s = df[col].dropna()
    if s.empty or s.min() == s.max():
        return None
    lo, hi = float(s.min()), float(s.max())
    as_int = pd.api.types.is_integer_dtype(df[col]) or (hi - lo) >= 20
    if as_int:
        lo, hi = math.floor(lo), math.ceil(hi)
    return col, lo, hi, as_int


def _sync(persist_key: str, widget_key: str) -> None:
    st.session_state[persist_key] = st.session_state[widget_key]


def reset_filters() -> None:
    for key in list(st.session_state.keys()):
        if str(key).startswith("flt_"):
            del st.session_state[key]


def render_filters(df: pd.DataFrame) -> None:
    """사이드바 전역 필터. 값은 flt_* 키에 저장되어 페이지를 이동해도 유지된다."""
    ss = st.session_state
    with st.sidebar:
        styles._html('<div class="sil-side-label">GLOBAL FILTERS</div>')
        for col in filter_columns(df):
            options = order_values(col, df[col].dropna().unique())
            pk, wk = f"flt_{col}", f"_w_flt_{col}"
            ss[wk] = [v for v in ss.get(pk, []) if v in options]
            st.multiselect(label(col), options, key=wk, placeholder="전체",
                           on_change=_sync, args=(pk, wk))

        spec = _range_spec(df)
        if spec:
            col, lo, hi, as_int = spec
            pk, wk = "flt_range", "_w_flt_range"
            cur = ss.get(pk, (lo, hi))
            cur = (max(lo, min(cur[0], hi)), min(hi, max(cur[1], lo)))
            if as_int:
                ss[wk] = (int(cur[0]), int(cur[1]))
                st.slider(f"{label(col)} 범위", int(lo), int(hi), key=wk, step=1,
                          on_change=_sync, args=(pk, wk))
            else:
                ss[wk] = (float(cur[0]), float(cur[1]))
                st.slider(f"{label(col)} 범위", float(lo), float(hi), key=wk,
                          step=(hi - lo) / 100, on_change=_sync, args=(pk, wk))

        st.button("필터 초기화", icon=":material/restart_alt:", on_click=reset_filters,
                  key="reset_filters", width="stretch")


def apply_filters(df: pd.DataFrame, ignore: tuple[str, ...] = ()) -> pd.DataFrame:
    ss = st.session_state
    mask = pd.Series(True, index=df.index)
    for col in filter_columns(df):
        selected = ss.get(f"flt_{col}") or []
        if col not in ignore and selected:
            mask &= df[col].isin(selected)
    spec = _range_spec(df)
    if spec and "flt_range" in ss:
        col, lo, hi, _ = spec
        a, b = ss["flt_range"]
        if (a, b) != (lo, hi):
            mask &= df[col].between(a, b)
    return df[mask]


def active_filters(df: pd.DataFrame, ignore: tuple[str, ...] = ()) -> list[str]:
    ss = st.session_state
    items = []
    for col in filter_columns(df):
        selected = ss.get(f"flt_{col}") or []
        if col not in ignore and selected:
            items.append(f"{label(col)}: {', '.join(map(str, selected))}")
    spec = _range_spec(df)
    if spec and "flt_range" in ss:
        col, lo, hi, as_int = spec
        a, b = ss["flt_range"]
        if (a, b) != (lo, hi):
            items.append(f"{label(col)}: {a:g}~{b:g}" if not as_int else f"{label(col)}: {int(a)}~{int(b)}")
    return items


def filter_bar(df: pd.DataFrame, fdf: pd.DataFrame, ignore: tuple[str, ...] = ()) -> None:
    """현재 필터 상태와 분석에 사용된 표본 수 표시."""
    items = active_filters(df, ignore)
    styles.chips_row(
        items or ["필터 없음 · 전체 데이터"],
        prefix=f"분석 대상 {len(fdf):,} / {len(df):,}행 ·",
    )


def sidebar_download(fdf: pd.DataFrame) -> None:
    with st.sidebar:
        st.download_button(
            "필터링된 데이터 CSV",
            fdf.to_csv(index=False).encode("utf-8-sig"),
            file_name="filtered_data.csv",
            mime="text/csv",
            icon=":material/download:",
            key="dl_filtered",
            width="stretch",
            disabled=fdf.empty,
            on_click="ignore",
        )


def use_filtered_data(ignore: tuple[str, ...] = ()) -> tuple[pd.DataFrame, pd.DataFrame]:
    """분석 페이지 공통: 데이터 확인 → 전역 필터 → 다운로드 → (원본, 필터 결과)."""
    df = require_data()
    render_filters(df)
    fdf = apply_filters(df, ignore)
    sidebar_download(apply_filters(df))
    return df, fdf


def stop_if_empty(fdf: pd.DataFrame) -> None:
    if fdf.empty:
        styles.empty_state("🫥", "조건에 맞는 학생이 없어요",
                           "필터 조합을 줄이거나 사이드바의 '필터 초기화'를 눌러 보세요.")
        st.stop()
