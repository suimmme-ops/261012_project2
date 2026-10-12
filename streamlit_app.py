"""STUDENT INSIGHT LAB — 메인 페이지 (데이터셋 소개).

과제 조건에 따라 이 페이지에는 생성형 AI로 작성한 데이터셋 설명만 담는다.
(CSV 업로드 위젯, 통계 분석, Plotly 차트는 배치하지 않음)
"""

import streamlit as st

from utils import styles

styles.setup_page("데이터셋 소개", "🧪")

styles.hero(
    kicker="AI-WRITTEN DATASET GUIDE",
    title_html="STUDENT<br>INSIGHT LAB",
    subtitle="EXPLORE DATA. DISCOVER INSIGHTS.",
    body=(
        "Student Insight Lab은 학생들의 학업 성취도 데이터를 탐색하고 시각화하는 인터랙티브 분석 플랫폼입니다.<br><br>"
        "본 데이터에는 학생 1,000명의 수학·읽기·쓰기 점수와 성별, 부모 교육 수준, 점심 지원 유형, "
        "시험 준비 과정 이수 여부 등의 정보가 포함되어 있습니다.<br><br>"
        "다양한 변수를 비교하여 학업 성취도에서 나타나는 특징과 패턴을 탐색할 수 있습니다."
    ),
)

styles.note("※ 이 페이지의 데이터셋 설명은 생성형 AI를 활용해 작성했습니다.")

# ---------------------------------------------------------------------------
styles.section("01", "데이터셋 한눈에 보기", "StudentsPerformance.csv · 학생 1명 = 1행", bg=styles.LIME)

c1, c2, c3 = st.columns(3)
with c1:
    styles.kpi("Rows", "1,000", "학생 수 (관측치)", bg=styles.WHITE)
with c2:
    styles.kpi("Columns", "8", "범주형 5개 · 숫자형 3개", bg=styles.PINK)
with c3:
    styles.kpi("Score Range", "0–100", "과목별 시험 점수", bg=styles.VIOLET, fg=styles.WHITE)

# ---------------------------------------------------------------------------
styles.section("02", "주요 변수 설명", "배경 변수 5개와 성취도 변수 3개로 구성됩니다.", bg=styles.PINK)

VARIABLES = [
    ("gender", "성별", "학생의 성별입니다. <b>female</b>, <b>male</b> 두 값이 있습니다.", styles.INK),
    ("race/ethnicity", "인종·민족 그룹",
     "학생이 속한 인종·민족 그룹입니다. <b>AIAN</b>(아메리칸 인디언·알래스카 원주민), <b>Asian</b>, "
     "<b>Black</b>, <b>NHPI</b>(하와이 원주민·태평양 도서민), <b>White</b> 5개 범주입니다.", styles.YELLOW),
    ("parental level of education", "부모 교육 수준",
     "부모의 최종 학력입니다. some high school부터 master's degree까지 6단계 범주입니다.", styles.LIME),
    ("lunch", "점심 지원 유형",
     "<b>standard</b>(일반) 또는 <b>free/reduced</b>(무료·할인 급식)입니다. 가정의 경제적 배경을 "
     "간접적으로 보여주는 변수로 자주 쓰입니다.", styles.PINK),
    ("test preparation course", "시험 준비 과정",
     "시험 대비 과정을 <b>completed</b>(이수)했는지, <b>none</b>(미이수)인지 나타냅니다.", styles.VIOLET),
    ("math score", "수학 점수", "수학 시험 점수 (0~100점).", styles.COBALT),
    ("reading score", "읽기 점수", "읽기 시험 점수 (0~100점).", styles.PINK),
    ("writing score", "쓰기 점수", "쓰기 시험 점수 (0~100점).", styles.VIOLET),
]

# Bento: 배경 변수 3 + 2, 점수 변수 3
rows = [VARIABLES[:3], VARIABLES[3:5], VARIABLES[5:]]
for row in rows:
    cols = st.columns(len(row))
    for col, (name, ko, text, color) in zip(cols, row):
        with col:
            styles.info_card(name, ko, text, color)

styles.note("분석 페이지에서는 세 과목 점수로 3과목 평균(average score)과 총점(total score)을 계산해 함께 사용합니다.")

# ---------------------------------------------------------------------------
styles.section("03", "무엇을 탐색할 수 있나요?", bg=styles.COBALT)

left, right = st.columns([3, 2], gap="medium")
with left:
    with st.container(key="card-purpose"):
        styles.card_title("데이터 분석 목적")
        st.markdown(
            "- **성취도 분포** — 과목별 평균, 중앙값, 점수의 퍼짐 정도를 확인합니다.\n"
            "- **집단 간 비교** — 성별, 부모 교육 수준, 점심 지원 유형, 시험 준비 과정에 따라 평균 점수가 어떻게 다른지 비교합니다.\n"
            "- **과목 간 관계** — 수학·읽기·쓰기 점수가 함께 움직이는지 상관관계로 살펴봅니다.\n"
            "- **탐구 질문** — 질문을 고르고 필터를 조정하며 데이터 기반 인사이트를 직접 찾아봅니다."
        )
with right:
    with st.container(key="tint-start"):
        styles.card_title("HOW TO START", "분석은 다음 페이지에서 시작됩니다.")
        st.markdown(
            "1. **01 · 데이터 업로드**에서 CSV를 올리거나 샘플 데이터를 선택하세요.\n"
            "2. 사이드바의 **전역 필터**로 관심 집단을 고르세요.\n"
            "3. 02~05 페이지를 오가며 그래프를 직접 조작해 보세요."
        )
        st.page_link("pages/1_데이터_업로드.py", label="데이터 업로드로 이동 →", icon=":material/arrow_forward:")

# ---------------------------------------------------------------------------
styles.section("04", "데이터 활용·해석 시 주의사항", bg=styles.YELLOW)

w1, w2 = st.columns(2, gap="medium")
with w1:
    styles.insight(
        "CORRELATION ≠ CAUSATION",
        "",
        "집단 간 평균 차이나 높은 상관관계는 <b>함께 나타나는 경향</b>일 뿐, 한 변수가 다른 변수의 "
        "<b>원인</b>이라는 뜻이 아닙니다. 예를 들어 시험 준비 과정 이수 집단의 점수가 더 높더라도, "
        "그 차이가 준비 과정 때문이라고 단정할 수는 없습니다.",
        bg=styles.YELLOW, sticker="⚠",
    )
with w2:
    styles.insight(
        "KNOW YOUR DATA",
        "",
        "이 데이터는 공개 교육용 예제 데이터로, 수집 대상·시기·방법이 명시되어 있지 않습니다. "
        "결과를 특정 학교나 국가 전체로 <b>일반화하지 말고</b>, 집단별 표본 수(n)가 작을 때는 "
        "평균 차이를 더 신중하게 해석하세요. 인종·민족, 성별 등 민감한 변수는 개인에 대한 판단 근거로 사용하지 않아야 합니다.",
        bg=styles.LIME, sticker="i",
    )
