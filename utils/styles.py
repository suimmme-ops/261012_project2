"""디자인 시스템: 컬러 토큰, 전역 CSS, 공통 UI 컴포넌트(HTML)."""

from __future__ import annotations

from html import escape

import streamlit as st

# ---------------------------------------------------------------------------
# Design tokens

LIME = "#C7F36B"
VIOLET = "#6C63FF"
PINK = "#FF79B0"
COBALT = "#4688FF"
YELLOW = "#FFD45A"
PAPER = "#FFFDF7"
WHITE = "#FFFFFF"
INK = "#1D1D1F"
MUTED = "#6B7280"
LINE = "#E8E8E8"

FONT_STACK = (
    '"Pretendard", "Pretendard Variable", -apple-system, BlinkMacSystemFont, '
    '"Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", "Segoe UI", sans-serif'
)
DISPLAY_STACK = f'"Space Grotesk", {FONT_STACK}'

PAGES = [
    ("streamlit_app.py", "HOME · 데이터셋 소개", ":material/home:"),
    ("pages/1_데이터_업로드.py", "01 · 데이터 업로드", ":material/upload_file:"),
    ("pages/2_성취도_분석.py", "02 · 성취도 분석", ":material/bar_chart:"),
    ("pages/3_집단별_비교.py", "03 · 집단별 비교", ":material/groups:"),
    ("pages/4_상관관계_탐색.py", "04 · 상관관계 탐색", ":material/scatter_plot:"),
    ("pages/5_인사이트_탐구.py", "05 · 인사이트 탐구", ":material/insights:"),
]

_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');

:root {{
  --lime:{LIME}; --violet:{VIOLET}; --pink:{PINK}; --cobalt:{COBALT}; --yellow:{YELLOW};
  --paper:{PAPER}; --white:{WHITE}; --ink:{INK}; --muted:{MUTED}; --line:{LINE};
  --font-ko:{FONT_STACK}; --font-display:{DISPLAY_STACK};
  --radius:18px;
}}

/* ---------- Base typography ---------- */
.stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea,
.stApp button, .stApp td, .stApp th, [data-testid="stMarkdownContainer"] {{
  font-family: var(--font-ko);
}}
.stApp {{ background: var(--paper); color: var(--ink); }}
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
  font-family: var(--font-display); letter-spacing: -0.02em; color: var(--ink);
}}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 2.2rem; padding-bottom: 4rem; max-width: 1280px; }}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {{ background: #F6F3EA; border-right: 1px solid var(--line); }}
[data-testid="stSidebar"] [data-testid="stPageLink"] a {{ border-radius: 999px; }}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {{ background: rgba(108,99,255,.10); }}

/* ---------- Cards (st.container(key=...)) ---------- */
[class*="st-key-card"] {{
  background: var(--white); border: 1px solid var(--line); border-radius: var(--radius);
  padding: 20px 22px 16px; box-shadow: 0 2px 0 rgba(29,29,31,.03);
}}
[class*="st-key-brut"] {{
  background: var(--white); border: 2px solid var(--ink); border-radius: var(--radius);
  padding: 20px 22px 16px; box-shadow: 6px 6px 0 var(--ink);
}}
[class*="st-key-tint"] {{
  background: #F4F3FF; border: 2px solid var(--ink); border-radius: var(--radius);
  padding: 20px 22px 16px; box-shadow: 6px 6px 0 var(--violet);
}}

/* ---------- Buttons ---------- */
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-secondary"] {{
  border: 2px solid var(--ink) !important; border-radius: 999px !important;
  font-weight: 700 !important; box-shadow: 3px 3px 0 var(--ink);
  transition: transform .08s ease, box-shadow .08s ease;
}}
[data-testid="stBaseButton-secondary"] {{ background: var(--white) !important; color: var(--ink) !important; }}
[data-testid="stBaseButton-primary"] {{ background: var(--violet) !important; color: var(--white) !important; }}
[data-testid="stBaseButton-primary"]:hover, [data-testid="stBaseButton-secondary"]:hover {{
  transform: translate(-1px,-1px); box-shadow: 4px 4px 0 var(--ink);
}}
[data-testid="stBaseButton-primary"]:active, [data-testid="stBaseButton-secondary"]:active {{
  transform: translate(2px,2px); box-shadow: 1px 1px 0 var(--ink);
}}
[data-testid="stBaseButton-primary"]:focus-visible, [data-testid="stBaseButton-secondary"]:focus-visible {{
  outline: 3px solid var(--yellow); outline-offset: 2px;
}}

/* ---------- File uploader ---------- */
[data-testid="stFileUploaderDropzone"] {{
  min-height: 170px; border: 2px dashed var(--violet); border-radius: var(--radius);
  background: #F4F3FF;
}}

/* ---------- Custom HTML components ---------- */
.sil-hero {{
  position: relative; overflow: hidden; background: var(--lime); border: 2px solid var(--ink);
  border-radius: 24px; padding: 40px 36px 34px; box-shadow: 8px 8px 0 var(--ink); margin-bottom: 12px;
}}
.sil-hero__title {{
  font-family: var(--font-display) !important; font-weight: 700; font-size: clamp(40px, 7vw, 64px);
  line-height: .95; letter-spacing: -0.04em; margin: 14px 0 12px; color: var(--ink); padding: 0;
}}
.sil-hero__sub {{ font-family: var(--font-display); font-weight: 700; font-size: 18px; letter-spacing: .04em; margin: 0; }}
.sil-hero__body {{ max-width: 680px; font-size: 15.5px; line-height: 1.7; margin-top: 18px; }}

.sil-page {{ position: relative; padding: 4px 0 6px; margin-bottom: 8px; }}
.sil-page__title {{
  font-family: var(--font-display) !important; font-weight: 700; font-size: clamp(30px, 4.6vw, 44px);
  line-height: 1.02; letter-spacing: -0.035em; margin: 12px 0 10px; padding: 0; max-width: 900px;
}}
.sil-page__title mark {{ background: var(--accent, var(--lime)); padding: 0 .12em; border-radius: 6px; color: var(--ink); }}
.sil-page__desc {{ color: var(--muted); font-size: 15px; max-width: 720px; margin: 0; }}

.sil-pill {{
  display: inline-block; padding: 5px 12px; border-radius: 999px; border: 2px solid var(--ink);
  background: var(--bg, var(--white)); color: var(--fg, var(--ink));
  font-family: var(--font-display); font-weight: 700; font-size: 12px; letter-spacing: .06em; margin: 0 6px 6px 0;
}}
.sil-chip {{
  display: inline-block; padding: 4px 10px; border-radius: 999px; background: #EFEDE4;
  font-size: 12.5px; margin: 0 6px 6px 0; color: var(--ink);
}}

.sil-sec {{ display: flex; gap: 14px; align-items: flex-start; margin: 26px 0 12px; }}
.sil-sec__no {{
  flex: 0 0 auto; width: 38px; height: 38px; border-radius: 10px; border: 2px solid var(--ink);
  background: var(--bg, var(--yellow)); display: grid; place-items: center;
  font-family: var(--font-display); font-weight: 700; font-size: 17px; box-shadow: 3px 3px 0 var(--ink);
}}
.sil-sec__title {{ font-family: var(--font-display); font-weight: 700; font-size: clamp(20px, 2.6vw, 26px); letter-spacing: -0.02em; line-height: 1.15; margin: 2px 0 2px; }}
.sil-sec__desc {{ color: var(--muted); font-size: 14px; margin: 0; }}

.sil-card-title {{ font-family: var(--font-display); font-weight: 700; font-size: 18px; margin: 0 0 2px; letter-spacing: -0.01em; }}
.sil-card-desc {{ color: var(--muted); font-size: 13px; margin: 0 0 6px; }}

.sil-kpi {{
  background: var(--bg, var(--white)); color: var(--fg, var(--ink)); border-radius: var(--radius);
  border: 2px solid var(--ink); padding: 16px 18px 14px; min-height: 132px;
  display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 14px;
}}
.sil-kpi--soft {{ border: 1px solid var(--line); }}
.sil-kpi__label {{ font-family: var(--font-display); font-weight: 700; font-size: 12px; letter-spacing: .08em; text-transform: uppercase; opacity: .85; }}
.sil-kpi__value {{ font-family: var(--font-display); font-weight: 700; font-size: clamp(34px, 4vw, 50px); line-height: 1; letter-spacing: -0.04em; margin-top: 10px; }}
.sil-kpi__sub {{ font-size: 12.5px; margin-top: 8px; opacity: .85; }}

.sil-insight {{
  position: relative; background: var(--bg, var(--yellow)); border: 2px solid var(--ink); border-radius: var(--radius);
  padding: 18px 20px 16px; box-shadow: 5px 5px 0 var(--ink); margin-bottom: 16px; color: var(--ink);
}}
.sil-insight__big {{ font-family: var(--font-display); font-weight: 700; font-size: clamp(30px, 3.6vw, 44px); letter-spacing: -0.03em; line-height: 1; margin: 6px 0 8px; }}
.sil-insight__text {{ font-size: 14.5px; line-height: 1.6; margin: 0; }}
.sil-insight__tag {{ font-family: var(--font-display); font-weight: 700; font-size: 12px; letter-spacing: .08em; }}
.sil-insight__sticker {{
  position: absolute; top: -14px; right: 14px; width: 34px; height: 34px; background: var(--white);
  border: 2px solid var(--ink); border-radius: 50%; display: grid; place-items: center; font-size: 16px;
}}

.sil-info {{
  background: var(--white); border-radius: var(--radius); border: 1px solid var(--line);
  padding: 18px 18px 16px; height: 100%; min-height: 150px; margin-bottom: 14px;
}}
.sil-info__tag {{ display: inline-block; width: 12px; height: 12px; border-radius: 4px; background: var(--bg, var(--violet)); border: 2px solid var(--ink); margin-right: 8px; vertical-align: -1px; }}
.sil-info__name {{ font-family: var(--font-display); font-weight: 700; font-size: 16px; }}
.sil-info__ko {{ color: var(--muted); font-size: 13px; margin: 4px 0 8px; }}
.sil-info__text {{ font-size: 13.5px; line-height: 1.55; margin: 0; }}

.sil-empty {{
  text-align: center; background: var(--white); border: 2px dashed var(--ink); border-radius: 24px;
  padding: 42px 24px; margin: 12px 0 18px;
}}
.sil-empty__icon {{ font-size: 44px; }}
.sil-empty__title {{ font-family: var(--font-display); font-weight: 700; font-size: 24px; margin: 8px 0 6px; }}
.sil-empty__text {{ color: var(--muted); font-size: 14.5px; margin: 0; }}

.sil-note {{ font-size: 12.5px; color: var(--muted); margin: 4px 0 0; }}
.sil-brand {{ font-family: var(--font-display); font-weight: 700; font-size: 20px; letter-spacing: -0.02em; line-height: 1.05; margin: 2px 0 2px; }}
.sil-brand span {{ background: var(--lime); padding: 0 4px; border-radius: 4px; }}
.sil-side-label {{ font-family: var(--font-display); font-weight: 700; font-size: 11.5px; letter-spacing: .12em; color: var(--muted); margin: 14px 0 6px; }}

/* Geometric stickers */
.sil-shape {{ position: absolute; border: 2px solid var(--ink); }}
.sil-shape--circle {{ width: 92px; height: 92px; border-radius: 50%; background: var(--pink); top: 26px; right: 120px; }}
.sil-shape--square {{ width: 70px; height: 70px; border-radius: 14px; background: var(--cobalt); top: 92px; right: 40px; transform: rotate(14deg); }}
.sil-shape--star {{
  width: 78px; height: 78px; background: var(--yellow); top: 150px; right: 150px; border: none;
  clip-path: polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%);
}}
.sil-shape--ring {{ width: 46px; height: 46px; border-radius: 50%; background: transparent; border-width: 6px; border-color: var(--violet); top: 24px; right: 34px; }}
.sil-shape--small {{ transform: scale(.6); transform-origin: top right; }}

/* ---------- Responsive ---------- */
@media (max-width: 900px) {{
  .sil-hero {{ padding: 30px 22px 26px; }}
  .sil-shape {{ opacity: .35; }}
}}
@media (max-width: 640px) {{
  .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
  .sil-hero {{ box-shadow: 5px 5px 0 var(--ink); }}
  .sil-shape--star, .sil-shape--square {{ display: none; }}
  .sil-kpi {{ min-height: 112px; }}
  [class*="st-key-brut"], [class*="st-key-tint"] {{ box-shadow: 4px 4px 0 var(--ink); padding: 16px; }}
  [class*="st-key-card"] {{ padding: 16px; }}
}}
</style>
"""


def _html(markup: str) -> None:
    """들여쓰기가 마크다운 코드 블록으로 바뀌지 않도록 줄을 합쳐서 렌더링."""
    st.markdown("".join(line.strip() for line in markup.splitlines()), unsafe_allow_html=True)


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def setup_page(title: str, icon: str = "🧪") -> None:
    """모든 페이지 공통: 페이지 설정 + CSS + 사이드바 내비게이션."""
    st.set_page_config(
        page_title=f"{title} · Student Insight Lab",
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()
    sidebar_nav()


def sidebar_nav() -> None:
    with st.sidebar:
        _html('<div class="sil-brand">STUDENT<br><span>INSIGHT</span> LAB</div>'
              '<div class="sil-note">EXPLORE DATA. DISCOVER INSIGHTS.</div>')
        _html('<div class="sil-side-label">NAVIGATE</div>')
        for path, label, icon in PAGES:
            st.page_link(path, label=label, icon=icon)

        df = st.session_state.get("df")
        _html('<div class="sil-side-label">DATA STATUS</div>')
        if df is None:
            _html(pill("NO DATA", bg=WHITE) + '<div class="sil-note">01 페이지에서 CSV를 업로드하세요.</div>')
        else:
            name = escape(str(st.session_state.get("data_name", "data.csv")))
            _html(pill("LOADED", bg=LIME) + f'<div class="sil-note">{name}<br>'
                  f'{len(df):,}행 × {df.shape[1]}열</div>')


# ---------------------------------------------------------------------------
# HTML components

def pill(text: str, bg: str = WHITE, fg: str = INK) -> str:
    return f'<span class="sil-pill" style="--bg:{bg};--fg:{fg}">{escape(text)}</span>'


def chip(text: str) -> str:
    return f'<span class="sil-chip">{escape(text)}</span>'


def hero(kicker: str, title_html: str, subtitle: str, body: str = "") -> None:
    body_html = f'<div class="sil-hero__body">{body}</div>' if body else ""
    _html(f"""
    <div class="sil-hero">
      <div class="sil-shape sil-shape--circle"></div>
      <div class="sil-shape sil-shape--square"></div>
      <div class="sil-shape sil-shape--star"></div>
      <div class="sil-shape sil-shape--ring"></div>
      {pill(kicker, bg=WHITE)}
      <h1 class="sil-hero__title">{title_html}</h1>
      <p class="sil-hero__sub">{escape(subtitle)}</p>
      {body_html}
    </div>
    """)


def page_header(number: str, kicker: str, title_html: str, desc: str, accent: str = LIME) -> None:
    _html(f"""
    <div class="sil-page" style="--accent:{accent}">
      {pill(f"PAGE {number}", bg=INK, fg=WHITE)}{pill(kicker, bg=accent)}
      <h1 class="sil-page__title">{title_html}</h1>
      <p class="sil-page__desc">{escape(desc)}</p>
    </div>
    """)


def section(marker: str, title: str, desc: str = "", bg: str = YELLOW) -> None:
    desc_html = f'<p class="sil-sec__desc">{escape(desc)}</p>' if desc else ""
    _html(f"""
    <div class="sil-sec">
      <div class="sil-sec__no" style="--bg:{bg}">{escape(marker)}</div>
      <div><div class="sil-sec__title">{escape(title)}</div>{desc_html}</div>
    </div>
    """)


def card_title(title: str, desc: str = "") -> None:
    desc_html = f'<p class="sil-card-desc">{escape(desc)}</p>' if desc else ""
    _html(f'<div class="sil-card-title">{escape(title)}</div>{desc_html}')


def kpi(label: str, value: str, sub: str = "", bg: str = WHITE, fg: str = INK, soft: bool = False) -> None:
    cls = "sil-kpi sil-kpi--soft" if soft else "sil-kpi"
    sub_html = f'<div class="sil-kpi__sub">{escape(sub)}</div>' if sub else ""
    _html(f"""
    <div class="{cls}" style="--bg:{bg};--fg:{fg}">
      <div class="sil-kpi__label">{escape(label)}</div>
      <div class="sil-kpi__value">{escape(value)}</div>
      {sub_html}
    </div>
    """)


def insight(tag: str, big: str, text_html: str, bg: str = YELLOW, sticker: str = "✦") -> None:
    """text_html은 호출하는 쪽에서 escape한 문자열이어야 한다."""
    big_html = f'<div class="sil-insight__big">{escape(big)}</div>' if big else ""
    _html(f"""
    <div class="sil-insight" style="--bg:{bg}">
      <div class="sil-insight__sticker">{sticker}</div>
      <div class="sil-insight__tag">{escape(tag)}</div>
      {big_html}
      <p class="sil-insight__text">{text_html}</p>
    </div>
    """)


def info_card(name: str, ko: str, text: str, color: str = VIOLET) -> None:
    _html(f"""
    <div class="sil-info">
      <span class="sil-info__tag" style="--bg:{color}"></span><span class="sil-info__name">{escape(name)}</span>
      <div class="sil-info__ko">{escape(ko)}</div>
      <p class="sil-info__text">{text}</p>
    </div>
    """)


def empty_state(icon: str, title: str, text: str) -> None:
    _html(f"""
    <div class="sil-empty">
      <div class="sil-empty__icon">{icon}</div>
      <div class="sil-empty__title">{escape(title)}</div>
      <p class="sil-empty__text">{escape(text)}</p>
    </div>
    """)


def note(text: str) -> None:
    _html(f'<p class="sil-note">{escape(text)}</p>')


def chips_row(items: list[str], prefix: str = "") -> None:
    head = f'<span class="sil-note" style="margin-right:6px">{escape(prefix)}</span>' if prefix else ""
    _html("<div>" + head + "".join(chip(i) for i in items) + "</div>")
