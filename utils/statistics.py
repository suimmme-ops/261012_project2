"""기술통계·집단 비교·상관분석 계산. 모든 값은 실제 데이터에서 계산한다."""

from __future__ import annotations

import numpy as np
import pandas as pd

from utils.data_loader import label, order_values

STAT_COLUMNS = ["Count", "Mean", "Median", "Std", "Min", "Q1", "Q3", "Max"]


def describe(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """변수별 기술통계 (결측 제외, 표준편차는 표본 표준편차 ddof=1)."""
    rows = []
    for col in cols:
        s = df[col].dropna()
        if s.empty:
            rows.append({"변수": label(col), "Count": 0})
            continue
        rows.append({
            "변수": label(col),
            "Count": int(s.count()),
            "Mean": s.mean(),
            "Median": s.median(),
            "Std": s.std() if len(s) > 1 else np.nan,
            "Min": s.min(),
            "Q1": s.quantile(0.25),
            "Q3": s.quantile(0.75),
            "Max": s.max(),
        })
    out = pd.DataFrame(rows).set_index("변수").reindex(columns=STAT_COLUMNS)
    return out.round(1)


def frequency(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """범주별 빈도와 비율(%). 결측은 별도 행으로 표시."""
    counts = df[col].value_counts(dropna=False)
    order = order_values(col, [v for v in counts.index if pd.notna(v)])
    if counts.index.isna().any():
        order.append(np.nan)
    counts = counts.reindex(order)
    out = pd.DataFrame({
        "값": ["(결측)" if pd.isna(v) else str(v) for v in counts.index],
        "빈도": counts.values.astype(int),
    })
    out["비율(%)"] = (out["빈도"] / out["빈도"].sum() * 100).round(1)
    return out


def modes(s: pd.Series) -> list:
    m = s.dropna().mode()
    return m.tolist()


def group_means(df: pd.DataFrame, group_col: str, cols: list[str]) -> pd.DataFrame:
    """집단별 학생 수(n)와 변수별 평균. 집단 값이 결측인 행은 제외."""
    data = df.dropna(subset=[group_col])
    if data.empty:
        return pd.DataFrame(columns=["n", *cols])
    g = data.groupby(group_col, observed=True)
    out = g[cols].mean()
    out.insert(0, "n", g.size())
    return out.reindex(order_values(group_col, out.index))


def to_long(gm: pd.DataFrame, cols: list[str], group_col: str) -> pd.DataFrame:
    """그래프용 긴 형식: group, variable, 과목, mean, n."""
    long = gm.reset_index().melt(id_vars=[group_col, "n"], value_vars=cols,
                                 var_name="variable", value_name="mean")
    long["과목"] = long["variable"].map(label)
    return long.rename(columns={group_col: "group"})


def group_insights(gm: pd.DataFrame, cols: list[str], target: str) -> dict | None:
    """최고/최저 평균 집단과 집단 간 차이가 가장 큰 변수. 집단이 2개 미만이면 None."""
    valid = gm.dropna(subset=[target])
    if len(valid) < 2:
        return None
    gaps = {c: valid[c].max() - valid[c].min() for c in cols if valid[c].notna().sum() >= 2}
    widest = max(gaps, key=gaps.get) if gaps else None
    hi, lo = valid[target].idxmax(), valid[target].idxmin()
    return {
        "top": hi, "top_value": valid.at[hi, target], "top_n": int(valid.at[hi, "n"]),
        "bottom": lo, "bottom_value": valid.at[lo, target], "bottom_n": int(valid.at[lo, "n"]),
        "spread": valid.at[hi, target] - valid.at[lo, target],
        "widest_col": widest, "widest_gap": gaps.get(widest) if widest else None,
    }


def pearson(df: pd.DataFrame, x: str, y: str) -> dict:
    """두 변수의 피어슨 상관계수. 계산할 수 없으면 reason에 이유를 담는다."""
    pair = df[[x, y]].dropna() if x != y else df[[x]].dropna().assign(_y=lambda d: d[x])
    n = len(pair)
    if n < 3:
        return {"r": None, "n": n, "reason": f"유효 표본이 {n}개로 너무 적어 상관계수를 계산할 수 없습니다 (최소 3개)."}
    a, b = pair.iloc[:, 0].to_numpy(float), pair.iloc[:, 1].to_numpy(float)
    if np.std(a) == 0 or np.std(b) == 0:
        return {"r": None, "n": n, "reason": "한 변수의 분산이 0(모든 값이 동일)이라 상관계수를 계산할 수 없습니다."}
    return {"r": float(np.corrcoef(a, b)[0, 1]), "n": n, "reason": None}


def corr_matrix(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    return df[cols].corr(method="pearson")


def strength(r: float) -> tuple[str, str]:
    """(방향, 강도) 한국어 표현. 기준: |r| <0.1 / 0.3 / 0.5 / 0.7."""
    a = abs(r)
    if a < 0.1:
        level = "거의 없는"
    elif a < 0.3:
        level = "약한"
    elif a < 0.5:
        level = "중간 정도의"
    elif a < 0.7:
        level = "강한"
    else:
        level = "매우 강한"
    direction = "양(+)의" if r > 0 else "음(−)의" if r < 0 else ""
    return direction, level


def linear_fit(df: pd.DataFrame, x: str, y: str) -> tuple[float, float] | None:
    pair = df[[x, y]].dropna()
    if len(pair) < 2 or pair[x].nunique() < 2:
        return None
    slope, intercept = np.polyfit(pair[x].to_numpy(float), pair[y].to_numpy(float), 1)
    return float(slope), float(intercept)


def quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """변수별 자료형·결측·고유값 요약."""
    return pd.DataFrame({
        "변수": df.columns,
        "자료형": [str(t) for t in df.dtypes],
        "결측값": df.isna().sum().values,
        "고유값 수": [df[c].nunique(dropna=True) for c in df.columns],
        "예시 값": [", ".join(map(str, df[c].dropna().unique()[:3])) for c in df.columns],
    })
