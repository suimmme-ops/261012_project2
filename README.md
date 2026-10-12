# 🧪 STUDENT INSIGHT LAB

**EXPLORE DATA. DISCOVER INSIGHTS.**

학생 1,000명의 수학·읽기·쓰기 점수와 배경 변수(성별, 인종·민족 그룹, 부모 교육 수준, 점심 지원 유형, 시험 준비 과정)를 탐색하는 Streamlit 멀티 페이지 데이터 시각화 웹앱입니다. 변수를 직접 고르고 필터를 바꾸면서 학업 성취도의 패턴을 찾아볼 수 있습니다.

- 배포 URL: `https://<your-app-name>.streamlit.app` ← 배포 후 실제 주소로 바꾸세요

## 1. 주요 기능

| 페이지 | 내용 |
|---|---|
| **HOME** (`streamlit_app.py`) | 생성형 AI로 작성한 데이터셋 소개: 변수 설명, 분석 목적, 해석 시 주의사항 (차트·업로드 없음) |
| **01 데이터 업로드** | CSV 업로드(UTF-8/CP949 자동 인식), 샘플 데이터 사용, 행·열·결측·중복 KPI, 미리보기, 숫자형/범주형 자동 분류 |
| **02 성취도 분석** | KPI, 과목별 평균 막대, 히스토그램(평균·중앙값 표시), 박스플롯, 기술통계표, 범주형 빈도 분석 |
| **03 집단별 비교** | 집단별 평균 막대, 히트맵, 두 집단 비교(덤벨 차트·분포 비교), 최고/최저 집단 자동 요약 |
| **04 상관관계 탐색** | 피어슨 상관 행렬, 변수 선택 산점도(추세선 토글, 범주별 색상), 상관계수 해석 |
| **05 인사이트 탐구** | 탐구 질문 5개 → 그래프 → 기술통계 → 규칙 기반 자동 인사이트 문장 |

공통 기능

- **전역 필터**(사이드바): 성별·인종·부모 교육·점심·시험 준비 + 3과목 평균 범위 슬라이더. 필터끼리는 AND, 한 필터 안의 여러 값은 OR로 적용되며, 페이지를 이동해도 유지됩니다.
- **필터 초기화** 버튼, **필터링된 데이터 CSV** 다운로드, **집단별 요약 통계 / 기술통계 CSV** 다운로드
- 모든 차트는 Plotly로 그려서 Hover, Zoom, Pan, 범례 클릭, **PNG 저장**(차트 오른쪽 위 카메라 아이콘)을 지원합니다.
- 다른 구조의 CSV를 올리면 범용 분석 모드로 바뀝니다. 숫자형 변수 기술통계, 범주형 빈도, 분포, 상관관계 분석을 제공하고, 학생 데이터 전용 기능은 필요한 열이 모두 있을 때만 켜집니다.

## 2. 사용 기술

- Python 3.11, Streamlit (멀티 페이지, `st.session_state`)
- Pandas, NumPy: 데이터 처리와 통계 계산
- Plotly Express / Graph Objects: 인터랙티브 시각화
- Custom CSS + `.streamlit/config.toml` 테마: Neo-Brutalism × Bento Grid 디자인, Pretendard / Space Grotesk 폰트(로드에 실패하면 시스템 폰트 사용)

## 3. 프로젝트 구조

```text
├── streamlit_app.py          # 메인: 데이터셋 소개
├── pages/
│   ├── 1_데이터_업로드.py
│   ├── 2_성취도_분석.py
│   ├── 3_집단별_비교.py
│   ├── 4_상관관계_탐색.py
│   └── 5_인사이트_탐구.py
├── utils/
│   ├── data_loader.py        # CSV 로드·전처리, 세션 상태, 전역 필터
│   ├── statistics.py         # 기술통계·집단 비교·상관계수
│   ├── charts.py             # Plotly 차트 스타일과 차트 함수
│   └── styles.py             # 컬러 토큰, CSS, 공통 UI 컴포넌트
├── data/StudentsPerformance.csv   # 샘플 데이터
├── .streamlit/config.toml    # 테마 설정
└── requirements.txt
```

## 4. 로컬(Codespaces) 실행 방법

```bash
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

브라우저에서 `http://localhost:8501`이 열립니다. Codespaces에서는 **포트(PORTS)** 탭의 8501 포트를 열면 됩니다.

## 5. CSV 업로드 방법

1. 사이드바에서 **01 · 데이터 업로드**로 이동합니다.
2. 업로드 영역에 CSV 파일을 끌어다 놓거나, **샘플 데이터 사용** 버튼을 누릅니다.
3. 업로드에 성공하면 KPI 카드와 미리보기가 나타나고, 02~05 페이지에서 같은 데이터로 분석할 수 있습니다.
4. 새 파일을 올리면 이전 필터와 분석 설정이 초기화됩니다.

- 첫 줄은 열 이름(헤더)이어야 합니다.
- 학생 데이터 전용 기능을 쓰려면 다음 8개 열이 필요합니다: `gender`, `race/ethnicity`, `parental level of education`, `lunch`, `test preparation course`, `math score`, `reading score`, `writing score`

## 6. Streamlit Community Cloud 배포 방법

1. 이 프로젝트를 GitHub 저장소에 push합니다. 저장소에 `requirements.txt`, `.streamlit/config.toml`, `data/`, `pages/`, `utils/`가 모두 포함되어야 합니다.
2. <https://share.streamlit.io> 에 GitHub 계정으로 로그인합니다.
3. **Create app**에서 다음을 지정합니다.
   - Repository: 내 저장소, Branch: `main`
   - Main file path: **`streamlit_app.py`**
   - App URL: 원하는 이름 입력 (예: `student-insight-lab`)
4. **Deploy**를 누르고 설치 로그가 끝날 때까지 기다립니다. Advanced settings의 Python 버전은 3.11 이상을 권장합니다.
5. 공개 URL 확인 절차
   - 로그인하지 않은 브라우저(시크릿 창)에서 `https://<앱이름>.streamlit.app`에 접속해 보세요.
   - HOME 화면이 열리는지, 사이드바에서 6개 페이지로 이동할 수 있는지 확인하세요.
   - 01 페이지에서 **샘플 데이터 사용**을 누른 뒤 02~05 페이지의 그래프가 모두 표시되는지 확인하세요.
   - 앱의 **Share** 설정이 Public인지 확인하세요.

## 7. 데이터 해석 시 주의사항

- **상관관계·집단 차이 ≠ 인과관계**: 시험 준비 과정을 이수한 집단의 평균이 더 높더라도, 그 차이가 준비 과정 때문이라고 단정할 수 없습니다.
- **표본 수 확인**: 필터를 많이 걸면 집단의 표본 수(n)가 작아집니다. n이 작을수록 평균 차이를 더 신중하게 해석하세요.
- **일반화 주의**: 공개 교육용 예제 데이터라 수집 대상·시기·방법이 명시되어 있지 않습니다. 결과를 특정 학교나 국가 전체로 일반화하지 마세요.
- **민감 변수**: 인종·민족, 성별 등은 집단의 경향을 살펴보는 데만 사용하고, 개인을 판단하는 근거로 쓰지 마세요.
- 통계값은 소수점 첫째 자리, 상관계수는 셋째 자리로 표시합니다. 결측값은 해당 변수 값이 없는 행만 제외하고 계산하며, 화면에 유효 표본 수를 함께 보여 줍니다.
