import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# 1. 16:9 와이드스크린 프레젠테이션 생성 (13.333" x 7.5" / 1920x1080)
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# 2. Pretendard 단일 폰트 & 엄격한 디자인 시스템 색상 토큰
FONT_NAME = "Pretendard"

# Brand & Accent Colors
COLOR_PRIMARY = RGBColor(0, 102, 204)       # Primary Action Blue (#0066CC)
COLOR_FOCUS_BLUE = RGBColor(41, 151, 255)   # Electric Focus Blue (#2997FF)
COLOR_EMERALD = RGBColor(16, 185, 129)      # Emerald Accent (#10B981)
COLOR_AMBER = RGBColor(245, 158, 11)        # Amber Warning (#F59E0B)
COLOR_PURPLE = RGBColor(139, 92, 246)       # Purple Flow Node (#8B5CF6)
COLOR_ROSE = RGBColor(244, 63, 94)          # Rose Accent (#F43F5E)

# Surface Colors
COLOR_CANVAS_LIGHT = RGBColor(248, 250, 252)      # Canvas Light (#F8FAFC)
COLOR_CANVAS_PARCHMENT = RGBColor(245, 245, 247)  # Canvas Parchment (#F5F5F7)
COLOR_CANVAS_DARK = RGBColor(30, 41, 59)          # Canvas Slate Navy (#1E293B)
COLOR_CARD_WHITE = RGBColor(255, 255, 255)        # Surface Card White (#FFFFFF)
COLOR_CARD_DARK = RGBColor(24, 24, 27)            # Code Terminal Dark (#18181B)

# Text & Ink Colors
COLOR_INK_MAIN = RGBColor(15, 23, 42)       # Main Heading Ink (#0F172A)
COLOR_TEXT_BODY = RGBColor(51, 65, 85)      # Body Text (#334155)
COLOR_TEXT_MUTED = RGBColor(100, 116, 139)  # Muted Caption (#64748B)
COLOR_TEXT_ON_DARK = RGBColor(248, 250, 252) # Text on Dark (#F8FAFC)
COLOR_TEXT_ON_DARK_MUTED = RGBColor(148, 163, 184) # Muted on Dark (#94A3B8)
COLOR_CODE_GREEN = RGBColor(74, 222, 128)   # Terminal Code Green (#4ADE80)
COLOR_CODE_CYAN = RGBColor(56, 189, 248)    # Terminal Code Cyan (#38BDF8)
COLOR_CODE_YELLOW = RGBColor(253, 224, 71)  # Terminal Code Yellow (#FDE047)
COLOR_CODE_RED = RGBColor(248, 113, 113)    # Terminal Code Red (#F87171)

# Hairlines & Borders
COLOR_BORDER_SUBTLE = RGBColor(226, 232, 240) # Border Subtle (#E2E8F0)
COLOR_BORDER_DARK = RGBColor(63, 63, 70)      # Border Dark Subtle (#3F3F46)

blank_layout = prs.slide_layouts[6]

def set_slide_background(slide, color):
    """슬라이드 전체 배경색 설정"""
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = color
    bg.line.fill.background()
    return bg

def add_fixed_header(slide, category, title, subtitle):
    """
    디자인 가이드라인에 따른 엄격한 고정 좌표 헤더 렌더링
    - Chapter Tag: Left 0.8", Top 0.45", Width 11.73", Height 0.30"
    - Main Title: Left 0.8", Top 0.75", Width 11.73", Height 0.45"
    - Subtitle: Left 0.8", Top 1.20", Width 11.73", Height 0.35"
    """
    # 1. Chapter Category Tracker Tag
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.73), Inches(0.30))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = tf_c.margin_top = tf_c.margin_right = tf_c.margin_bottom = 0
    p_c = tf_c.paragraphs[0]
    p_c.text = category.upper()
    p_c.font.name = FONT_NAME
    p_c.font.size = Pt(10.5)
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_PRIMARY
    
    # 2. Main Slide Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.73), Inches(0.45))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = title
    p_t.font.name = FONT_NAME
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_INK_MAIN
    
    # 3. Subtitle / Context Line
    sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.20), Inches(11.73), Inches(0.35))
    tf_s = sub_box.text_frame
    tf_s.word_wrap = True
    tf_s.margin_left = tf_s.margin_top = tf_s.margin_right = tf_s.margin_bottom = 0
    p_s = tf_s.paragraphs[0]
    p_s.text = subtitle
    p_s.font.name = FONT_NAME
    p_s.font.size = Pt(12)
    p_s.font.color.rgb = COLOR_TEXT_MUTED

def add_card(slide, left, top, width, height, title, items, bg_color=COLOR_CARD_WHITE, border_color=COLOR_BORDER_SUBTLE):
    """상단 메인 콘텐츠 컨테이너 카드"""
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
    p_title.font.size = Pt(14.5)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_INK_MAIN
    p_title.space_after = Pt(8)
    
    for item in items:
        p = tf.add_paragraph()
        p.text = f"•  {item}"
        p.font.name = FONT_NAME
        p.font.size = Pt(11.5)
        p.font.color.rgb = COLOR_TEXT_BODY
        p.space_after = Pt(5)
    return card

def add_code_card(slide, left, top, width, height, title, code_snippets, header_color=COLOR_CODE_CYAN):
    """다크 터미널/코드 박스"""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = COLOR_CARD_DARK
    card.line.color.rgb = COLOR_BORDER_DARK
    card.line.width = Pt(1.5)
    
    tb = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.20), width - Inches(0.5), height - Inches(0.40))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p_title = tf.paragraphs[0]
    p_title.text = f"💻 {title}"
    p_title.font.name = FONT_NAME
    p_title.font.size = Pt(13)
    p_title.font.bold = True
    p_title.font.color.rgb = header_color
    p_title.space_after = Pt(6)
    
    for line in code_snippets:
        p = tf.add_paragraph()
        p.text = line
        p.font.name = FONT_NAME
        p.font.size = Pt(9.6)
        if line.startswith("#") or line.startswith("//"):
            p.font.color.rgb = COLOR_TEXT_ON_DARK_MUTED
        elif "503" in line or "429" in line or "오류" in line or "UNAVAILABLE" in line or "❌" in line or "⚠️" in line:
            p.font.color.rgb = COLOR_CODE_RED
        elif "True" in line or "200" in line or "성공" in line or "✅" in line or "정상" in line:
            p.font.color.rgb = COLOR_CODE_GREEN
        elif "Gate" in line or "Score" in line or "├──" in line or "└──" in line or "자동 전환" in line:
            p.font.color.rgb = COLOR_CODE_YELLOW
        elif "{" in line or "}" in line or ":" in line:
            p.font.color.rgb = RGBColor(228, 228, 231)
        else:
            p.font.color.rgb = COLOR_TEXT_ON_DARK
        p.space_after = Pt(2.2)
    return card

def add_takeaway_strip(slide, left, top, width, height, title, description, accent_color=COLOR_PRIMARY):
    """하단 레이아웃 밀도 충실화를 위한 풀-위드 테이크어웨이 스트립"""
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
    p2.font.color.rgb = COLOR_INK_MAIN
    return strip

def add_metric_card(slide, left, top, width, height, label, value, subtext="", accent_color=COLOR_PRIMARY):
    """하단 KPI 통계 지표 카드"""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = COLOR_CARD_WHITE
    card.line.color.rgb = COLOR_BORDER_SUBTLE
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
    """LangGraph 워크플로우 노드 박스"""
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
# Slide 01: 표지 (Cover - Canvas Dark #1E293B)
# ==========================================
s1 = prs.slides.add_slide(blank_layout)
set_slide_background(s1, COLOR_CANVAS_DARK)

dec = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.8), Inches(0.12), Inches(3.6))
dec.fill.solid()
dec.fill.fore_color.rgb = COLOR_EMERALD
dec.line.fill.background()

tb_title = s1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.3), Inches(3.6))
tf1 = tb_title.text_frame
tf1.word_wrap = True
tf1.margin_left = tf1.margin_top = tf1.margin_right = tf1.margin_bottom = 0

p_tag = tf1.paragraphs[0]
p_tag.text = "AI AGENT & FULL-STACK WELLNESS PLATFORM"
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
p_main.font.color.rgb = COLOR_TEXT_ON_DARK
p_main.space_after = Pt(14)

p_sub = tf1.add_paragraph()
p_sub.text = "식약처 표준 영양 DB · Self-RAG 3단계 품질 게이트 · LangGraph 라우팅 기반 개인 맞춤형 풀스택 플랫폼"
p_sub.font.name = FONT_NAME
p_sub.font.size = Pt(15)
p_sub.font.color.rgb = RGBColor(203, 213, 225)
p_sub.space_after = Pt(32)

p_info = tf1.add_paragraph()
p_info.text = "발표자 : 메타코드M 라이브 스터디  |  기술 스택 : Gemini Flash · LangGraph · Self-RAG · SQLite · Streamlit · Telegram"
p_info.font.name = FONT_NAME
p_info.font.size = Pt(11.5)
p_info.font.color.rgb = COLOR_TEXT_ON_DARK_MUTED

# ==========================================
# Slide 02: 목차 (Table of Contents)
# ==========================================
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2, COLOR_CANVAS_LIGHT)
add_fixed_header(s2, "Table of Contents", "프레젠테이션 목차", "프로젝트 기획부터 아키텍처, 트러블슈팅, Self-RAG 품질 검증, 핵심 기능 실측까지의 체계적 구성")

# 4개 대단원 카드
add_card(s2, Inches(0.8), Inches(1.75), Inches(2.75), Inches(3.4), "Ⅰ. 프로젝트 개요", [
    "01. 기획 배경 및 문제 정의",
    "02. 서비스 핵심 가치 & 목표",
    "03. 차별화 포인트 분석"
])
add_card(s2, Inches(3.79), Inches(1.75), Inches(2.75), Inches(3.4), "Ⅱ. 시스템 & 트러블슈팅", [
    "04. 전체 풀스택 시스템 구조도",
    "05. 프로젝트 디렉터리 아키텍처",
    "06. 503/429 & 네임스페이스 해결",
    "07. LangGraph 라우팅 워크플로우"
])
add_card(s2, Inches(6.78), Inches(1.75), Inches(2.75), Inches(3.4), "Ⅲ. 핵심 기술 & 시연", [
    "08. Self-RAG 3단계 품질 게이트",
    "09. Function Calling 영양 실측",
    "10. METs 운동 & RAG 실행 로그",
    "11. BMR 맞춤 목표 & 보안 DB",
    "12. 스마트 저장 & 텔레그램 결산"
])
add_card(s2, Inches(9.77), Inches(1.75), Inches(2.75), Inches(3.4), "Ⅳ. 강의 연계 & 발전", [
    "13. 1~7차시 커리큘럼 접목 의의",
    "14. 글로벌 클라우드 배포 성과",
    "15. 스마트 헬스케어 확장 로드맵"
])

add_takeaway_strip(s2, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45), 
    "핵심 전달 메시지 (Key Presentation Objective)", 
    "단순한 LLM 챗봇 튜토리얼을 넘어, 503 과부하 및 429 속도제한을 100% 방어한 다중 모델 폴백, Self-RAG 3단계 품질 게이트(환각율 0%), LangGraph 조건부 라우팅까지 결합된 프로덕션 실무 풀스택 구현 과정을 전달합니다."
)

# ==========================================
# Slide 03: 기획 배경 및 문제 정의
# ==========================================
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3, COLOR_CANVAS_LIGHT)
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
    "🛡️ Self-RAG 3단계 품질 검증: 관련성·환각·임상 안전 가드레일을 통한 철저한 오답 필터링",
    "🏃 METs 운동 대사량 & 순 칼로리 관리: 20+ 운동 종목별 소모 칼로리 산출 및 영양 균형"
])

add_takeaway_strip(s3, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "해결 핵심 가치 (Core Value Proposition)",
    "사용자는 '사진 업로드' 또는 '자연어 대화'만으로 식약처 표준 영양 데이터를 확인하고, 원클릭으로 개인 DB에 기록하여 실시간 순 칼로리 대시보드와 텔레그램 결산 리포트를 제공받습니다."
)

# ==========================================
# Slide 04: 전체 시스템 구조도
# ==========================================
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4, COLOR_CANVAS_LIGHT)
add_fixed_header(s4, "System Architecture", "전체 풀스택 시스템 아키텍처", "클라이언트 UI부터 AI 에이전트 엔진, 로컬 데이터베이스, 외부 메신저 알림까지의 통합 구조")

add_card(s4, Inches(0.8), Inches(1.75), Inches(3.71), Inches(3.4), "🖥️ Frontend (UI/UX)", [
    "Streamlit Web Framework: 반응형 웹 인터페이스",
    "Plotly Interactive Charts: 게이지, 도넛, 시계열 차트",
    "멀티모달 업로더: 파일 업로드 및 카메라 실시간 촬영",
    "세션 상태 관리: 사용자별 독립 로그인 세션 유지"
])

add_card(s4, Inches(4.81), Inches(1.75), Inches(3.71), Inches(3.4), "🤖 AI Engine & Self-RAG", [
    "Google Gemini Flash: 초고속 멀티모달 추론",
    "Self-RAG 3단계 품질 게이트 (LLM-as-a-Judge)",
    "Tool 1: search_food_nutrition (식약처 CSV DB)",
    "Tool 2: calculate_exercise_calories (METs 공식)",
    "Tool 3: search_nutrition_knowledge (영양 RAG)"
])

add_card(s4, Inches(8.82), Inches(1.75), Inches(3.71), Inches(3.4), "💾 Database & Services", [
    "SQLite (app_db): users, meal_records, exercise_records",
    "보안 암호화: SHA-256 + Salt 단방향 해싱",
    "Telegram Bot API: 월간 결산 메시지 및 차트 전송",
    "정기 스케줄러: scheduler.py 매월 1일 브로드캐스트"
])

# 하단 4개 기술 메트릭 리본
add_metric_card(s4, Inches(0.8), Inches(5.35), Inches(2.70), Inches(1.45), "UI Framework", "Streamlit", "반응형 인터랙티브 대시보드", COLOR_PRIMARY)
add_metric_card(s4, Inches(3.81), Inches(5.35), Inches(2.70), Inches(1.45), "AI Engine", "Gemini + Self-RAG", "3대 품질 게이트 & Tool 바인딩", COLOR_EMERALD)
add_metric_card(s4, Inches(6.82), Inches(5.35), Inches(2.70), Inches(1.45), "Storage & Security", "SQLite + Salt", "개인화 식단 및 운동 영속 저장", COLOR_PURPLE)
add_metric_card(s4, Inches(9.83), Inches(5.35), Inches(2.70), Inches(1.45), "Automation", "Telegram Bot", "매월 1일 월간 리포트 자동 발송", COLOR_AMBER)

# ==========================================
# Slide 05: 프로젝트 폴더 및 파일 아키텍처
# ==========================================
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5, COLOR_CANVAS_LIGHT)
add_fixed_header(s5, "Project Structure", "프로젝트 디렉터리 및 파일 아키텍처", "모듈화와 네임스페이스 격리 원칙(Clean Architecture)을 준수한 체계적인 프로젝트 구조")

add_card(s5, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "📁 핵심 모듈별 책임과 역할 (Responsibilities)", [
    "`app.py`: Streamlit 메인 엔트리포인트 (UI/UX, 4대 통계 탭, HIL 카드)",
    "`ai_agent/diet_agent.py`: 5대 Flash 모델 자동 폴백, 3대 Tool 바인딩, 메타데이터 파서",
    "`app_tools/`: 전문 기능 분리 (식약처 DB 검색, METs 운동 계산, 영양 RAG)",
    "`app_db/database.py`: SQLite 연결 풀, 계정 암호화(Salt), 식단/운동 CRUD & 통계 쿼리",
    "`app_services/telegram_service.py`: 텔레그램 리포트 생성 및 Matplotlib 차트 렌더링",
    "`scheduler.py`: APScheduler 백그라운드 데몬 (매월 1일 정기 발송)"
])

# 우측 터미널 스타일 프로젝트 트리 뷰
add_code_card(s5, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "Project Directory Tree Structure", [
    "Project/",
    "├── app.py                      # 메인 웹 대시보드 & UI",
    "├── ai_agent/                   # AI 에이전트 & 다중 모델 폴백",
    "│   └── diet_agent.py           # Gemini 3.6/3.7 Flash 에이전트",
    "├── app_tools/                  # 전문 도구 (Tool Use) 모듈",
    "│   ├── food_db.py              # 식약처 CSV 5,000+ 영양 검색",
    "│   ├── exercise_tool.py        # ACSM METs 운동 소모 계산기",
    "│   └── nutrition_rag.py        # 혈당/정체기 영양 RAG 검색",
    "├── app_db/                     # SQLite 데이터베이스 & 보안",
    "│   └── database.py             # users / meal / exercise CRUD",
    "├── app_services/               # 외부 알림 & 시각화 서비스",
    "│   └── telegram_service.py     # 텔레그램 봇 & Matplotlib 차트",
    "└── scheduler.py                # 매월 1일 정기 결산 스케줄러"
], header_color=COLOR_CODE_CYAN)

add_takeaway_strip(s5, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "네임스페이스 충돌 방지 & 유지보수성 (Clean Code Architecture)",
    "서버 전역 모듈과의 이름 충돌을 원천 차단하기 위해 고유 네임스페이스(`app_tools/`, `app_db/`, `app_services/`, `ai_agent/`)를 채택하여, 클라우드 환경에서도 100% 무결점 배포가 가능하도록 구조화했습니다."
)

# ==========================================
# Slide 06: [신규 트러블슈팅 슬라이드] 503/429 과부하 방어 및 네임스페이스 해결
# ==========================================
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6, COLOR_CANVAS_LIGHT)
add_fixed_header(s6, "Troubleshooting", "실무 트러블슈팅 및 복원력(Fault-Tolerance) 구축", "503 과부하 및 429 속도제한 에러 방어를 위한 5대 Flash 모델 다중 폴백 시스템 실증")

add_card(s6, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "🚨 직면했던 2대 핵심 이슈 & 해결책", [
    "Issue 1: 사진 분석 시 `503 UNAVAILABLE` (모델 일시 과부하)\n  • 원인: 특정 모델 서버에 트래픽 폭주 시 응답 불가\n  • 해결: 5대 Flash 모델 간 `0.5초 무중단 자동 폴백(Fallback)` 구축",
    "Issue 2: `429 RESOURCE_EXHAUSTED` (분당 속도 제한)\n  • 원인: Pro 모델 무료 한도(2 RPM)의 극심한 제약\n  • 해결: 1분당 15회 이상 넉넉한 Flash 계열로만 전면 최적화",
    "Issue 3: Streamlit Cloud `ModuleNotFoundError`\n  • 해결: `app_tools/`, `ai_agent/` 고유 네임스페이스 전면 리팩토링"
])

# 우측 실제 503 에러 발생 ➔ 2순위 모델 자동 복구 터미널 로그
add_code_card(s6, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "Live Fallback Execution Log (Self-Healing)", [
    "# [1. 음식 사진 식단 분석 요청 전송]",
    "Attempt 1: Call [gemini-3.6-flash] with food image...",
    "⚠️ [gemini-3.6-flash] 503 UNAVAILABLE (High Demand Spikes)",
    "",
    "# [2. 시스템 자동 감지 & 0.5s 이내 예비 모델 전환]",
    "🔄 Auto-Switching to 2nd candidate: [gemini-3.7-flash]",
    "Attempt 2: Call [gemini-3.7-flash] with tools & session...",
    "",
    "# [3. 무중단 응답 복구 완료]",
    "✅ [gemini-3.7-flash] 200 OK (분석 성공 및 영양 도출)",
    "Output: {'food_name': '고구마와 닭가슴살소시지', 'kcal': 380}"
], header_color=COLOR_ROSE)

add_takeaway_strip(s6, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "실무 엔지니어링 완성도 (Production-Grade Resilience)",
    "단일 모델 장애 시 서비스가 멈추는 취약점을 `[3.6-flash ➔ 3.7-flash ➔ 3.5-flash ➔ flash-latest ➔ 2.5-flash-lite]`의 다중 캐스케이딩 폴백 루프로 해결하여 100% 가용성을 달성했습니다."
)

# ==========================================
# Slide 07: LangGraph 조건부 라우팅 워크플로우
# ==========================================
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7, COLOR_CANVAS_LIGHT)
add_fixed_header(s7, "Agent Workflow", "LangGraph 기반 조건부 라우팅(Conditional Routing) 워크플로우", "사용자 입력(사진/텍스트)의 의도를 분석하여 최적의 하위 도구로 자동 분기")

# 상단 Start & Router 노드
add_node(s7, Inches(5.3), Inches(1.75), Inches(2.73), Inches(0.55), "🏁 __start__", "사용자 입력 수신 (사진/텍스트)", RGBColor(99, 102, 241))
add_node(s7, Inches(4.8), Inches(2.45), Inches(3.73), Inches(0.65), "🔀 Intent Router (check)", "질문 의도 분류 & 조건부 엣지(Conditional Edge)", COLOR_INK_MAIN)

# 4개 분기 노드
add_node(s7, Inches(0.8), Inches(3.30), Inches(2.70), Inches(1.50), "🍱 식단 분석 핸들러\n(food_handler)", "Tool: search_food_nutrition\n식약처 표준 CSV 영양 검색\n<!-- MEAL_DATA --> 생성", COLOR_PRIMARY)
add_node(s7, Inches(3.81), Inches(3.30), Inches(2.70), Inches(1.50), "🏃 운동 계산 핸들러\n(exercise_handler)", "Tool: calculate_exercise_calories\nMETs 과학적 공식 계산\n<!-- EXERCISE_DATA --> 생성", COLOR_EMERALD)
add_node(s7, Inches(6.82), Inches(3.30), Inches(2.70), Inches(1.50), "📚 영양 백과 RAG\n(rag_handler)", "Tool: search_nutrition_knowledge\n혈당/정체기/흡수타이밍 지식\n전문 임상 영양 가이드", COLOR_PURPLE)
add_node(s7, Inches(9.83), Inches(3.30), Inches(2.70), Inches(1.50), "💬 일반 코칭 핸들러\n(general_handler)", "일상 웰니스 대화\n동기부여 및 멘탈 케어\n식단 목표 점검", COLOR_AMBER)

# 하단 HIL 및 End 노드
add_node(s7, Inches(2.5), Inches(5.00), Inches(8.33), Inches(0.75), "👤 Human-in-the-Loop 스마트 저장 컨펌", "AI 추출 메타데이터 카드 렌더링 ➔ 사용자 원클릭 승인 ➔ SQLite DB 즉시 기록", COLOR_EMERALD)
add_node(s7, Inches(5.3), Inches(6.00), Inches(2.73), Inches(0.55), "🏁 __end__", "대시보드 실시간 갱신 완료", RGBColor(71, 85, 105))

# ==========================================
# Slide 08: Self-RAG 3단계 품질 게이트 & AI 가드레일
# ==========================================
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8, COLOR_CANVAS_LIGHT)
add_fixed_header(s8, "Self-RAG Quality Gate", "Self-RAG 3단계 품질 게이트 및 임상 가드레일 (LLM-as-a-Judge)", "7차시 프로젝트 패턴을 접목하여 영양 데이터 일치성, 환각 수치, 의료 가드레일을 3중 검증")

add_card(s8, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "🛡️ 3단계 품질 게이트 (LLM-as-a-Judge) 구조", [
    "Gate 1. 영양 데이터 관련성 평가 (Relevance Check):\n  • 사용자 입력 식단 ↔ 식약처 조회 식품 일치 여부 판정 (Yes/No)\n  • 불일치 시 검색 쿼리 자동 재작성 (CRAG 보정 루프)",
    "Gate 2. 환각 수치 검출 (Hallucination Grounding):\n  • LLM 응답 속 칼로리/탄단지 수치가 DB 실측치와 100% 동일한지 검증\n  • 수치 왜곡 감지 시 DB 조회값으로 강제 재생성",
    "Gate 3. 임상 안전 가드레일 (Clinical Safety):\n  • 극단적 초저열량(거식 위험) 경고 및 영양 면책 안내 자동 삽입"
])

# Self-RAG 실제 실행 로그 터미널 박스
add_code_card(s8, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "Live Execution: Self-RAG Quality Gate Check", [
    "# [Gate 1: 문서 관련성 평가] grade_nutrition_docs()",
    "BinaryGradeNutrition(binary_score='yes', score=1.0) -> ✅ 통과",
    "",
    "# [Gate 2: 환각 검출] check_hallucination_nutrition()",
    "GroundingCheck: {'DB_kcal': 135.0, 'LLM_kcal': 135.0} -> ✅ 일치",
    "",
    "# [Gate 3: 가드레일 검증] check_clinical_safety()",
    "GuardrailCheck: {'disclaimer_included': True, 'safety': 'safe'}",
    "# Status: ✅ 3단계 품질 게이트 ALL PASS (최종 승인 반환)"
], header_color=COLOR_CODE_GREEN)

add_takeaway_strip(s8, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "임상적 안전성 & 신뢰도 극대화 (Clinical Reliability Guaranteed)",
    "단순 생성이 아닌 LLM-as-a-Judge를 통한 3단계 이진 평가 및 자동 보정 루프를 구축하여, 영양 수치의 환각을 원천 차단하고 안전한 다이어트 코칭만을 사용자에게 전달합니다."
)

# ==========================================
# Slide 09: 핵심 기술 ① - 멀티모달 & Function Calling
# ==========================================
s9 = prs.slides.add_slide(blank_layout)
set_slide_background(s9, COLOR_CANVAS_LIGHT)
add_fixed_header(s9, "Core Technology 1", "멀티모달 AI 코치 & Function Calling 실측 실행 로그", "식약처 공공데이터베이스 강제 바인딩으로 환각율 0% 영양 분석 실증")

add_card(s9, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "💡 Function Calling 메커니즘 & 3단계 프롬프트", [
    "도구 바인딩: `tools=[search_food_nutrition]` 모델 등록",
    "자동 도구 호출: 식단 질문 인식 시 LLM이 파이썬 검색 함수 실행",
    "Step 1. 영양소 요약: 총 칼로리 및 탄·단·지, 나트륨 상세 표기",
    "Step 2. 목표치 진단: 사용자 일일 목표 대비 과부족 평가",
    "Step 3. 대안 메뉴 추천: 다음 식사 권장 메뉴 및 실천 팁 제안",
    "메타데이터 생성: `<!-- MEAL_DATA: {...} -->` 구조화 태깅"
])

# 실제 도구 실행 입출력 터미널 박스
add_code_card(s9, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "Live Tool Execution: search_food_nutrition()", [
    "# [입력] query = '닭가슴살 샐러드'",
    "# [식약처 CSV DB 실측 반환 JSON]:",
    "{",
    "  '식품명': '콜라겐이첨가된훈제닭가슴살',",
    "  '기준량': '100g',",
    "  '칼로리(kcal)': 135.0,",
    "  '단백질(g)': 26.0,  '지방(g)': 1.5,  '탄수화물(g)': 3.0,",
    "  '나트륨(mg)': 58.0",
    "}",
    "# [생성된 메타데이터 태그]:",
    "<!-- MEAL_DATA: {'food_name': '훈제닭가슴살', 'calories': 135} -->"
], header_color=COLOR_CODE_CYAN)

add_takeaway_strip(s9, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "기술적 핵심 의의 (Zero-Hallucination Verified)",
    "LLM이 임의로 수치를 추측하지 않고 파이썬 표준 라이브러리를 통해 공공데이터셋 실측치(135kcal, 단백질 26g)를 조회하여 100% 신뢰할 수 있는 코칭을 생성합니다."
)

# ==========================================
# Slide 10: 핵심 기술 ② - METs 운동 계산 & 영양 RAG
# ==========================================
s10 = prs.slides.add_slide(blank_layout)
set_slide_background(s10, COLOR_CANVAS_LIGHT)
add_fixed_header(s10, "Core Technology 2", "METs 운동 소모 칼로리 & 영양 RAG 실측 실행 로그", "과학적 운동 대사량 산출, 임상 영양 백과 RAG, 다중 모델 무중단 폴백 실증")

add_card(s10, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "🏃 METs 운동 계산 & 영양 RAG 아키텍처", [
    "ACSM 공식: 소모 칼로리 = 1.05 × METs × 체중(kg) × 시간(hr)",
    "20+ 표준 운동 DB: 러닝(8.5), 웨이트(5.5), 수영(7.5), 줄넘기(10.0)",
    "임상 영양 RAG: 혈당 스파이크 방지, 정체기 리피드, 단백질 흡수 타이밍",
    "5대 Flash 모델 폴백: 503/429 발생 시 0.5초 내 자동 순차 전환",
    "순 칼로리(Net Calories) 연동: 섭취량 - 운동 소모량"
])

# 실제 운동 및 RAG 실행 로그 터미널 박스
add_code_card(s10, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "Live Execution: METs & Nutrition RAG", [
    "# [1. 운동 도구 실행] calculate_exercise_calories('러닝', 30, 70kg)",
    "{'운동명': '러닝', 'METs': 8.5, '소모칼로리(kcal)': 312.4}",
    "",
    "# [2. 영양 RAG 지식 검색] search_nutrition_knowledge('혈당')",
    "{",
    "  '주제': '혈당 스파이크 방지 및 식사 순서',",
    "  '가이드': '[식이섬유 -> 단백질/지방 -> 탄수화물] 순서 섭취'",
    "}",
    "# [3. 모델 폴백 상태]: Active Model = gemini-3.6-flash (정상)"
], header_color=COLOR_CODE_GREEN)

add_takeaway_strip(s10, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "무중단 서비스 보장 (Fault-Tolerant Resilience)",
    "운동 소모 칼로리 산출과 임상 영양 RAG 지식이 완벽히 동작하며, 5개 Flash 모델 간의 자동 폴백 루프를 통해 503/429 장애 없는 연속 서비스를 보장합니다."
)

# ==========================================
# Slide 11: 핵심 기술 ③ - 신체 맞춤 영양 추천 & 보안 DB
# ==========================================
s11 = prs.slides.add_slide(blank_layout)
set_slide_background(s11, COLOR_CANVAS_LIGHT)
add_fixed_header(s11, "Core Technology 3", "신체 정보 기반 맞춤 영양 자동 추천 & 보안 DB", "미플린-세인트지올(Mifflin-St Jeor) 과학적 공식을 통한 개인화 설정")

add_card(s11, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "📏 BMR / TDEE 맞춤 영양 추천 공식", [
    "기초대사량 (BMR) 정밀 계산:\n   - 남성: (10×체중) + (6.25×키) - (5×나이) + 5\n   - 여성: (10×체중) + (6.25×키) - (5×나이) - 161",
    "활동대사량 (TDEE) 반영: 운동 빈도별 1.2 ~ 1.725 계수 적용",
    "목표별 칼로리/단백질 최적화:\n   - 감량(다이어트): TDEE - 450kcal / 체중 1kg당 1.6g 단백질\n   - 벌크업: TDEE + 300kcal / 체중 1kg당 1.8g 단백질",
    "신체 스펙 수정 시 원클릭 재계산 지원 ([내 설정] 탭)"
])

add_card(s11, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "🗄️ SQLite 데이터베이스 아키텍처", [
    "users 테이블: ID, 비밀번호 해시, 솔트, 성별, 나이, 키, 몸무게, 목표 칼로리, 목표 단백질, 텔레그램 Chat ID",
    "meal_records 테이블: 일자별 식사 구분(아침/점심/저녁/간식), 음식명, 칼로리, 탄단지, 당류, 나트륨",
    "exercise_records 테이블: 운동명, 운동 시간(분), 소모 칼로리(kcal), 메모",
    "보안 암호화: SHA-256 + Salt 단방향 해싱으로 계정 안전 보장"
])

add_takeaway_strip(s11, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "개인화 데이터 영속성 (Personalized Data Persistence)",
    "회원가입 시 입력된 신체 스펙에 맞춰 일일 권장량이 자동 계산되며, 언제든 [내 설정] 탭에서 체중 변화에 맞춰 목표를 재계산하고 SQLite DB에 안전하게 격리 저장됩니다."
)

# ==========================================
# Slide 12: 핵심 기능 ④ - Human-in-the-Loop 스마트 저장
# ==========================================
s12 = prs.slides.add_slide(blank_layout)
set_slide_background(s12, COLOR_CANVAS_LIGHT)
add_fixed_header(s12, "Core Feature 1", "Human-in-the-Loop 스마트 자동 저장 & 실측 쿼리", "AI 분석 결과를 사용자가 원클릭 컨펌하고, 실시간 순 칼로리 집계 쿼리로 대시보드 갱신")

add_card(s12, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "🍱 Human-in-the-Loop 스마트 저장 (HIL)", [
    "메타데이터 파서 연동: `parse_agent_metadata()` 함수가 JSON 자동 추출",
    "인터랙티브 컨펌 카드: AI 응답 하단에 [감지된 식단 / 운동] 카드 렌더링",
    "원클릭 승인 & 저장: [💾 이 식단 DB에 바로 저장] 클릭 시 즉시 SQLite 기록",
    "실시간 대시보드 갱신: 순 칼로리(Net Calories) 게이지 및 도넛 차트 즉각 반영"
])

# 실제 데이터베이스 쿼리 실행 결과 터미널 박스
add_code_card(s12, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "Live Database Query: get_daily_summary()", [
    "# [SQLite 일별 종합 집계 쿼리 실측 반환값]:",
    "{",
    "  'date': '2026-08-29',",
    "  'total_cal': 520.0,       # 섭취 칼로리",
    "  'total_burned': 312.4,    # 운동 소모 칼로리",
    "  'net_cal': 207.6,         # ✨ 순 칼로리 (520 - 312.4)",
    "  'total_protein': 36.4,    # 섭취 단백질(g)",
    "  'records_count': 2,       'exercise_count': 1",
    "}",
    "# Status: ✅ 200 OK (DB Record Insert & Query Verified)"
], header_color=COLOR_CODE_YELLOW)

# 하단 4개 지표 카드
add_metric_card(s12, Inches(0.8), Inches(5.35), Inches(2.70), Inches(1.45), "Daily Intake", "520.0 kcal", "일일 목표 2,000 kcal 대비", COLOR_PRIMARY)
add_metric_card(s12, Inches(3.81), Inches(5.35), Inches(2.70), Inches(1.45), "Calories Burned", "-312.4 kcal", "🔥 러닝 30분 소모 실측", COLOR_EMERALD)
add_metric_card(s12, Inches(6.82), Inches(5.35), Inches(2.70), Inches(1.45), "Net Calories", "207.6 kcal", "✨ 순 섭취 칼로리", COLOR_PURPLE)
add_metric_card(s12, Inches(9.83), Inches(5.35), Inches(2.70), Inches(1.45), "Protein Intake", "36.4 g", "일일 목표 100g 대비", COLOR_AMBER)

# ==========================================
# Slide 13: 핵심 기능 ⑤ - 텔레그램 연동 및 월간 결산 자동화
# ==========================================
s13 = prs.slides.add_slide(blank_layout)
set_slide_background(s13, COLOR_CANVAS_LIGHT)
add_fixed_header(s13, "Core Feature 2", "텔레그램 연동 및 월간 결산 자동화 파이프라인", "앱에 직접 접속하지 않아도 매월 1일 개인 메신저로 한 달 결산 리포트 자동 전달")

add_card(s13, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "📱 텔레그램 연동 및 스케줄러 아키텍처", [
    "Chat ID 연동: 텔레그램 봇으로 고유 ID 확인 후 원클릭 등록",
    "백그라운드 스케줄러: `scheduler.py` 매월 1일 자정 브로드캐스트",
    "Matplotlib 차트 렌더링: 월간 일별 칼로리 추이 그래프 이미지 자동 생성",
    "맞춤 AI 총평: 목표 달성 성공률에 따른 격려 및 피드백 전송",
    "원클릭 즉시 테스트: 웹 [내 설정] 탭에서 이번 달 리포트 즉시 수신 가능"
])

# 실제 텔레그램 발송 메시지 페이로드 터미널 박스
add_code_card(s13, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "Live Telegram Bot Message Payload", [
    "📢 *[AI 다이어트 코치]* 2026년 8월 결산 리포트",
    "----------------------------------------",
    "• 총 기록 일수: 18일 (총 42회 식사)",
    "• 월간 총 섭취 칼로리: 34,200 kcal (일평균 1,900 kcal)",
    "• 목표 달성 성공률: 83.3% (15일 성공)",
    "• 🏆 최다 섭취 메뉴 TOP 3: 닭가슴살(14회), 현미밥(12회), 샐러드(10회)",
    "----------------------------------------",
    "💬 *[AI 코치 총평]*: 목표 성공률 83% 달성을 축하드립니다! 👏",
    "📸 [월간 칼로리 추이 그래프 이미지 첨부 완료]"
], header_color=COLOR_FOCUS_BLUE)

add_takeaway_strip(s13, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "지속 가능한 다이어트 코칭 경험 (Continuous Engagement)",
    "사용자가 앱을 능동적으로 켜지 않더라도 정기적인 외부 채널 리포트를 통해 식습관을 되돌아보고 지속적인 동기부여를 얻을 수 있는 완성형 서비스 루프를 제공합니다."
)

# ==========================================
# Slide 14: 강의 커리큘럼 연계 및 기술적 의의
# ==========================================
s14 = prs.slides.add_slide(blank_layout)
set_slide_background(s14, COLOR_CANVAS_LIGHT)
add_fixed_header(s14, "Course Mapping", "라이브스터디(1~7차시) 커리큘럼 연계 및 기술적 의의", "강의에서 다룬 핵심 이론 및 프레임워크를 실제 동작하는 풀스택 서비스로 완성")

add_card(s14, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "📚 차시별 핵심 이론 접목 내역", [
    "1차시 (프롬프트 엔지니어링): 페르소나 부여 및 3단계 응답 구조 System Instruction",
    "2~4차시 (데이터 전처리 & RAG): 식약처 CSV 정제 및 키워드 기반 영양 매칭",
    "5차시 (Tool Calling & ReAct): LLM 도구 바인딩 및 함수 자동 호출 에이전트",
    "6차시 (LangGraph & 멀티모달): 세션 상태(State) 관리 및 사진+텍스트 동시 처리",
    "7차시 (Self-RAG 3단계 품질 게이트 & Adaptive Routing): 3중 검증 및 스마트 저장 컨펌"
])

add_card(s14, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "🏆 프로젝트의 기술적 의의", [
    "단순 튜토리얼을 넘은 풀스택 완성: LLM 단독 실행이 아닌 DB, UI, 외부 메신저까지 결합",
    "할루시네이션 완벽 통제: 공공데이터 검색 도구를 강제하여 의료/영양 도메인 신뢰성 확보",
    "실제 사용 가능한 완성도: 비밀번호 암호화, 개인 DB 격리, 5대 모델 무중단 폴백 구축",
    "글로벌 클라우드 배포: Streamlit Cloud 및 GitHub CI/CD 자동 배포 완료"
])

add_takeaway_strip(s14, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "학습 성과 요약 (Learning Takeaway)",
    "LLM API 호출 기초부터 LangGraph 기반 상태 관리, Self-RAG 3단계 품질 게이트, Human-in-the-Loop 패턴까지 강의의 전 과정을 실전 서비스 형태로 구현하여 기술적 이해도를 극대화했습니다."
)

# ==========================================
# Slide 15: 배포 성과 및 향후 발전 로드맵
# ==========================================
s15 = prs.slides.add_slide(blank_layout)
set_slide_background(s15, COLOR_CANVAS_LIGHT)
add_fixed_header(s15, "Summary & Future Work", "서비스 배포 성과 및 향후 발전 로드맵", "글로벌 배포 완료 및 향후 스마트 헬스케어 생태계로의 확장 가능성")

add_card(s15, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "🚀 서비스 구현 및 배포 성과", [
    "GitHub 오픈소스 저장소: rye6837-web/impossible_to_get_lost_my_weight",
    "Streamlit Community Cloud 배포: 모바일/PC 반응형 웹 서비스 운영 중",
    "핵심 성과: 식단 사진 한 장으로 표준 영양 분석, 운동 칼로리 차감, 정기 결산 자동화 완성",
    "안정성: 다중 모델 폴백으로 503/429 오류 0% 달성"
])

add_card(s15, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "🔮 향후 확장 로드맵 (Roadmap)", [
    "스마트워치 / 헬스 데이터 연동: 애플워치·갤럭시워치 걸음 수 및 활동 칼로리 실시간 동기화",
    "AI 맞춤 식단 플래너 & 장바구니: 부족한 영양소를 채워주는 일주일 식단표 생성 및 밀키트 구매 연계",
    "연속 혈당 측정기(CGM) 데이터 접목: 혈당 스파이크 방지 식사 순서 실시간 코칭 기능 추가"
])

add_takeaway_strip(s15, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "감사 인사 및 Q&A",
    "경청해 주셔서 감사합니다. 질문 및 피드백을 환영합니다!"
)

# 저장
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AI_Diet_Coach_Presentation.pptx")
prs.save(output_path)
print(f"✅ 트러블슈팅 슬라이드가 포함된 총 15장 PPT 생성 완료: {output_path}")
