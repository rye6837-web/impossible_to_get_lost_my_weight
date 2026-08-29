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
    """고정 좌표 헤더 렌더링"""
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
    """간결화된 텍스트 카드"""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1.5)
    
    tb = slide.shapes.add_textbox(left + Inches(0.28), top + Inches(0.24), width - Inches(0.56), height - Inches(0.48))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p_title = tf.paragraphs[0]
    p_title.text = title
    p_title.font.name = FONT_NAME
    p_title.font.size = Pt(15)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_INK_MAIN
    p_title.space_after = Pt(10)
    
    for item in items:
        p = tf.add_paragraph()
        p.text = f"•  {item}"
        p.font.name = FONT_NAME
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_TEXT_BODY
        p.space_after = Pt(6)
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
        p.font.size = Pt(10)
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
        p.space_after = Pt(2.5)
    return card

def add_takeaway_strip(slide, left, top, width, height, title, description, accent_color=COLOR_PRIMARY):
    """하단 테이크어웨이 스트립 (간결화)"""
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
    """하단 KPI 지표 카드"""
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
# Slide 01: 표지 (Cover)
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
p_sub.text = "식약처 표준 DB · Self-RAG 3단계 품질 게이트 · LangGraph 라우팅 기반 개인 맞춤형 플랫폼"
p_sub.font.name = FONT_NAME
p_sub.font.size = Pt(15)
p_sub.font.color.rgb = RGBColor(203, 213, 225)
p_sub.space_after = Pt(32)

p_info = tf1.add_paragraph()
p_info.text = "발표자 : 메타코드M 라이브 스터디  |  스택 : Gemini Flash · LangGraph · Self-RAG · SQLite · Streamlit · Telegram"
p_info.font.name = FONT_NAME
p_info.font.size = Pt(11.5)
p_info.font.color.rgb = COLOR_TEXT_ON_DARK_MUTED

# ==========================================
# Slide 02: 목차 (Table of Contents)
# ==========================================
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2, COLOR_CANVAS_LIGHT)
add_fixed_header(s2, "Table of Contents", "프레젠테이션 목차", "기획 배경부터 아키텍처, 트러블슈팅, Self-RAG 품질 검증, 기능 실측까지의 핵심 요약")

add_card(s2, Inches(0.8), Inches(1.75), Inches(2.75), Inches(3.4), "Ⅰ. 프로젝트 개요", [
    "01. 기획 배경 & 문제 정의",
    "02. 서비스 핵심 가치",
    "03. 기존 대비 차별점"
])
add_card(s2, Inches(3.79), Inches(1.75), Inches(2.75), Inches(3.4), "Ⅱ. 시스템 & 복원력", [
    "04. 풀스택 시스템 아키텍처",
    "05. 파일 & 디렉터리 구조",
    "06. 503/429 과부하 트러블슈팅",
    "07. LangGraph 조건부 라우팅"
])
add_card(s2, Inches(6.78), Inches(1.75), Inches(2.75), Inches(3.4), "Ⅲ. 핵심 기술 & 실측", [
    "08. Self-RAG 3단계 품질 게이트",
    "09. Function Calling 영양 실측",
    "10. METs 운동 & 영양 RAG",
    "11. BMR 맞춤 추천 & 보안 DB",
    "12. HIL 스마트 저장 & 텔레그램"
])
add_card(s2, Inches(9.77), Inches(1.75), Inches(2.75), Inches(3.4), "Ⅳ. 성과 & 로드맵", [
    "13. 1~7차시 커리큘럼 연계",
    "14. 글로벌 클라우드 배포 성과",
    "15. 스마트 헬스케어 확장 계획"
])

add_takeaway_strip(s2, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45), 
    "핵심 발표 목표 (Key Objective)", 
    "식약처 DB 강제 바인딩(환각 0%), 503 과부하를 0.5초 만에 방어하는 5대 Flash 모델 폴백, Self-RAG 3단계 검증까지 갖춘 프로덕션 풀스택 구현 과정을 전달합니다."
)

# ==========================================
# Slide 03: 기획 배경 및 문제 정의
# ==========================================
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3, COLOR_CANVAS_LIGHT)
add_fixed_header(s3, "Problem & Solution", "기획 배경 및 해결 과제", "수동 기록의 피로도와 일반 LLM의 환각(Hallucination) 한계를 동시 극복")

add_card(s3, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "⚠️ 기존 다이어트 앱 & LLM의 한계", [
    "수동 입력 피로도: 식사마다 g 수 검색 및 직접 타이핑",
    "치명적 환각 (Hallucination): 임의로 칼로리 수치 왜곡 생성",
    "개인화 결여: 사용자 체형/목표(BMR/TDEE) 미반영",
    "단일 모델 장애: 트래픽 과부하(503/429) 시 서비스 전면 중단"
])

add_card(s3, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "✨ AI 코치의 해결 솔루션", [
    "📸 사진 식단 분석: 멀티모달 비전으로 메뉴 자동 인식",
    "🔍 식약처 표준 DB 도구: Function Calling으로 신뢰성 100%",
    "🛡️ Self-RAG 품질 게이트: 관련성·환각·임상 가드레일 3중 검증",
    "🏃 METs 운동 대사량 연동: 소모 칼로리 산출 및 순 칼로리 관리"
])

add_takeaway_strip(s3, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "핵심 가치 제안 (Value Proposition)",
    "사진 1장 또는 자연어 대화만으로 식약처 표준 영양 데이터를 확인하고, 원클릭으로 DB에 저장하여 실시간 순 칼로리 대시보드와 정기 결산 리포트를 제공합니다."
)

# ==========================================
# Slide 04: 전체 시스템 구조도
# ==========================================
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4, COLOR_CANVAS_LIGHT)
add_fixed_header(s4, "System Architecture", "전체 풀스택 시스템 아키텍처", "UI부터 AI 엔진, 로컬 데이터베이스, 외부 메신저 알림까지의 통합 구조")

add_card(s4, Inches(0.8), Inches(1.75), Inches(3.71), Inches(3.4), "🖥️ Frontend (UI/UX)", [
    "Streamlit 기반 반응형 인터페이스",
    "Plotly 게이지·도넛·시계열 차트",
    "카메라 촬영 & 이미지 업로더",
    "사용자별 독립 로그인 세션 유지"
])

add_card(s4, Inches(4.81), Inches(1.75), Inches(3.71), Inches(3.4), "🤖 AI Engine & Self-RAG", [
    "Gemini Flash 초고속 멀티모달",
    "Self-RAG 3단계 품질 게이트",
    "Tool 1: 식약처 CSV 영양 검색",
    "Tool 2: ACSM METs 운동 계산기",
    "Tool 3: 혈당·정체기 영양 RAG"
])

add_card(s4, Inches(8.82), Inches(1.75), Inches(3.71), Inches(3.4), "💾 Database & Services", [
    "SQLite: users, meal, exercise",
    "SHA-256 + Salt 비밀번호 암호화",
    "Telegram Bot 월간 리포트 발송",
    "scheduler.py 매월 1일 브로드캐스트"
])

# 하단 4개 기술 메트릭 리본
add_metric_card(s4, Inches(0.8), Inches(5.35), Inches(2.70), Inches(1.45), "UI Framework", "Streamlit", "반응형 인터랙티브 웹", COLOR_PRIMARY)
add_metric_card(s4, Inches(3.81), Inches(5.35), Inches(2.70), Inches(1.45), "AI Engine", "Gemini + Self-RAG", "3대 품질 게이트 & Tool 바인딩", COLOR_EMERALD)
add_metric_card(s4, Inches(6.82), Inches(5.35), Inches(2.70), Inches(1.45), "Storage & Security", "SQLite + Salt", "개인 식단·운동 영속 격리", COLOR_PURPLE)
add_metric_card(s4, Inches(9.83), Inches(5.35), Inches(2.70), Inches(1.45), "Automation", "Telegram Bot", "매월 1일 정기 리포트 발송", COLOR_AMBER)

# ==========================================
# Slide 05: 프로젝트 폴더 및 파일 아키텍처
# ==========================================
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5, COLOR_CANVAS_LIGHT)
add_fixed_header(s5, "Project Structure", "프로젝트 디렉터리 & 파일 아키텍처", "모듈화 및 네임스페이스 격리 원칙(Clean Architecture) 적용")

add_card(s5, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "📁 핵심 모듈별 책임과 역할", [
    "`app.py`: Streamlit 메인 엔트리포인트 (UI/UX, 4대 대시보드)",
    "`ai_agent/diet_agent.py`: 5대 Flash 모델 폴백 & 3대 Tool 바인딩",
    "`app_tools/`: 전문 기능 분리 (식약처 DB, METs 계산, 영양 RAG)",
    "`app_db/database.py`: SQLite DB 풀, Salt 암호화, 식단/운동 CRUD",
    "`app_services/telegram_service.py`: 텔레그램 연동 & 차트 생성",
    "`scheduler.py`: 매월 1일 결산 브로드캐스트 스케줄러"
])

add_code_card(s5, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "Project Directory Tree Structure", [
    "Project/",
    "├── app.py                      # 메인 웹 대시보드",
    "├── ai_agent/                   # AI 에이전트 & 다중 폴백",
    "│   └── diet_agent.py           # Gemini Flash 에이전트",
    "├── app_tools/                  # 전문 도구 (Tool Use)",
    "│   ├── food_db.py              # 식약처 CSV 영양 검색",
    "│   ├── exercise_tool.py        # ACSM METs 운동 계산기",
    "│   └── nutrition_rag.py        # 혈당·정체기 RAG 지식",
    "├── app_db/                     # SQLite 데이터베이스",
    "│   └── database.py             # 사용자·식단·운동 CRUD",
    "├── app_services/               # 외부 알림 서비스",
    "│   └── telegram_service.py     # 텔레그램 봇 & Matplotlib",
    "└── scheduler.py                # 매월 1일 결산 데몬"
], header_color=COLOR_CODE_CYAN)

add_takeaway_strip(s5, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "클린 아키텍처 & 배포 무결점 (Clean Architecture)",
    "서버 전역 패키지와의 이름 충돌을 방지하기 위해 고유 네임스페이스(`app_tools/`, `ai_agent/`, `app_db/`)를 채택하여 클라우드 무결점 배포를 달성했습니다."
)

# ==========================================
# Slide 06: 실무 트러블슈팅
# ==========================================
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6, COLOR_CANVAS_LIGHT)
add_fixed_header(s6, "Troubleshooting", "실무 트러블슈팅 & 복원력 구축", "503 과부하 및 429 속도제한 에러 방어를 위한 5대 Flash 모델 다중 폴백 실증")

add_card(s6, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "🚨 3대 핵심 이슈 & 해결 조치", [
    "Issue 1. `503 UNAVAILABLE` (모델 일시 과부하)\n  ➔ 5대 Flash 모델 간 `0.5초 무중단 자동 폴백` 구축",
    "Issue 2. `429 RESOURCE_EXHAUSTED` (분당 속도 제한)\n  ➔ Pro 모델 배제, 분당 15회 넉넉한 Flash 계열로 최적화",
    "Issue 3. Cloud 배포 시 `ModuleNotFoundError`\n  ➔ 고유 네임스페이스(`app_tools/`, `ai_agent/`) 전면 리팩토링"
])

add_code_card(s6, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "Live Fallback Execution Log (Self-Healing)", [
    "# [1. 음식 사진 식단 분석 요청 전송]",
    "Attempt 1: Call [gemini-3.6-flash] with food image...",
    "⚠️ [gemini-3.6-flash] 503 UNAVAILABLE (High Demand Spikes)",
    "",
    "# [2. 시스템 자동 감지 & 0.5s 내 예비 모델 전환]",
    "🔄 Auto-Switching: [gemini-3.7-flash]",
    "Attempt 2: Call [gemini-3.7-flash] with tools & session...",
    "",
    "# [3. 무중단 정상 응답 복구]",
    "✅ [gemini-3.7-flash] 200 OK (분석 성공)",
    "Output: {'food_name': '고구마와 닭가슴살소시지', 'kcal': 380}"
], header_color=COLOR_ROSE)

add_takeaway_strip(s6, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "고가용성 복원력 (High Availability Resilience)",
    "단일 모델 장애 시 서비스가 중단되는 문제를 `[3.6-flash ➔ 3.7-flash ➔ 3.5-flash ➔ flash-latest ➔ 2.5-flash-lite]` 캐스케이딩 폴백으로 완벽히 해결했습니다."
)

# ==========================================
# Slide 07: LangGraph 조건부 라우팅 워크플로우
# ==========================================
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7, COLOR_CANVAS_LIGHT)
add_fixed_header(s7, "Agent Workflow", "LangGraph 기반 조건부 라우팅 워크플로우", "사용자 입력(사진/텍스트) 의도에 따른 4대 전문 하위 도구 분기")

add_node(s7, Inches(5.3), Inches(1.75), Inches(2.73), Inches(0.55), "🏁 __start__", "사용자 입력 수신 (사진/텍스트)", RGBColor(99, 102, 241))
add_node(s7, Inches(4.8), Inches(2.45), Inches(3.73), Inches(0.65), "🔀 Intent Router (check)", "질문 의도 분류 & 조건부 엣지", COLOR_INK_MAIN)

add_node(s7, Inches(0.8), Inches(3.30), Inches(2.70), Inches(1.50), "🍱 식단 분석 핸들러\n(food_handler)", "Tool: search_food_nutrition\n식약처 CSV 표준 영양 검색\n<!-- MEAL_DATA --> 생성", COLOR_PRIMARY)
add_node(s7, Inches(3.81), Inches(3.30), Inches(2.70), Inches(1.50), "🏃 운동 계산 핸들러\n(exercise_handler)", "Tool: calculate_exercise_calories\nACSM METs 공식 계산\n<!-- EXERCISE_DATA --> 생성", COLOR_EMERALD)
add_node(s7, Inches(6.82), Inches(3.30), Inches(2.70), Inches(1.50), "📚 영양 백과 RAG\n(rag_handler)", "Tool: search_nutrition_knowledge\n혈당·정체기 임상 영양 지식\n전문 코칭 가이드", COLOR_PURPLE)
add_node(s7, Inches(9.83), Inches(3.30), Inches(2.70), Inches(1.50), "💬 일반 코칭 핸들러\n(general_handler)", "일상 웰니스 대화\n동기부여 및 멘탈 케어\n식단 목표 점검", COLOR_AMBER)

add_node(s7, Inches(2.5), Inches(5.00), Inches(8.33), Inches(0.75), "👤 Human-in-the-Loop 스마트 저장 컨펌", "AI 추출 메타데이터 카드 렌더링 ➔ 사용자 원클릭 승인 ➔ SQLite DB 즉시 기록", COLOR_EMERALD)
add_node(s7, Inches(5.3), Inches(6.00), Inches(2.73), Inches(0.55), "🏁 __end__", "대시보드 실시간 갱신 완료", RGBColor(71, 85, 105))

# ==========================================
# Slide 08: Self-RAG 3단계 품질 게이트
# ==========================================
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8, COLOR_CANVAS_LIGHT)
add_fixed_header(s8, "Self-RAG Quality Gate", "Self-RAG 3단계 품질 게이트 (LLM-as-a-Judge)", "7차시 패턴 적용: 영양 일치성, 환각 수치, 임상 가드레일 3중 검증")

add_card(s8, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "🛡️ 3단계 이진 품질 평가 구조", [
    "Gate 1. 영양 관련성 검증 (Relevance Check):\n  • 사용자 식단 ↔ DB 조회 식품 일치 여부 판정 (Yes/No)\n  • 불일치 시 쿼리 자동 재작성 (CRAG 보정)",
    "Gate 2. 환각 수치 검출 (Hallucination Grounding):\n  • 칼로리/탄단지 수치와 DB 실측치 100% 일치 검증",
    "Gate 3. 임상 안전 가드레일 (Clinical Safety):\n  • 초저열량 경고 및 의학적 면책 안내 자동 삽입"
])

add_code_card(s8, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "Live Execution: Self-RAG Quality Gate Check", [
    "# [Gate 1: 관련성 평가] grade_nutrition_docs()",
    "BinaryGradeNutrition(score='yes') -> ✅ 통과",
    "",
    "# [Gate 2: 환각 검출] check_hallucination_nutrition()",
    "GroundingCheck: {'DB_kcal': 135.0, 'LLM_kcal': 135.0} -> ✅ 일치",
    "",
    "# [Gate 3: 가드레일 검증] check_clinical_safety()",
    "GuardrailCheck: {'disclaimer': True, 'safety': 'safe'}",
    "# Status: ✅ 3단계 품질 게이트 ALL PASS"
], header_color=COLOR_CODE_GREEN)

add_takeaway_strip(s8, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "임상적 안전성 & 환각 차단 (Clinical Reliability)",
    "LLM-as-a-Judge 기반의 3단계 이진 평가 및 자동 보정 루프를 구축하여 영양 수치의 환각을 원천 차단했습니다."
)

# ==========================================
# Slide 09: 핵심 기술 ① - 멀티모달 & Function Calling
# ==========================================
s9 = prs.slides.add_slide(blank_layout)
set_slide_background(s9, COLOR_CANVAS_LIGHT)
add_fixed_header(s9, "Core Technology 1", "멀티모달 AI & Function Calling 영양 실측", "식약처 공공데이터베이스 강제 바인딩으로 환각율 0% 영양 분석 실증")

add_card(s9, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "💡 도구 바인딩 메커니즘 & 3단계 프롬프트", [
    "도구 바인딩: `tools=[search_food_nutrition]` 등록",
    "자동 함수 호출: 식단 인식 시 파이썬 검색 함수 실행",
    "3단계 코칭: ① 영양소 요약 ➔ ② 목표 대비 진단 ➔ ③ 메뉴 제안",
    "메타데이터 태깅: `<!-- MEAL_DATA: {...} -->` 자동 추출"
])

add_code_card(s9, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "Live Tool Execution: search_food_nutrition()", [
    "# [입력] query = '닭가슴살 샐러드'",
    "# [식약처 CSV DB 실측 반환 JSON]:",
    "{",
    "  '식품명': '콜라겐이첨가된훈제닭가슴살',",
    "  '기준량': '100g',  '칼로리(kcal)': 135.0,",
    "  '단백질(g)': 26.0,  '지방(g)': 1.5,  '탄수화물(g)': 3.0,",
    "  '나트륨(mg)': 58.0",
    "}",
    "# [생성된 메타데이터 태그]:",
    "<!-- MEAL_DATA: {'food_name': '훈제닭가슴살', 'calories': 135} -->"
], header_color=COLOR_CODE_CYAN)

add_takeaway_strip(s9, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "100% 신뢰성 검증 (Zero-Hallucination Verified)",
    "LLM이 수치를 추측하지 않고 파이썬 함수가 공공데이터 실측치(135kcal, 단백질 26g)를 조회하여 답변을 생성합니다."
)

# ==========================================
# Slide 10: 핵심 기술 ② - METs 운동 계산 & 영양 RAG
# ==========================================
s10 = prs.slides.add_slide(blank_layout)
set_slide_background(s10, COLOR_CANVAS_LIGHT)
add_fixed_header(s10, "Core Technology 2", "METs 운동 계산 & 영양 RAG 실측 로그", "ACSM 운동 대사량 산출 공식 및 임상 영양 백과 RAG 연동")

add_card(s10, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "🏃 METs 운동 계산 & 영양 RAG 아키텍처", [
    "ACSM 공식: `소모 칼로리 = 1.05 × METs × 체중(kg) × 시간(hr)`",
    "20+ 운동 DB: 러닝(8.5), 웨이트(5.5), 수영(7.5), 사이클(7.0)",
    "영양 RAG: 혈당 스파이크 방지 식사순서, 정체기 리피드 전략",
    "순 칼로리(Net Calories) 연동: 섭취 칼로리 - 운동 소모량"
])

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
    "과학적 대사량 관리 (Scientific Energy Balance)",
    "사용자의 체중과 표준 METs 계수를 기반으로 운동 소모 칼로리를 정밀 산출하여 순 칼로리 균형을 관리합니다."
)

# ==========================================
# Slide 11: 핵심 기술 ③ - 신체 맞춤 영양 추천 & 보안 DB
# ==========================================
s11 = prs.slides.add_slide(blank_layout)
set_slide_background(s11, COLOR_CANVAS_LIGHT)
add_fixed_header(s11, "Core Technology 3", "신체 정보 기반 맞춤 영양 추천 & 보안 DB", "미플린-세인트지올(Mifflin-St Jeor) 과학적 공식 및 SQLite 암호화")

add_card(s11, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "📏 BMR / TDEE 맞춤 추천 알고리즘", [
    "BMR 산출 (Mifflin-St Jeor):\n  • 남: (10×체중) + (6.25×키) - (5×나이) + 5\n  • 여: (10×체중) + (6.25×키) - (5×나이) - 161",
    "TDEE 반영: 활동량별 1.2 ~ 1.725 계수 곱연산",
    "목표별 설정: 감량(TDEE - 450kcal), 증량(TDEE + 300kcal)"
])

add_card(s11, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "🗄️ SQLite 데이터베이스 & 보안", [
    "테이블 구조: users, meal_records, exercise_records",
    "단방향 보안 암호화: SHA-256 + 32바이트 Salt 난수 해싱",
    "목표 재계산: [내 설정] 탭에서 체중 변화 시 원클릭 갱신",
    "데이터 무결성: 사용자 ID 기반 완벽한 개인 데이터 격리"
])

add_takeaway_strip(s11, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "개인화 데이터 영속성 (Data Persistence & Security)",
    "사용자 신체 스펙에 최적화된 영양 목표가 자동 산출되며, 모든 기록은 SQLite에 안전하게 암호화 저장됩니다."
)

# ==========================================
# Slide 12: 핵심 기능 ④ - Human-in-the-Loop 스마트 저장
# ==========================================
s12 = prs.slides.add_slide(blank_layout)
set_slide_background(s12, COLOR_CANVAS_LIGHT)
add_fixed_header(s12, "Core Feature 1", "Human-in-the-Loop 스마트 저장 & 통계", "AI 분석 결과를 원클릭 컨펌하여 DB 저장하고 실시간 순 칼로리 차트 반영")

add_card(s12, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "🍱 HIL 스마트 저장 & 인터랙티브 UI", [
    "메타데이터 파서: AI 응답에서 구조화 JSON 자동 추출",
    "스마트 컨펌 카드: 답변 하단에 [식단/운동 정보] 카드 렌더링",
    "원클릭 DB 저장: [💾 이 식단 DB에 바로 저장] 클릭 시 즉시 기록",
    "반응형 대시보드: 일/주/월/년 4대 Plotly 인터랙티브 차트"
])

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
    "# Status: ✅ 200 OK (DB Record Insert Verified)"
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
add_fixed_header(s13, "Core Feature 2", "텔레그램 연동 & 월간 결산 자동화", "매월 1일 개인 메신저로 한 달 결산 리포트 및 칼로리 추이 차트 자동 전송")

add_card(s13, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "📱 텔레그램 리포트 & 스케줄러", [
    "간편 연동: 텔레그램 봇으로 고유 Chat ID 원클릭 등록",
    "자동 스케줄러: `scheduler.py` 매월 1일 자정 브로드캐스트",
    "차트 렌더링: Matplotlib 기반 월간 칼로리 추이 그래프 생성",
    "개인화 총평: 한 달 목표 달성률에 따른 AI 맞춤 코칭 피드백"
])

add_code_card(s13, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "Live Telegram Bot Message Payload", [
    "📢 *[AI 다이어트 코치]* 2026년 8월 결산 리포트",
    "----------------------------------------",
    "• 총 기록 일수: 18일 (총 42회 식사)",
    "• 월간 총 섭취 칼로리: 34,200 kcal (일평균 1,900 kcal)",
    "• 목표 달성 성공률: 83.3% (15일 성공)",
    "• 🏆 최다 섭취 메뉴 TOP 3: 닭가슴살, 현미밥, 샐러드",
    "----------------------------------------",
    "💬 *[AI 코치 총평]*: 목표 성공률 83% 달성을 축하드립니다! 👏",
    "📸 [월간 칼로리 추이 그래프 이미지 첨부 완료]"
], header_color=COLOR_FOCUS_BLUE)

add_takeaway_strip(s13, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "지속적 동기부여 (Continuous Engagement)",
    "앱을 직접 실행하지 않아도 정기 리포트를 개인 메신저로 전달받아 지속적인 식습관 관리가 가능합니다."
)

# ==========================================
# Slide 14: 강의 커리큘럼 연계 및 기술적 의의
# ==========================================
s14 = prs.slides.add_slide(blank_layout)
set_slide_background(s14, COLOR_CANVAS_LIGHT)
add_fixed_header(s14, "Course Mapping", "라이브스터디(1~7차시) 커리큘럼 연계", "강의 핵심 이론 및 프레임워크를 실전 풀스택 프로덕션 서비스로 완성")

add_card(s14, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "📚 차시별 이론 접목 내역", [
    "1차시: 페르소나 및 3단계 응답 구조 프롬프트 엔지니어링",
    "2~4차시: 식약처 CSV 데이터 정제 및 키워드 매칭 로직",
    "5차시: Function Calling 도구 바인딩 & ReAct 에이전트",
    "6차시: 세션 히스토리 메모리 & 멀티모달 사진 처리",
    "7차시: Self-RAG 3단계 품질 게이트 & LangGraph 조건부 라우팅"
])

add_card(s14, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "🏆 프로젝트의 기술적 의의", [
    "풀스택 완성: LLM 단독 실행이 아닌 DB, UI, 메신저 결합",
    "환각 통제: 공공데이터 도구 강제로 의료/영양 신뢰성 확보",
    "무중단 복원력: 5대 Flash 모델 폴백으로 503/429 장애 극복",
    "글로벌 배포: Streamlit Cloud 및 GitHub CI/CD 운영 완료"
])

add_takeaway_strip(s14, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "학습 성과 요약 (Learning Takeaway)",
    "프롬프트부터 RAG, Tool Use, LangGraph, Self-RAG까지 전 과정을 실전 서비스로 구현하여 엔지니어링 역량을 극대화했습니다."
)

# ==========================================
# Slide 15: 배포 성과 및 향후 발전 로드맵
# ==========================================
s15 = prs.slides.add_slide(blank_layout)
set_slide_background(s15, COLOR_CANVAS_LIGHT)
add_fixed_header(s15, "Summary & Future Work", "서비스 배포 성과 & 발전 로드맵", "글로벌 배포 완료 및 스마트 헬스케어 생태계로의 확장 계획")

add_card(s15, Inches(0.8), Inches(1.75), Inches(5.72), Inches(3.4), "🚀 배포 성과 & 서비스 현황", [
    "GitHub 저장소: rye6837-web/impossible_to_get_lost_my_weight",
    "Streamlit Community Cloud: 모바일/PC 반응형 웹 서비스 운영 중",
    "핵심 가치: 사진 1장 식단 분석, 운동 칼로리 차감, 결산 자동화",
    "안정성: 다중 모델 폴백 체계로 무중단 24/7 서비스 유지"
])

add_card(s15, Inches(6.81), Inches(1.75), Inches(5.72), Inches(3.4), "🔮 향후 확장 로드맵 (Roadmap)", [
    "스마트워치 연동: 애플워치·갤럭시워치 활동 칼로리 실시간 동기화",
    "AI 맞춤 식단 플래너: 일주일 식단표 자동 생성 및 밀키트 연계",
    "연속 혈당 측정기(CGM) 접목: 혈당 반응 기반 실시간 코칭 추가"
])

add_takeaway_strip(s15, Inches(0.8), Inches(5.35), Inches(11.73), Inches(1.45),
    "감사 인사 및 Q&A",
    "경청해 주셔서 감사합니다. 질문 및 피드백을 환영합니다!"
)

# 저장
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AI_Diet_Coach_Presentation.pptx")
prs.save(output_path)
print(f"✅ 텍스트가 2/3로 압축 정돈된 15장 PPT 생성 완료: {output_path}")
