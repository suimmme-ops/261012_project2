"""Plotly 차트 디자인 시스템과 공통 차트 빌더."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import styles
from utils.data_loader import AVG_COL, TOTAL_COL, label

# 과목별 색상은 모든 페이지에서 동일하게 사용한다.
SUBJECT_COLORS = {
    "math score": styles.COBALT,
    "reading score": styles.PINK,
    "writing score": styles.VIOLET,
    AVG_COL: styles.INK,
    TOTAL_COL: styles.MUTED,
}
# 범주 색상: 팔레트 기반 (흰 배경 대비를 위해 노랑·라임은 진한 톤 사용)
CATEGORY_COLORS = ["#6C63FF", "#FF79B0", "#4688FF", "#E0A800", "#5E9E00",
                   "#1D1D1F", "#A39DFF", "#FF9F6B", "#7FB2FF", "#6B7280"]
SEQUENTIAL = [[0, "#F4F3FF"], [0.5, "#A9A3FF"], [1, "#3B33C4"]]
DIVERGING = [[0, styles.COBALT], [0.5, "#FFFFFF"], [1, styles.PINK]]

FONT = 'Pretendard, "Space Grotesk", -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", sans-serif'

PLOTLY_CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "scrollZoom": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    "toImageButtonOptions": {"format": "png", "filename": "student_insight_lab_chart", "scale": 2},
}


def color_for(col: str, i: int = 0) -> str:
    return SUBJECT_COLORS.get(col, CATEGORY_COLORS[i % len(CATEGORY_COLORS)])


def color_map(cols: list[str]) -> dict[str, str]:
    """변수명 → 색상, 한국어 레이블 → 색상 둘 다 제공."""
    out = {}
    for i, c in enumerate(cols):
        out[c] = color_for(c, i)
        out[label(c)] = color_for(c, i)
    return out


def category_map(values) -> dict:
    return {v: CATEGORY_COLORS[i % len(CATEGORY_COLORS)] for i, v in enumerate(values)}


def style(fig: go.Figure, height: int = 380, legend: bool = True) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, size=13, color=styles.INK),
        margin=dict(l=8, r=8, t=36 if legend else 12, b=8),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    title_text="", font=dict(size=12)),
        hoverlabel=dict(bgcolor=styles.INK, bordercolor=styles.INK,
                        font=dict(family=FONT, color="#FFFFFF", size=12.5)),
        bargap=0.25,
    )
    fig.update_xaxes(showgrid=False, linecolor=styles.LINE, ticks="", title_font=dict(size=12.5),
                     automargin=True)
    fig.update_yaxes(gridcolor="#EFEDE6", zeroline=True, zerolinecolor=styles.LINE,
                     title_font=dict(size=12.5), automargin=True)
    return fig


def show(fig: go.Figure, key: str) -> None:
    st.plotly_chart(fig, key=key, config=PLOTLY_CONFIG, theme=None)


# ---------------------------------------------------------------------------
# Builders

def mean_bar(stats: pd.DataFrame) -> go.Figure:
    """stats: columns variable, 과목, mean, n."""
    fig = px.bar(stats, x="과목", y="mean", color="variable", text="mean",
                 color_discrete_map=color_map(stats["variable"].tolist()),
                 custom_data=["n"])
    fig.update_traces(texttemplate="<b>%{y:.1f}</b>", textposition="outside", cliponaxis=False,
                      marker_line_color=styles.INK, marker_line_width=1.5,
                      hovertemplate="<b>%{x}</b><br>평균 %{y:.1f}점<br>유효 표본 %{customdata[0]:,}명<extra></extra>")
    top = float(stats["mean"].max()) if len(stats) else 0
    fig.update_yaxes(range=[0, max(top * 1.18, 1)], title="평균 점수")
    fig.update_xaxes(title=None)
    return style(fig, legend=False)


def histogram(df: pd.DataFrame, col: str, nbins: int) -> go.Figure:
    s = df[col].dropna()
    fig = px.histogram(df, x=col, nbins=nbins, color_discrete_sequence=[color_for(col)])
    fig.update_traces(marker_line_color=styles.INK, marker_line_width=1,
                      hovertemplate="구간 %{x}<br>학생 수 %{y:,}명<extra></extra>")
    if not s.empty:
        mean, median = s.mean(), s.median()
        fig.add_vline(x=mean, line_width=2.5, line_color=styles.INK,
                      annotation_text=f"평균 {mean:.1f}", annotation_position="top left",
                      annotation_font=dict(size=12, color=styles.INK))
        fig.add_vline(x=median, line_width=2.5, line_dash="dash", line_color="#E0A800",
                      annotation_text=f"중앙값 {median:.1f}", annotation_position="top right",
                      annotation_font=dict(size=12, color="#9A7400"))
    fig.update_xaxes(title=label(col))
    fig.update_yaxes(title="학생 수")
    return style(fig, legend=False)


def box(df: pd.DataFrame, cols: list[str]) -> go.Figure:
    long = df[cols].melt(var_name="variable", value_name="score").dropna()
    long["과목"] = long["variable"].map(label)
    fig = px.box(long, x="과목", y="score", color="variable", points="outliers",
                 color_discrete_map=color_map(cols))
    fig.update_traces(marker=dict(size=6, line=dict(width=1, color=styles.INK)), line_width=2)
    fig.update_xaxes(title=None)
    fig.update_yaxes(title="점수")
    return style(fig, legend=False)


def frequency_bar(freq: pd.DataFrame, col: str) -> go.Figure:
    fig = px.bar(freq, x="값", y="빈도", text="비율(%)", color="값",
                 color_discrete_map=category_map(freq["값"].tolist()))
    fig.update_traces(texttemplate="%{y:,} · %{text:.1f}%", textposition="outside", cliponaxis=False,
                      marker_line_color=styles.INK, marker_line_width=1.2,
                      hovertemplate="<b>%{x}</b><br>빈도 %{y:,}<br>비율 %{text:.1f}%<extra></extra>")
    fig.update_yaxes(range=[0, freq["빈도"].max() * 1.2 if len(freq) else 1], title="빈도")
    fig.update_xaxes(title=label(col), type="category")
    return style(fig, legend=False)


def grouped_bar(long: pd.DataFrame, group_title: str) -> go.Figure:
    variables = long["variable"].unique().tolist()
    fig = px.bar(long, x="group", y="mean", color="과목", barmode="group", text="mean",
                 color_discrete_map=color_map(variables), custom_data=["n", "과목"])
    fig.update_traces(texttemplate="%{y:.1f}", textposition="outside", cliponaxis=False,
                      textfont_size=11, marker_line_color=styles.INK, marker_line_width=1,
                      hovertemplate="<b>%{x}</b> · %{customdata[1]}<br>평균 %{y:.1f}<br>n = %{customdata[0]:,}<extra></extra>")
    top = float(long["mean"].max()) if len(long) else 0
    fig.update_yaxes(range=[0, max(top * 1.15, 1)], title="평균")
    fig.update_xaxes(title=group_title, type="category")
    return style(fig, height=420)


def heatmap(gm: pd.DataFrame, cols: list[str], group_title: str) -> go.Figure:
    z = gm[cols]
    y_labels = [f"{g} (n={int(n):,})" for g, n in zip(gm.index, gm["n"])]
    fig = px.imshow(z.to_numpy(), x=[label(c) for c in cols], y=y_labels,
                    color_continuous_scale=SEQUENTIAL, aspect="auto", text_auto=".1f",
                    labels=dict(color="평균"))
    fig.update_traces(hovertemplate="<b>%{y}</b><br>%{x} 평균 %{z:.1f}<extra></extra>",
                      xgap=3, ygap=3, textfont=dict(size=13))
    fig.update_xaxes(side="top", title=None)
    fig.update_yaxes(title=group_title, autorange="reversed")
    fig = style(fig, height=max(260, 70 + 48 * len(gm)), legend=False)
    fig.update_layout(coloraxis_colorbar=dict(thickness=12, len=0.8, title=dict(text="평균")))
    return fig


def dumbbell(a_name: str, a_means: pd.Series, b_name: str, b_means: pd.Series, cols: list[str]) -> go.Figure:
    ys = [label(c) for c in cols]
    fig = go.Figure()
    for c, y in zip(cols, ys):
        fig.add_trace(go.Scatter(x=[a_means[c], b_means[c]], y=[y, y], mode="lines",
                                 line=dict(color=color_for(c), width=6), showlegend=False,
                                 hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=a_means[cols], y=ys, mode="markers+text", name=str(a_name),
                             marker=dict(size=18, color=styles.INK, symbol="circle",
                                         line=dict(width=2, color=styles.INK)),
                             text=[f"{v:.1f}" for v in a_means[cols]], textposition="top center",
                             hovertemplate=f"<b>{a_name}</b><br>%{{y}} 평균 %{{x:.1f}}<extra></extra>"))
    fig.add_trace(go.Scatter(x=b_means[cols], y=ys, mode="markers+text", name=str(b_name),
                             marker=dict(size=18, color=styles.YELLOW, symbol="diamond",
                                         line=dict(width=2, color=styles.INK)),
                             text=[f"{v:.1f}" for v in b_means[cols]], textposition="bottom center",
                             hovertemplate=f"<b>{b_name}</b><br>%{{y}} 평균 %{{x:.1f}}<extra></extra>"))
    fig.update_xaxes(title="평균", showgrid=True, gridcolor="#EFEDE6")
    fig.update_yaxes(title=None, type="category", autorange="reversed")
    return style(fig, height=120 + 80 * len(cols))


def compare_hist(df: pd.DataFrame, group_col: str, a, b, value: str) -> go.Figure:
    data = df[df[group_col].isin([a, b])].dropna(subset=[value])
    fig = px.histogram(data, x=value, color=group_col, barmode="overlay", histnorm="percent",
                       nbins=20, opacity=0.65, category_orders={group_col: [a, b]},
                       color_discrete_map={a: styles.INK, b: styles.YELLOW})
    fig.update_traces(marker_line_color=styles.INK, marker_line_width=1,
                      hovertemplate="구간 %{x}<br>비율 %{y:.1f}%<extra></extra>")
    fig.update_xaxes(title=label(value))
    fig.update_yaxes(title="집단 내 비율(%)")
    return style(fig)


def group_box(df: pd.DataFrame, group_col: str, value: str, order: list) -> go.Figure:
    data = df.dropna(subset=[group_col, value])
    fig = px.box(data, x=group_col, y=value, color=group_col, points="outliers",
                 category_orders={group_col: order}, color_discrete_map=category_map(order))
    fig.update_traces(line_width=2, marker=dict(size=5, line=dict(width=1, color=styles.INK)))
    fig.update_xaxes(title=label(group_col), type="category")
    fig.update_yaxes(title=label(value))
    return style(fig, legend=False)


def corr_heatmap(corr: pd.DataFrame) -> go.Figure:
    names = [label(c) for c in corr.columns]
    fig = px.imshow(corr.to_numpy(), x=names, y=names, zmin=-1, zmax=1,
                    color_continuous_scale=DIVERGING, text_auto=".3f", aspect="auto")
    fig.update_traces(hovertemplate="%{y} × %{x}<br>r = %{z:.3f}<extra></extra>",
                      xgap=4, ygap=4, textfont=dict(size=15))
    fig.update_xaxes(side="top", title=None)
    fig.update_yaxes(title=None)
    fig = style(fig, height=max(320, 90 + 80 * len(names)), legend=False)
    fig.update_layout(coloraxis_colorbar=dict(thickness=12, len=0.85, title=dict(text="r")))
    return fig


def scatter(df: pd.DataFrame, x: str, y: str, color: str | None, fit: tuple[float, float] | None,
            order: list | None = None) -> go.Figure:
    data = df.dropna(subset=[x, y] + ([color] if color else []))
    kwargs = {}
    if color:
        order = order or sorted(data[color].unique(), key=str)
        kwargs = dict(color=color, category_orders={color: order}, color_discrete_map=category_map(order))
    else:
        kwargs = dict(color_discrete_sequence=[styles.VIOLET])
    fig = px.scatter(data, x=x, y=y, opacity=0.7, labels={x: label(x), y: label(y)}, **kwargs)
    fig.update_traces(marker=dict(size=8, line=dict(width=0.8, color=styles.INK)))
    if fit:
        slope, intercept = fit
        xs = np.linspace(data[x].min(), data[x].max(), 50)
        fig.add_trace(go.Scatter(x=xs, y=slope * xs + intercept, mode="lines", name="선형 추세선",
                                 line=dict(color=styles.INK, width=3, dash="dash"),
                                 hovertemplate=f"추세선<br>y = {slope:.2f}x + {intercept:.2f}<extra></extra>"))
    fig.update_xaxes(title=label(x))
    fig.update_yaxes(title=label(y))
    return style(fig, height=460)
