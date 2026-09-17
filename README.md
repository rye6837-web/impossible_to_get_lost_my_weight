# 🥗 AI Diet Coach (절대 살 안 빠질 수 없는 다이어트 코치)

> **식약처 7.3만 건 공인 DB와 미국스포츠의학회(ACSM) 가이드라인 기반의 지능형 영양 & 운동 관리 AI 에이전트**  
> 복합 대화 분석(ReAct), 하이브리드 RAG, 초고속 SQLite FTS5 검색(1.24ms), 3단계 품질 게이트(Self-RAG)를 탑재한 종합 웰니스 웹 서비스입니다.

---

## 📌 1. 프로젝트 핵심 하이라이트

1. **⚡ SQLite FTS5 1.24ms 초고속 전문 검색 (RAM 0MB)**
   * 식품의약품안전처 2024 통합식품영양성분 73,199건 데이터를 SQLite FTS5 가상 테이블로 색인.
   * 무거운 판다스(Pandas) 메모리 상주 없이 0MB 램 점유율과 1.24ms의 극한 검색 속도 달성.

2. **🍱 ReAct 복합 질문 처리 & 듀얼 스마트 카드 (Human-in-the-Loop)**
   * *"점심에 삼겹살 먹고 40분 러닝했어"*와 같은 복합 질의에서 식단과 운동을 동시 감지.
   * 전문 도구 병렬 호출 후 식단/운동 **2단 동시 저장 카드**를 노출하여 원클릭 일괄 DB 저장 지원.

3. **🛡️ Self-RAG 3단계 품질 게이트 (Zero-Hallucination)**
   * **Gate 1 (관련성)**: DB 조회 정상 여부 판정 및 불일치 시 스마트 폴백(Smart Fallback) 우회.
   * **Gate 2 (사실 근거성)**: AI 답변 속 수치와 DB 실측치 교차 대조를 통한 환각 원천 차단.
   * **Gate 3 (임상 안전)**: 100kcal 미만 극단적 절식 등 위험 요소 감지 시 의학적 경고 라벨 자동 결합.

4. **🔄 4단계 캐스케이딩 모델 폴백 & 8턴 슬라이딩 윈도우**
   * 평상시 초고속/경량의 `gemini-3.5-flash-lite` 1순위 활용으로 응답 시간(1.5초)과 토큰 비용 절감.
   * 구글 API 503(과부하) 또는 429(속도제한) 발생 시 대화 맥락을 유지한 채 `3.6-flash` ➔ `3.7-flash`로 무중단 자동 전환.
   * 최근 8턴(총 16개 메시지) 슬라이딩 윈도우 버퍼를 통해 장기 세션 토큰 폭증 40% 이상 영구 절감.

5. **📚 신뢰도 높은 공인 출처(Citations) 100% 명시**
   * 영양 수치: **식품의약품안전처 2024 통합식품영양성분DB**
   * 운동 소비 칼로리: **미국스포츠의학회(ACSM) 및 Ainsworth Compendium 공인 METs**
   * 영양 상식/원리: **보건복지부 한국인 영양소 섭취기준(KDRIs)**

---

## 🏗️ 2. 시스템 아키텍처

```mermaid
flowchart TD
    User([사용자 복합 입력]) --> Agent[DietAgent (Gemini 3.5 Flash-Lite)]
    
    subgraph ToolEngine [전문 분석 도구 엔진]
        Agent -->|식단 분석| FoodDB[(SQLite FTS5 73,199건<br>식약처 DB 1.24ms)]
        Agent -->|운동 계산| ACSM[ACSM METs<br>칼로리 계산기]
        Agent -->|영양 상식| HybridRAG[14대 토픽 하이브리드 RAG<br>BM25 + Semantic Cosine]
    end
    
    subgraph QualityGate [🛡️ Self-RAG 3단계 품질 게이트]
        FoodDB & ACSM & HybridRAG --> Gate1{Gate 1: 관련성 검증}
        Gate1 -->|Yes| Gate2{Gate 2: 수치 일치 검증}
        Gate2 -->|True| Gate3{Gate 3: 임상 안전 가드레일}
    end
    
    Gate3 -->|ALL PASS| UI[Streamlit 웹 대시보드]
    UI --> Cards[식단/운동 2단 동시 저장 카드]
    Cards --> LocalDB[(SQLite 사용자 다이어트 장부)]
```

---

## 📂 3. 디렉토리 구조

```text
impossible_to_get_lost_my_weight/
├── app.py                     # Streamlit 메인 웹 애플리케이션 (대시보드 & 채팅 UI)
├── requirements.txt           # 필수 파이썬 라이브러리 목록
├── README.md                  # 프로젝트 안내서
│
├── ai_agent/                  # AI 에이전트 코어
│   └── diet_agent.py          # 4단 폴백, 8턴 윈도우, ReAct 프롬프트, 태그 파서
│
├── app_tools/                 # 전문 분석 도구 모음
│   ├── food_db.py             # SQLite FTS5 초고속 영양 검색 & 10대 카테고리 폴백
│   ├── exercise_tool.py       # ACSM METs 공식 기반 운동 소모 칼로리 계산기
│   └── nutrition_rag.py       # BM25 + 시맨틱 코사인 유사도 하이브리드 RAG (14개 토픽)
│
├── data/                      # 데이터셋 및 스크립트
│   ├── raw/                   # 식약처 원본 CSV 데이터
│   ├── processed/             # SQLite FTS5 데이터베이스 (food_nutrition.db)
│   └── scripts/               # FTS5 빌드 및 검증 스크립트 (build_fts_db.py 등)
│
├── docs/                      # 프로젝트 문서 및 연구 자료
│   ├── AI_DIET_COACH_IMPROVEMENT_ROADMAP.md  # 5대 요구사항 피드백 타당성 검증서
│   ├── FINAL_PRESENTATION_MASTER_GUIDE.md    # 최종 발표 대본 및 Q&A 방어 가이드
│   └── PRESENTATION_STUDY_GUIDE.md           # 실측 검증 기술 스터디 노트
│
├── notebooks/                 # 주피터 노트북 실측 검증
│   ├── Diet_Agent_Pipeline_Verification.ipynb # 10개 셀 LangGraph & RAG 실측 노트북
│   └── create_notebook.py                    # 노트북 생성 및 자동화 스크립트
│
└── presentation/              # 발표 자료 및 시각화 자산
    ├── AI_Diet_Coach_Presentation_수정2.pptx  # 최종 17개 슬라이드 공식 발표 PPT
    └── improved_langgraph_slide.png          # 고화질 아키텍처 다이어그램
```

---

## 🚀 4. 빠른 실행 방법 (Getting Started)

### 1) 저장소 복제 및 이동
```bash
git clone https://github.com/rye6837-web/impossible_to_get_lost_my_weight.git
cd impossible_to_get_lost_my_weight
```

### 2) 가상환경 구성 및 패키지 설치
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3) API 키 설정
프로젝트 루트 경로에 `.streamlit/secrets.toml` 파일을 생성하고 Google Gemini API 키를 입력합니다:
```toml
GEMINI_API_KEY = "AIzaSy..."
```
*(또는 웹 화면 사이드바의 입력창에 직접 API 키를 입력하여 실행할 수도 있습니다)*

### 4) Streamlit 웹 서버 실행
```bash
streamlit run app.py
```
브라우저에서 `http://localhost:8501`로 접속하여 이용하실 수 있습니다.

---

## 🛠️ 5. 기술 스택 (Tech Stack)

* **언어 및 런타임**: Python 3.11+
* **웹 인터페이스**: Streamlit, Plotly, HTML/CSS
* **인공지능 & LLM**: Google Gemini (`gemini-3.5-flash-lite`, `3.6-flash`, `3.7-flash`)
* **데이터베이스 & 검색**: SQLite3 (FTS5 Unicode61 전문 검색), In-Memory Hybrid RAG (BM25 + Dense Cosine + RRF)
* **프레젠테이션 엔진**: python-pptx (16:9 와이드스크린 자동 생성)
