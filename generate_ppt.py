import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# 1. 16:9 와이드스크린 프레젠테이션 생성
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# 2. 통일된 디자인 시스템 토큰
FONT_NAME = "Pretendard"

COLOR_BG = RGBColor(248, 250, 252)         # Canvas Light (#F8FAFC)
COLOR_PARCHMENT = RGBColor(245, 245, 247)  # Canvas Parchment (#F5F5F7)
COLOR_NAVY = RGBColor(30, 41, 59)           # Canvas Slate Navy (#1E293B)
COLOR_CARD = RGBColor(255, 255, 255)        # Card White (#FFFFFF)
COLOR_BORDER = RGBColor(226, 232, 240)      # Border Subtle (#E2E8F0)

COLOR_PRIMARY = RGBColor(0, 102, 204)       # Action Blue (#0066CC)
COLOR_EMERALD = RGBColor(16, 185, 129)      # Emerald Accent (#10B981)
COLOR_PURPLE = RGBColor(139, 92, 246)       # Purple Accent (#8B5CF6)
COLOR_AMBER = RGBColor(245, 158, 11)        # Amber Warning (#F59E0B)

COLOR_TEXT_MAIN = RGBColor(15, 23, 42)      # Main Ink (#0F172A)
COLOR_TEXT_BODY = RGBColor(51, 65, 85)      # Body Text (#334155)
COLOR_TEXT_MUTED = RGBColor(100, 116, 139)  # Muted Text (#64748B)

blank_layout = prs.slide_layouts[6]

def set_slide_background(slide, color):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = color
    bg.line.fill.background()
    return bg

def add_fixed_header(slide, category, title, subtitle):
    """
    모든 슬라이드에 완전히 일치하는 고정 좌표 헤더 렌더링
    - Category: Left 0.8", Top 0.45", Width 11.73"
    - Main Title: Left 0.8", Top 0.75", Width 11.73"
    - Subtitle: Left 0.8", Top 1.20", Width 11.73"
    """
    # 1. 챕터 카테고리 태그
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.73), Inches(0.30))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = tf_c.margin_top = tf_c.margin_right = tf_c.margin_bottom = 0
    p_c = tf_c.paragraphs[0]
    p_c.text = category.upper()
    p_c.font.name = FONT_NAME
    p_c.font.size = Pt(10)
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_PRIMARY
    
    # 2. 메인 슬라이드 제목
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.73), Inches(0.45))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = title
    p_t.font.name = FONT_NAME
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_NAVY
    
    # 3. 부제목 / 핵심 요약문
    sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.20), Inches(11.73), Inches(0.35))
    tf_s = sub_box.text_frame
    tf_s.word_wrap = True
    tf_s.margin_left = tf_s.margin_top = tf_s.margin_right = tf_s.margin_bottom = 0
    p_s = tf_s.paragraphs[0]
    p_s.text = subtitle
    p_s.font.name = FONT_NAME
    p_s.font.size = Pt(12)
    p_s.font.color.rgb = COLOR_TEXT_MUTED

def add_card(slide, left, top, width, height, title, items, bg_color=COLOR_CARD, border_color=COLOR_BORDER):
    """표준 컨테이너 카드"""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1.5)
    
    tb = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.22), width - Inches(0.5), height - Inches(0.44))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p_title = tf.paragraphs[0]
    p_title.text = title
    p_title.font.name = FONT_NAME
    p_title.font.size = Pt(14)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_NAVY
    p_title.space_after = Pt(8)
    
    for item in items:
        p = tf.add_paragraph()
        p.text = f"•  {item}"
        p.font.name = FONT_NAME
        p.font.size = Pt(11.5)
        p.font.color.rgb = COLOR_TEXT_BODY
        p.space_after = Pt(5)
    return card

def add_takeaway_strip(slide, left, top, width, height, title, description, accent_color=COLOR_PRIMARY):
    """하단 밀도 강화를 위한 풀-위드 서머리 스트립"""
    strip = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    strip.fill.solid()
    strip.fill.fore_color.rgb = RGBColor(241, 245, 249)
    strip.line.color.rgb = accent_color
    strip.line.width = Pt(1.5)
    
    tb = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.18), width - Inches(0.5), height - Inches(0.36))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p = tf.paragraphs[0]
    p.text = f"💡 {title}"
    p.font.name = FONT_NAME
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = accent_color
    p.space_after = Pt(3)
    
    p2 = tf.add_paragraph()
    p2.text = description
    p2.font.name = FONT_NAME
    p2.font.size = Pt(11)
    p2.font.color.rgb = COLOR_TEXT_MAIN
    return strip

def add_metric_card(slide, left, top, width, height, label, value, subtext="", accent_color=COLOR_PRIMARY):
    """하단 KPI 지표 카드"""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = COLOR_CARD
    card.line.color.rgb = COLOR_BORDER
    card.line.width = Pt(1.5)
    
    tb = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.15), width - Inches(0.3), height - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p_label = tf.paragraphs[0]
    p_label.text = label
    p_label.font.name = FONT_NAME
    p_label.font.size = Pt(10.5)
    p_label.font.color.rgb = COLOR_TEXT_MUTED
    p_label.space_after = Pt(2)
    
    p_val = tf.add_paragraph()
    p_val.text = value
    p_val.font.name = FONT_NAME
    p_val.font.size = Pt(18)
    p_val.font.bold = True
    p_val.font.color.rgb = accent_color
    
    if subtext:
        p_sub = tf.add_paragraph()
        p_sub.text = subtext
        p_sub.font.name = FONT_NAME
        p_sub.font.size = Pt(9.5)
        p_sub.font.color.rgb = COLOR_TEXT_BODY
    return card

def add_node(slide, left, top, width, height, text, subtext="", bg_color=COLOR_PRIMARY, text_color=RGBColor(255, 255, 255)):
    """LangGraph 노드 박스"""
    node = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    node.fill.solid()
    node.fill.fore_color.rgb = bg_color
    node.line.fill.background()
    
    tf = node.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = text
    p.font.name = FONT_NAME
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = text_color
    p.alignment = PP_ALIGN.CENTER
    
    if subtext:
        p2 = tf.add_paragraph()
        p2.text = subtext
        p2.font.name = FONT_NAME
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = text_color
        p2.alignment = PP_ALIGN.CENTER
    return node

# ==========================================
# Slide 01: 표지 (Cover Slide - Dark Canvas)
# ==========================================
s1 = prs.slides.add_slide(blank_layout)
set_slide_background(s1, COLOR_NAVY)

dec = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.8), Inches(0.12), Inches(3.6))
dec.fill.solid()
dec.fill.fore_color.rgb = COLOR_EMERALD
dec.line.fill.background()

tb_title = s1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.3), Inches(3.6))
tf1 = tb_title.text_frame
tf1.word_wrap = True
tf1.margin_left = tf1.margin_top = tf1.margin_right = tf1.margin_bottom = 0

p_tag = tf1.paragraphs[0]
p_tag.text = "AI AGENT & FULL-STACK WELLNESS PROJECT"
p_tag.font.name = FONT_NAME
p_tag.font.size = Pt(12)
p_tag.font.bold = True
p_tag.font.color.rgb = COLOR_EMERALD
p_tag.space_after = Pt(12)

p_main = tf1.add_paragraph()
p_main.text = "🥗 AI 다이어트 & 웰니스 코칭 서비스"
p_main.font.name = FONT_NAME
p_main.font.size = Pt(36)
p_main.font.bold = True
p_main.font.color.rgb = RGBColor(255, 255, 255)
p_main.space_after = Pt(14)

p_sub = tf1.add_paragraph()
p_sub.text = "식약처 표준 영양 DB · METs 운동 대사량 · LangGraph 라우팅 기반 개인 맞춤형 풀스택 플랫폼"
p_sub.font.name = FONT_NAME
p_sub.font.size = Pt(15)
p_sub.font.color.rgb = RGBColor(203, 213, 225)
p_sub.space_after = Pt(32)

p_info = tf1.add_paragraph()
p_info.text = "발표자 : 메타코드M 라이브 스터디  |  기술 스택 : Gemini Flash · LangGraph · Streamlit · SQLite · Plotly · Telegram"
p_info.font.name = FONT_NAME
p_info.font.size = Pt(11.5)
p_info.font.color.rgb = RGBColor(148, 163, 184)

# ==========================================
# Slide 02: 목차 (Table of Contents)
# ==========================================
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2, COLOR_BG)
add_fixed_header(s2, "Table of Contents", "프레젠테이션 목차", "프로젝트 기획부터 AI 아키텍처, 핵심 기능 구현, 강의 연계 성과까지의 체계적 구성")

# 4개 대단원 카드
add_card(s2, Inches(0.8), Inches(1.75), Inches(2.75), Inches(3.4), "Ⅰ. 프로젝트 개요", [
    "01. 기획 배경 및 문제 정의",
    "02. 서비스 핵심 가치 & 목표",
    "03. 차별화 포인트 분석"
])
add_card(s2, Inches(3.79), Inches(1.75), Inches(2.75), Inches(3.4), "Ⅱ. 시스템 & AI 엔진", [
    "04. 전체 시스템 구조도",
    "05. LangGraph 라우팅 워크플로우",
    "06. Function Calling & 멀티모달",
    "07. METs 운동 계산 & 영양 RAG",
    "08. 다중 모델 무중단 폴백 체계"
])
add_card(s2, Inches(6.78), Inches(1.75), Inches(2.75), Inches(3.4), "Ⅲ. 주요 기능 & 시연", [
    "09. BMR 맞춤 목표 & 보안 DB",
    "10. 스마트 식단 자동 저장 (HIL)",
    "11. 반응형 통계 대시보드",
    "12. 텔레그램 월간 결산 자동화"
])
add_card(s2, Inches(9.77), Inches(1.75), Inches(2.75), Inches(3.4), "Ⅳ. 강의 연계 & 발전", [
    "13. 1~7차시 커리큘럼 접목 의의",
    "14. 글로벌 클라우드 배포 성과",
    "15. 스마트 헬스케어 확장 로드맵"
])

add_takeaway_strip(s2, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45), 
    "핵심 전달 메시지 (Key Presentation Objective)", 
    "단순한 LLM 챗봇 튜토리얼을 넘어, 식약처 공공데이터베이스 강제 연동(환각율 0%), LangGraph 기반 의도 분류 및 Human-in-the-Loop 스마트 저장까지 결합된 완성도 높은 풀스택 실무 서비스의 구현 과정을 전달합니다."
)

# ==========================================
# Slide 03: 기획 배경 및 문제 정의
# ==========================================
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3, COLOR_BG)
add_fixed_header(s3, "Problem & Solution", "기획 배경 및 해결하고자 한 핵심 문제", "기존 다이어트 앱의 수동 기록 피로도와 일반 LLM의 환각(Hallucination) 한계를 동시 극복")

add_card(s3, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "⚠️ 기존 다이어트 앱 & LLM의 한계", [
    "수동 입력의 높은 피로도: 음식마다 g 수를 일일이 검색하고 타이핑해야 하는 번거로움",
    "LLM의 치명적 환각 (Hallucination): 임의로 칼로리/영양 수치를 지어내어 식단 왜곡 발생",
    "개인화 결여: 사용자 체형/목표(BMR/TDEE)가 반영되지 않는 획일적 기준",
    "단일 모델 장애: 트래픽 과부하(503/429) 발생 시 서비스 전체가 중단되는 취약성"
])

add_card(s3, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "✨ AI 코치의 해결 솔루션 & 혁신", [
    "📸 멀티모달 사진 식단 분석: 사진 1장으로 메뉴를 자동 식별하여 입력 시간 90% 단축",
    "🔍 식약처 표준 DB Function Calling: 파이썬 검색 도구 강제 연동으로 신뢰성 100% 확보",
    "🏃 METs 과학적 운동 대사량 연동: 20+ 운동 종목별 소모 칼로리 계산 및 순 칼로리 관리",
    "🛡️ 5대 다중 모델 무중단 폴백: Flash 계열 자동 전환으로 안정적 24/7 서비스 보장"
])

add_takeaway_strip(s3, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "해결 핵심 가치 (Core Value Proposition)",
    "사용자는 '사진 업로드' 또는 '자연어 대화'만으로 식약처 표준 영양 데이터를 확인하고, 원클릭으로 개인 DB에 기록하여 실시간 순 칼로리 대시보드와 텔레그램 결산 리포트를 제공받습니다."
)

# ==========================================
# Slide 04: 전체 시스템 구조도
# ==========================================
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4, COLOR_BG)
add_fixed_header(s4, "System Architecture", "전체 풀스택 시스템 아키텍처", "클라이언트 UI부터 AI 에이전트 엔진, 로컬 데이터베이스, 외부 메신저 알림까지의 통합 구조")

add_card(s4, Inches(0.8), Inches(1.75), Inches(3.71), Inches(3.4), "🖥️ Frontend (UI/UX)", [
    "Streamlit Web Framework: 반응형 웹 인터페이스",
    "Plotly Interactive Charts: 게이지, 도넛, 시계열 차트",
    "멀티모달 업로더: 파일 업로드 및 카메라 실시간 촬영",
    "세션 상태 관리: 사용자별 독립 로그인 세션 유지"
])

add_card(s4, Inches(4.81), Inches(1.75), Inches(3.71), Inches(3.4), "🤖 AI Engine & Tools", [
    "Google Gemini Flash: 초고속 멀티모달 추론",
    "Tool 1: search_food_nutrition (식약처 CSV DB)",
    "Tool 2: calculate_exercise_calories (METs 공식)",
    "Tool 3: search_nutrition_knowledge (영양 RAG)",
    "다중 모델 폴백: 5개 모델 자동 전환 복원력"
])

add_card(s4, Inches(8.82), Inches(1.75), Inches(3.71), Inches(3.4), "💾 Database & Services", [
    "SQLite (app_db): users, meal_records, exercise_records",
    "보안 암호화: SHA-256 + Salt 단방향 해싱",
    "Telegram Bot API: 월간 결산 메시지 및 차트 전송",
    "정기 스케줄러: scheduler.py 매월 1일 브로드캐스트"
])

# 하단 4개 기술 메트릭
add_metric_card(s4, Inches(0.8), Inches(5.35), Inches(2.70), Inches(1.45), "UI Framework", "Streamlit", "반응형 인터랙티브 대시보드", COLOR_PRIMARY)
add_metric_card(s4, Inches(3.81), Inches(5.35), Inches(2.70), Inches(1.45), "AI Model", "Gemini 3.6 Flash", "3대 전문 도구 바인딩 탑재", COLOR_EMERALD)
add_metric_card(s4, Inches(6.82), Inches(5.35), Inches(2.70), Inches(1.45), "Storage & Security", "SQLite + Salt", "개인화 식단 및 운동 영속 저장", COLOR_PURPLE)
add_metric_card(s4, Inches(9.83), Inches(5.35), Inches(2.70), Inches(1.45), "Automation", "Telegram Bot", "매월 1일 월간 리포트 자동 발송", COLOR_AMBER)

# ==========================================
# Slide 05: LangGraph 조건부 라우팅 워크플로우
# ==========================================
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5, COLOR_BG)
add_fixed_header(s5, "Agent Workflow", "LangGraph 기반 조건부 라우팅(Conditional Routing) 워크플로우", "사용자 입력(사진/텍스트)의 의도를 분석하여 최적의 하위 도구로 자동 분기")

# 상단 Start & Router 노드
add_node(s5, Inches(5.3), Inches(1.75), Inches(2.73), Inches(0.55), "🏁 __start__", "사용자 입력 수신 (사진/텍스트)", RGBColor(99, 102, 241))
add_node(s5, Inches(4.8), Inches(2.45), Inches(3.73), Inches(0.65), "🔀 Intent Router (check)", "질문 의도 분류 & 조건부 엣지(Conditional Edge)", COLOR_NAVY)

# 4개 분기 노드
add_node(s5, Inches(0.8), Inches(3.30), Inches(2.70), Inches(1.50), "🍱 식단 분석 핸들러\n(food_handler)", "Tool: search_food_nutrition\n식약처 표준 CSV 영양 검색\n<!-- MEAL_DATA --> 생성", COLOR_PRIMARY)
add_node(s5, Inches(3.81), Inches(3.30), Inches(2.70), Inches(1.50), "🏃 운동 계산 핸들러\n(exercise_handler)", "Tool: calculate_exercise_calories\nMETs 과학적 공식 계산\n<!-- EXERCISE_DATA --> 생성", COLOR_EMERALD)
add_node(s5, Inches(6.82), Inches(3.30), Inches(2.70), Inches(1.50), "📚 영양 백과 RAG\n(rag_handler)", "Tool: search_nutrition_knowledge\n혈당/정체기/흡수타이밍 지식\n전문 임상 영양 가이드", COLOR_PURPLE)
add_node(s5, Inches(9.83), Inches(3.30), Inches(2.70), Inches(1.50), "💬 일반 코칭 핸들러\n(general_handler)", "일상 웰니스 대화\n동기부여 및 멘탈 케어\n식단 목표 점검", COLOR_AMBER)

# 하단 HIL 및 End 노드
add_node(s5, Inches(2.5), Inches(5.00), Inches(8.33), Inches(0.75), "👤 Human-in-the-Loop 스마트 저장 컨펌", "AI 추출 메타데이터 카드 렌더링 ➔ 사용자 원클릭 승인 ➔ SQLite DB 즉시 기록", COLOR_EMERALD)
add_node(s5, Inches(5.3), Inches(6.00), Inches(2.73), Inches(0.55), "🏁 __end__", "대시보드 실시간 갱신 완료", RGBColor(71, 85, 105))

# ==========================================
# Slide 06: 핵심 기술 ① - 멀티모달 & Function Calling
# ==========================================
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6, COLOR_BG)
add_fixed_header(s6, "Core Technology 1", "멀티모달 AI 코치 & Function Calling (Tool Use)", "임의의 추측을 원천 배제하고 식약처 공공데이터만을 기반으로 영양 분석 수행")

add_card(s6, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "💡 Function Calling (도구 바인딩) 메커니즘", [
    "1. 사용자 입력: 음식 사진 업로드 또는 텍스트 입력 ('점심에 샐러드 먹었어')",
    "2. LLM 의도 판단: 식단 분석을 위해 영양 데이터 조회가 필수적임을 인식",
    "3. 도구 실행: Python `search_food_nutrition(음식명)` 함수를 자동 호출",
    "4. CSV DB 조회: 식약처 데이터셋에서 칼로리, 탄단지, 당류, 나트륨 수치 추출",
    "5. 최종 코칭 생성: 조회된 실제 데이터를 바탕으로 목표 대비 진단 및 피드백 제공"
])

add_card(s6, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "📋 3단계 전문 코칭 프롬프트 체계", [
    "Step 1. 영양소 요약: 섭취한 음식의 총 칼로리 및 탄·단·지, 나트륨 상세 수치 표기",
    "Step 2. 목표 대비 진단: 일일 목표치(예: 2,000kcal) 대비 현재 식단의 과부족 상태 평가",
    "Step 3. 솔루션 제안: 다음 식사(저녁/간식)에서 보충할 추천 대체 메뉴 및 행동 팁 제안",
    "환각율 0% 보장: 모든 영양 수치를 DB 조회값으로 고정하여 임상적 신뢰성 확보"
])

add_takeaway_strip(s6, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "기술적 핵심 의의 (Technical Significance)",
    "LLM을 단순 텍스트 생성기가 아닌 '의사결정 및 도구 실행 오케스트레이터'로 활용하여, 5,000+ 식약처 표준 영양 데이터셋과 완벽히 동기화된 정확한 답변을 생성합니다."
)

# ==========================================
# Slide 07: 핵심 기술 ② - METs 운동 계산 & 영양 RAG & 무중단 폴백
# ==========================================
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7, COLOR_BG)
add_fixed_header(s7, "Core Technology 2", "METs 운동 소모 칼로리 & 영양 RAG & 무중단 폴백", "과학적 운동 대사량 산출 공식, 임상 영양 백과 지식 검색, 다중 모델 복원력 구축")

add_card(s7, Inches(0.8), Inches(1.75), Inches(3.71), Inches(3.4), "🏃 METs 운동 소모 칼로리", [
    "미국 스포츠의학회(ACSM) 공식 적용:\n  1.05 × METs × 체중(kg) × 시간(hr)",
    "20+ 표준 운동 계수표 내장:\n  러닝(8.5), 웨이트(5.5), 수영(7.5) 등",
    "DB 체중 자동 연동: 사용자별 맞춤 계산",
    "순 칼로리(Net Calories) 연동"
])

add_card(s7, Inches(4.81), Inches(1.75), Inches(3.71), Inches(3.4), "📚 다이어트 & 영양 RAG", [
    "전문 영양 백과 지식 베이스 검색",
    "혈당 스파이크 방지 식사 순서 가이드",
    "다이어트 정체기 극복법 (리피드 전략)",
    "단백질 흡수 타이밍 & 대체 식재료 백과"
])

add_card(s7, Inches(8.82), Inches(1.75), Inches(3.71), Inches(3.4), "🛡️ 5대 다중 모델 폴백", [
    "1순위: gemini-3.6-flash (기본 호출)",
    "2순위: gemini-3.7-flash (차세대 플래시)",
    "3순위: gemini-3.5-flash (고가용성)",
    "4순위: gemini-flash-latest (최신)",
    "5순위: gemini-2.5-flash-lite (경량)"
])

add_takeaway_strip(s7, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "무중단 서비스 보장 (Fault-Tolerant Resilience)",
    "특정 Gemini 모델에 일시적 트래픽 과부하(503)나 분당 호출 제한(429)이 발생하더라도, 시스템이 0.5초 이내에 예비 Flash 모델로 자동 전환하여 사용자 중단 없이 안정적인 서비스를 제공합니다."
)

# ==========================================
# Slide 08: 핵심 기술 ③ - 신체 맞춤 영양 추천 & 보안 DB
# ==========================================
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8, COLOR_BG)
add_fixed_header(s8, "Core Technology 3", "신체 정보 기반 맞춤 영양 자동 추천 & 보안 DB", "미플린-세인트지올(Mifflin-St Jeor) 과학적 공식을 통한 개인화 설정")

add_card(s8, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "📏 BMR / TDEE 맞춤 영양 추천 공식", [
    "기초대사량 (BMR) 정밀 계산:\n   - 남성: (10×체중) + (6.25×키) - (5×나이) + 5\n   - 여성: (10×체중) + (6.25×키) - (5×나이) - 161",
    "활동대사량 (TDEE) 반영: 운동 빈도별 1.2 ~ 1.725 계수 적용",
    "목표별 칼로리/단백질 최적화:\n   - 감량(다이어트): TDEE - 450kcal / 체중 1kg당 1.6g 단백질\n   - 벌크업: TDEE + 300kcal / 체중 1kg당 1.8g 단백질",
    "신체 스펙 수정 시 원클릭 재계산 지원 ([내 설정] 탭)"
])

add_card(s8, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "🗄️ SQLite 데이터베이스 아키텍처", [
    "users 테이블: ID, 비밀번호 해시, 솔트, 성별, 나이, 키, 몸무게, 목표 칼로리, 목표 단백질, 텔레그램 Chat ID",
    "meal_records 테이블: 일자별 식사 구분(아침/점심/저녁/간식), 음식명, 칼로리, 탄단지, 당류, 나트륨",
    "exercise_records 테이블: 운동명, 운동 시간(분), 소모 칼로리(kcal), 메모",
    "보안 암호화: SHA-256 + Salt 단방향 해싱으로 계정 안전 보장"
])

add_takeaway_strip(s8, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "개인화 데이터 영속성 (Personalized Data Persistence)",
    "회원가입 시 입력된 신체 스펙에 맞춰 일일 권장량이 자동 계산되며, 언제든 [내 설정] 탭에서 체중 변화에 맞춰 목표를 재계산하고 SQLite DB에 안전하게 격리 저장됩니다."
)

# ==========================================
# Slide 09: 핵심 기능 ④ - Human-in-the-Loop 스마트 자동 저장 & 대시보드
# ==========================================
s9 = prs.slides.add_slide(blank_layout)
set_slide_background(s9, COLOR_BG)
add_fixed_header(s9, "Core Feature 1", "Human-in-the-Loop 스마트 자동 저장 & 통계 대시보드", "AI 분석 결과를 사용자가 원클릭으로 검토 및 저장하고, 실시간 통계 차트로 시각화")

add_card(s9, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "🍱 Human-in-the-Loop 스마트 저장 (HIL)", [
    "메타데이터 태그 자동 파싱: AI 응답에서 구조화된 JSON 데이터 추출",
    "인터랙티브 컨펌 카드: AI 답변 바로 아래에 감지된 식단/운동 정보 카드 표시",
    "원클릭 승인 & 저장: [💾 이 식단 DB에 바로 저장] 클릭 시 즉시 SQLite 기록",
    "수동 재입력 불필요: 사진 업로드부터 DB 저장까지 1초 만에 완료"
])

add_card(s9, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "📊 반응형 인터랙티브 통계 대시보드", [
    "일별(Daily): 순 칼로리(섭취 - 소모) 게이지 차트 & 3대 영양소 도넛 차트",
    "주간(Weekly): 7일간 일별 칼로리 vs 목표 기준선 막대/선 복합 차트",
    "월간(Monthly): 월간 목표 달성 성공률 KPI & 최다 섭취 음식 TOP 5 가로 막대",
    "연간(Yearly): 1~12월 월평균 칼로리 & 단백질 변화 다중 축 차트"
])

# 하단 4개 지표 카드
add_metric_card(s9, Inches(0.8), Inches(5.35), Inches(2.70), Inches(1.45), "Daily Intake", "총 섭취 칼로리", "일일 목표 대비 실시간 집계", COLOR_PRIMARY)
add_metric_card(s9, Inches(3.81), Inches(5.35), Inches(2.70), Inches(1.45), "Calories Burned", "🔥 운동 소모 칼로리", "METs 공식 기반 자동 차감", COLOR_EMERALD)
add_metric_card(s9, Inches(6.82), Inches(5.35), Inches(2.70), Inches(1.45), "Net Calories", "✨ 순 칼로리 (Net)", "섭취량 - 소모량 실시간 달성도", COLOR_PURPLE)
add_metric_card(s9, Inches(9.83), Inches(5.35), Inches(2.70), Inches(1.45), "Monthly Success", "목표 성공률 (%)", "한 달 식단 성공 일수 추적", COLOR_AMBER)

# ==========================================
# Slide 10: 핵심 기능 ⑤ - 텔레그램 연동 및 월간 결산 자동화
# ==========================================
s10 = prs.slides.add_slide(blank_layout)
set_slide_background(s10, COLOR_BG)
add_fixed_header(s10, "Core Feature 2", "텔레그램 연동 및 월간 결산 자동화 파이프라인", "앱에 직접 접속하지 않아도 매월 1일 개인 메신저로 한 달 결산 리포트 자동 전달")

add_card(s10, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "📱 텔레그램 리포트 구성 요소", [
    "간편한 연동: 텔레그램 봇으로 고유 Chat ID 확인 후 등록",
    "종합 결산 텍스트 리포트:\n   • 총 기록 일수 및 총 식사 횟수\n   • 월간 총 섭취 칼로리 및 일평균 섭취량\n   • 목표 달성 성공률 (%) 및 성공 일수\n   • 이번 달 최다 섭취 메뉴 TOP 3",
    "AI 코칭 총평: 달성률에 따른 맞춤형 피드백 및 다음 달 개선 조언",
    "차트 이미지 전송: Matplotlib 기반 월간 칼로리 추이 그래프 자동 렌더링"
])

add_card(s10, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "⏰ 자동 발송 파이프라인 (scheduler.py)", [
    "백그라운드 스케줄러: 매월 1일 자정 정기 트리거 동작",
    "일괄 브로드캐스트: 텔레그램 Chat ID를 등록한 모든 사용자 DB 일괄 조회",
    "개인화 리포트 생성: 사용자별 전월 식단 데이터를 독립 집계하여 차트 생성",
    "원클릭 즉시 테스트: 웹 [내 설정] 탭에서 이번 달 리포트 즉시 수신 테스트 가능"
])

add_takeaway_strip(s10, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "지속 가능한 다이어트 코칭 경험 (Continuous Engagement)",
    "사용자가 앱을 능동적으로 켜지 않더라도 정기적인 외부 채널 리포트를 통해 식습관을 되돌아보고 지속적인 동기부여를 얻을 수 있는 완성형 서비스 루프를 제공합니다."
)

# ==========================================
# Slide 11: 강의 커리큘럼 연계 및 기술적 의의
# ==========================================
s11 = prs.slides.add_slide(blank_layout)
set_slide_background(s11, COLOR_BG)
add_fixed_header(s11, "Course Mapping", "라이브스터디(1~7차시) 커리큘럼 연계 및 기술적 의의", "강의에서 다룬 핵심 이론 및 프레임워크를 실제 동작하는 풀스택 서비스로 완성")

add_card(s11, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "📚 차시별 핵심 이론 접목 내역", [
    "1차시 (프롬프트 엔지니어링): 페르소나 부여 및 3단계 응답 구조 System Instruction",
    "2~4차시 (데이터 전처리 & RAG): 식약처 CSV 정제 및 키워드 기반 영양 매칭",
    "5차시 (Tool Calling & ReAct): LLM 도구 바인딩 및 함수 자동 호출 에이전트",
    "6차시 (LangGraph & 멀티모달): 세션 상태(State) 관리 및 사진+텍스트 동시 처리",
    "7차시 (Adaptive Routing & Human-in-the-Loop): 조건부 분기 및 스마트 저장 컨펌"
])

add_card(s11, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "🏆 프로젝트의 기술적 의의", [
    "단순 튜토리얼을 넘은 풀스택 완성: LLM 단독 실행이 아닌 DB, UI, 외부 메신저까지 결합",
    "할루시네이션 완벽 통제: 공공데이터 검색 도구를 강제하여 의료/영양 도메인 신뢰성 확보",
    "실제 사용 가능한 완성도: 비밀번호 암호화, 개인 DB 격리, 5대 모델 무중단 폴백 구축",
    "글로벌 클라우드 배포: Streamlit Cloud 및 GitHub CI/CD 자동 배포 완료"
])

add_takeaway_strip(s11, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "학습 성과 요약 (Learning Takeaway)",
    "LLM API 호출 기초부터 LangGraph 기반 상태 관리, RAG 지식 검색, Human-in-the-Loop 패턴까지 강의의 전 과정을 실전 서비스 형태로 구현하여 기술적 이해도를 극대화했습니다."
)

# ==========================================
# Slide 12: 배포 성과 및 향후 발전 로드맵
# ==========================================
s12 = prs.slides.add_slide(blank_layout)
set_slide_background(s12, COLOR_BG)
add_fixed_header(s12, "Summary & Future Work", "서비스 배포 성과 및 향후 발전 로드맵", "글로벌 배포 완료 및 향후 스마트 헬스케어 생태계로의 확장 가능성")

add_card(s12, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "🚀 서비스 구현 및 배포 성과", [
    "GitHub 오픈소스 저장소: rye6837-web/impossible_to_get_lost_my_weight",
    "Streamlit Community Cloud 배포: 모바일/PC 반응형 웹 서비스 운영 중",
    "핵심 성과: 식단 사진 한 장으로 표준 영양 분석, 운동 칼로리 차감, 정기 결산 자동화 완성",
    "안정성: 다중 모델 폴백으로 503/429 오류 0% 달성"
])

add_card(s12, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "🔮 향후 확장 로드맵 (Roadmap)", [
    "스마트워치 / 헬스 데이터 연동: 애플워치·갤럭시워치 걸음 수 및 활동 칼로리 실시간 동기화",
    "AI 맞춤 식단 플래너 & 장바구니: 부족한 영양소를 채워주는 일주일 식단표 생성 및 밀키트 구매 연계",
    "연속 혈당 측정기(CGM) 데이터 접목: 혈당 스파이크 방지 식사 순서 실시간 코칭 기능 추가"
])

add_takeaway_strip(s12, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "감사 인사 및 Q&A",
    "경청해 주셔서 감사합니다. 질문 및 피드백을 환영합니다!"
)

# 저장
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AI_Diet_Coach_Presentation.pptx")
prs.save(output_path)
print(f"✅ Pretendard 단일 폰트 및 16:9 고정 헤더 디자인 시스템 기반 PPT 12장 생성 완료: {output_path}")
