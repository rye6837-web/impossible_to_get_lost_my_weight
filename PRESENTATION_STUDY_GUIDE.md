# 🥗 AI 다이어트 코치 파이프라인 검증 — 종합 발표 대본 및 기술 가이드 (Master Study Guide)

본 문서는 **파이프라인 검증 노트북 ([Diet_Agent_Pipeline_Verification.ipynb](file:///Users/a0000/Dev/%EB%A9%94%ED%83%80%EC%BD%94%EB%93%9CM/%EB%9D%BC%EC%9D%B4%EB%B8%8C%20%EC%8A%A4%ED%84%B0%EB%94%94/Project/Diet_Agent_Pipeline_Verification.ipynb))** 및 **14장 발표용 PPT ([AI_Diet_Coach_Presentation.pptx](file:///Users/a0000/Dev/%EB%A9%94%ED%83%80%EC%BD%94%EB%93%9CM/%EB%9D%BC%EC%9D%B4%EB%B8%8C%20%EC%8A%A4%ED%84%B0%EB%94%94/Project/AI_Diet_Coach_Presentation.pptx))**를 바탕으로, 발표자가 슬라이드별 핵심 전달 메시지, 구어체 발표 대본, 심층 기술 원리, 예상 질문(Q&A) 방어 전략을 완벽히 숙지할 수 있도록 제작된 마스터 가이드입니다.

---

## 📌 목차 (Index)
- **1. 프로젝트 1분 엘리베이터 피치 (Core Value)**
- **2. 슬라이드별 완벽 발표 대본 & 핵심 전달 포인트 (Slide 01 ~ 14)**
- **3. 핵심 기술 심층 마스터 (Deep Tech Knowledge)**
- **4. 평가위원/청중 예상 Q&A 10선 및 모범 답변**

---

## 1. 프로젝트 1분 엘리베이터 피치 (Elevator Pitch)
"기존 다이어트 앱은 매 끼니마다 음식 그램 수를 검색하고 수동으로 타이핑해야 하는 극심한 번거로움이 있었고, 일반 생성형 AI는 칼로리와 영양 수치를 마음대로 지어내는 치명적인 **환각(Hallucination)** 문제가 있었습니다.

저희 **'AI 다이어트 코치'**는 7차시 프로젝트 패턴을 발전시켜, **식약처 표준 영양 DB 도구(Function Calling)**를 강제로 호출하여 100% 신뢰할 수 있는 수치를 기반으로 맞춤형 코칭을 제공합니다. 또한 **LangGraph 상태 그래프(`get_graph()`) 시각화 및 조건부 분기**, **503 과부하/429 속도제한을 0.5초 만에 복구하는 5대 Flash 모델 무중단 폴백**, **Self-RAG 3단계 품질 게이트(관련성 ➔ 환각 0% ➔ 임상 안전성)**, 그리고 **ACSM 표준 METs 운동 소모 칼로리와 SQLite 순 칼로리 집계**까지 결합한 **실제 동작하는 완성형 AI 엔지니어링 파이프라인**입니다."

---

## 2. 슬라이드별 완벽 발표 대본 & 핵심 전달 포인트

### Slide 01. 표지 (Cover)
- **핵심 키워드**: AI 에이전트 파이프라인, 식약처 표준 DB, LangGraph 시각화, Self-RAG
- **발표 대본**:
  "안녕하십니까. 메타코드M 라이브스터디 1~7차시의 핵심 AI 이론을 주피터 노트북 파이프라인으로 체계적으로 실증하고 완성한 **'AI 다이어트 코치 에이전트 파이프라인 검증'** 발표를 맡은 [발표자 이름]입니다. 저희 발표는 실제 주피터 노트북에서 실행된 3대 전문 도구와 LangGraph 상태 그래프, 5대 모델 폴백, 그리고 Self-RAG 품질 게이트의 실측 로그를 중심으로 진행하겠습니다."

---

### Slide 02. 목차 (Table of Contents)
- **핵심 키워드**: 4대 대단원, MVP 요약 ➔ 핵심 도구 검증 ➔ 복원력 & Self-RAG ➔ 커리큘럼 연계
- **발표 대본**:
  "오늘 발표는 4개의 파트로 진행됩니다. 첫째, 기획 배경과 서비스 MVP 구동 요약. 둘째, LangGraph 상태 그래프 시각화 및 3대 전문 도구 실측 검증. 셋째, 5대 모델 폴백 복원력과 Self-RAG 3단계 품질 게이트 검증. 마지막으로 1~7차시 강의 커리큘럼과의 연계 의의 순으로 말씀드리겠습니다."

---

### Slide 03. 기획 배경 및 문제 정의 (Problem & Solution)
- **핵심 키워드**: 수동 기록 피로도, LLM 환각(Hallucination), 멀티모달 인식, 공공데이터 강제 바인딩
- **발표 대본**:
  "기존 다이어트 앱은 매 끼니마다 무게를 재고 검색해 타이핑해야 하는 극심한 번거로움이 있었습니다. 반면 일반 LLM은 칼로리와 영양 성분을 마음대로 지어내는 치명적인 **환각(Hallucination)**이 발생합니다.
  저희는 이 문제를 사진으로 메뉴를 자동 인식하는 **멀티모달 비전 AI**와, 파이썬 도구를 통해 식약처 CSV DB 실측치만을 가져오도록 강제하는 **Function Calling 도구 바인딩**으로 해결했습니다."

---

### Slide 04. 서비스 MVP 구동 요약 (MVP Demonstration)
- **핵심 키워드**: Streamlit 반응형 웹, 4대 대시보드, HIL 스마트 카드, 텔레그램 연동
- **발표 대본**:
  "보시는 화면은 실제 동작하는 Streamlit 웹 애플리케이션의 MVP 구동 모습입니다. 사용자가 사진을 올리거나 대화하면 AI가 분석하고, 하단의 Human-in-the-Loop 카드를 통해 원클릭으로 DB에 저장됩니다. 일별 순 칼로리 게이지와 주간/월간 추이 차트가 실시간 연동되며, 매월 1일 텔레그램으로 월간 결산 리포트가 자동 발송됩니다."

---

### Slide 05. LangGraph 상태 그래프 시각화 (LangGraph Workflow)
- **핵심 키워드**: StateGraph, get_graph().draw_mermaid(), 4대 핸들러, Self-RAG 평가
- **발표 대본**:
  "주피터 노트북 Cell 2에서 실행한 **LangGraph 상태 그래프(StateGraph) 시각화 결과**입니다.
  `get_graph().draw_mermaid()`를 통해 생성된 그래프를 보시면, 사용자 입력이 들어왔을 때 `intent_router`가 의도를 분류하여 `food`, `exercise`, `rag`, `general`의 4대 핸들러로 조건부 분기합니다. 이후 모든 핸들러는 `self_rag_evaluator` 품질 검증을 거쳐 `human_in_the_loop` 스마트 저장 노드로 안전하게 이어집니다."

---

### Slide 06. [Tool 1 검증] 식약처 영양 DB 검색 (Tool 1 Verification)
- **핵심 키워드**: search_food_nutrition, 5,000+ CSV 실측치, 환각 0%
- **발표 대본**:
  "주피터 노트북 Cell 3의 **Tool 1 식약처 표준 영양 DB 검색 실측 결과**입니다.
  '닭가슴살'을 입력했을 때, LLM이 임의로 추측하지 않고 식약처 CSV DB에서 '콜라겐 훈제 닭가슴살 100g당 135kcal, 단백질 26g, 나트륨 58mg'이라는 공인 실측 JSON 데이터를 정확하게 반환하는 것을 확인했습니다."

---

### Slide 07. [Tool 2 검증] ACSM METs 운동 소모 계산기 (Tool 2 Verification)
- **핵심 키워드**: calculate_exercise_calories, ACSM 공식, 1.05 × METs × 체중 × 시간
- **발표 대본**:
  "노트북 Cell 4의 **Tool 2 운동 대사량 소모 칼로리 계산 실측 결과**입니다.
  미국 스포츠의학회(ACSM) 공식인 `1.05 × METs × 체중(kg) × 시간(hr)`을 적용하여, 70kg 사용자가 러닝(METs 8.5) 30분을 수행했을 때 정확히 312.4 kcal 소모를 산출해 냅니다."

---

### Slide 08. [Tool 3 검증] 영양 백과 RAG 검색기 (Tool 3 Verification)
- **핵심 키워드**: search_nutrition_knowledge, 혈당 스파이크 방지, 정체기 리피드
- **발표 대본**:
  "노트북 Cell 5의 **Tool 3 영양 백과 RAG 지식 검색 실측 결과**입니다.
  단순 수치 계산을 넘어 '혈당 스파이크 방지' 질의에 대해 [식이섬유 ➔ 단백질 ➔ 탄수화물] 식사 순서 가이드와 식후 15분 산책 등 전문 임상 영양 지식을 정확히 탐색하여 반환합니다."

---

### Slide 09. 5대 Flash 모델 무중단 폴백 실증 (Fault Tolerance)
- **핵심 키워드**: 503 UNAVAILABLE, 429 속도제한, 5대 Flash 모델, 0.5초 무중단 복구
- **발표 대본**:
  "노트북 Cell 6에서 검증한 **5대 Flash 모델 무중단 자가 치유(Self-Healing) 폴백**입니다.
  음식 사진 분석 시 1순위 모델에서 구글 서버 트래픽 폭주로 인한 `503 UNAVAILABLE` 에러가 감지되는 즉시, 시스템이 0.5초 내에 2순위 `gemini-3.7-flash`로 자동 전환하여 100% 정상 응답을 복구해 낸 실측 로그입니다."

---

### Slide 10. 멀티모달 식단 분석 & 메타데이터 태깅 (Multimodal & HIL)
- **핵심 키워드**: parse_agent_metadata, <!-- MEAL_DATA -->, JSON 분리
- **발표 대본**:
  "노트북 Cell 7의 **멀티모달 식단 분석 및 정형 메타데이터 태깅 실측**입니다.
  AI 코치가 친절한 3단계 코칭 답변을 작성함과 동시에 응답 하단에 `<!-- MEAL_DATA -->` JSON 태그를 생성하고, 정규식 파서가 이를 완벽히 분리하여 사용자의 원클릭 저장을 준비합니다."

---

### Slide 11. Self-RAG 3단계 품질 게이트 실증 (Self-RAG Quality Gate)
- **핵심 키워드**: LLM-as-a-Judge, 관련성·환각·임상 가드레일 3중 검증
- **발표 대본**:
  "노트북 Cell 9의 **Self-RAG 3단계 품질 게이트 평가 실측**입니다.
  답변이 사용자에게 나가기 전 LLM-as-a-Judge가 1단계 관련성(Relevance), 2단계 환각 수치 검출(Grounding), 3단계 임상 안전성(Clinical Safety)을 이진 평가하여 `ALL_GATES_PASSED: True`를 판정했을 때만 최종 승인합니다."

---

### Slide 12. SQLite DB 연동 & 순 칼로리 집계 쿼리 실측 (Database & Net Calories)
- **핵심 키워드**: get_daily_summary, Net Calories(순 칼로리), 섭취량 - 소모량
- **발표 대본**:
  "노트북 Cell 10의 **SQLite 데이터베이스 실측 집계 쿼리 결과**입니다.
  당일 섭취한 520.0 kcal에서 운동 소모 312.4 kcal가 차감된 **순 칼로리(Net Calories) 207.6 kcal**가 정확하게 연산되어 대시보드 게이지에 실시간 반영되는 것을 검증했습니다."

---

### Slide 13. 강의 커리큘럼(1~7차시) 연계 및 기술적 의의 (Course Mapping)
- **핵심 키워드**: 1~7차시 집대성, 프롬프트-RAG-Tool-LangGraph-Self RAG 풀스택
- **발표 대본**:
  "본 프로젝트는 1차시 프롬프트부터 2~4차시 데이터 RAG, 5차시 Tool 바인딩, 6차시 멀티모달 메모리, 7차시 Self-RAG 품질 게이트 및 LangGraph 시각화까지 **전 차시의 핵심 이론을 주피터 노트북과 풀스택 웹으로 완벽히 실증**했다는 점에서 큰 기술적 의의를 갖습니다."

---

### Slide 14. 배포 성과 및 향후 발전 로드맵 (Summary & Future Work)
- **핵심 키워드**: GitHub 오픈소스, Streamlit Community Cloud 글로벌 배포, 애플워치/CGM 확장
- **발표 대본**:
  "현재 본 서비스는 GitHub 오픈소스와 Streamlit Cloud를 통해 글로벌 배포되어 운영 중입니다. 향후 스마트워치 활동 칼로리 실시간 동기화와 연속 혈당 측정기(CGM) 데이터를 결합하여 차세대 초개인화 헬스케어 플랫폼으로 발전해 나갈 것입니다. 경청해 주셔서 대단히 감사합니다."

---

## 3. 핵심 기술 심층 마스터 (Deep Tech Knowledge)

### ① LangGraph StateGraph 시각화 원리
- `compiled_agent.get_graph().draw_mermaid()`를 호출하면 LangGraph 노드와 조건부 엣지의 토폴로지가 Mermaid 텍스트로 추출되며, `mermaid.ink` API 또는 ASCII 렌더러를 통해 다이어그램 이미지를 즉시 생성할 수 있습니다.

### ② 5대 Flash 모델 캐스케이딩 폴백 메커니즘
- `gemini-3.6-flash` ➔ `3.7-flash` ➔ `3.5-flash` ➔ `flash-latest` ➔ `2.5-flash-lite` 순서로 등록하여, 503 과부하나 429 속도제한 발생 시 0.5초 이내에 다음 순위 모델 세션으로 자동 전환되어 100% 무중단 복구됩니다.

### ③ Self-RAG 3단계 품질 게이트 (LLM-as-a-Judge)
1. **Relevance Check**: 사용자 질의 ↔ DB 검색 데이터 간의 관련성을 Pydantic 이진 평가.
2. **Grounding Check**: 생성 답변 속 수치가 DB 실측치와 100% 일치하는지 환각 검출.
3. **Clinical Safety**: 극단적 초저열량 경고 및 의학적 면책 문구 포함 여부 검증.

---

## 4. 평가위원/청중 예상 Q&A 10선 및 모범 답변

#### Q1. 7차시 Project_Example.ipynb와 이번 Diet_Agent_Pipeline_Verification.ipynb의 차이점은 무엇인가요?
> **답변**: "7차시 예시가 법률 QA 도메인의 단일 노트북 프로토타입이었다면, 이번 `Diet_Agent_Pipeline_Verification.ipynb`는 식약처 5,000+ 공공데이터 영양 DB, METs 운동 계산기, 영양 RAG, 그리고 5대 모델 폴백까지 결합하여 실제 상용 풀스택 웹 서비스의 전체 AI 두뇌를 완벽히 검증하도록 고도화한 실증 노트북입니다."

#### Q2. 503 과부하 에러가 발생했을 때 어떻게 무중단 처리가 가능한가요?
> **답변**: "구글 서버의 일시적 트래픽 스파이크로 `503 UNAVAILABLE`이 반환되면, `DietAgent` 내부의 예외 처리기가 즉시 다음 순위의 Flash 모델(`gemini-3.7-flash` 등)로 세션을 0.5초 내에 재구성하여 재호출하므로 사용자는 서비스 중단 없이 정상적인 응답을 받게 됩니다."

#### Q3. LangGraph 시각화(`get_graph()`)를 도입한 이유는 무엇인가요?
> **답변**: "복잡한 에이전트의 조건부 분기(식단/운동/RAG/일반)와 Self-RAG 품질 검증 흐름을 Mermaid 다이어그램으로 가시화하여, 시스템의 구조적 제어 흐름과 안정성을 직관적으로 입증하기 위함입니다."

#### Q4. 식약처 DB 검색 시 환각이 0%인 이유는 무엇인가요?
> **답변**: "LLM에게 직접 칼로리를 생성하게 하지 않고, `search_food_nutrition` 파이썬 도구를 바인딩하여 식약처 CSV 파일에서 정확한 행을 탐색한 실측 JSON 데이터만 반환하도록 강제하기 때문입니다."

#### Q5. 순 칼로리(Net Calories) 지표의 임상적 의미는 무엇인가요?
> **답변**: "`순 칼로리 = 섭취량 - 운동 소모량`을 실시간 계산하여, 운동을 통해 획득한 칼로리 버퍼를 대시보드에 즉각 반영함으로써 지속 가능한 다이어트 동기부여를 제공합니다."
