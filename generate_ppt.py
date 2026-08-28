import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# 1. 프레젠테이션 객체 생성 및 16:9 비율 설정
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# 컬러 팔레트 정의
COLOR_BG = RGBColor(248, 250, 252)        # 밝은 배경 #F8FAFC
COLOR_PRIMARY = RGBColor(16, 185, 129)     # 에메랄드 그린 #10B981
COLOR_NAVY = RGBColor(30, 41, 59)          # 다크 네이비 #1E293B
COLOR_SECONDARY = RGBColor(59, 130, 246)   # 블루 #3B82F6
COLOR_CARD = RGBColor(255, 255, 255)       # 카드 흰색 #FFFFFF
COLOR_BORDER = RGBColor(226, 232, 240)     # 카드 테두리 #E2E8F0
COLOR_TEXT_MAIN = RGBColor(15, 23, 42)     # 진한 본문 #0F172A
COLOR_TEXT_MUTED = RGBColor(100, 116, 139) # 흐린 텍스트 #64748B
COLOR_ACCENT = RGBColor(245, 158, 11)      # 오렌지 포인트 #F59E0B

blank_layout = prs.slide_layouts[6]

def set_slide_background(slide, color):
    """슬라이드 전체 배경색 설정"""
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = color
    bg.line.fill.background()
    return bg

def add_header(slide, category, title, subtitle=None):
    """일관된 상단 헤더 추가"""
    # 카테고리 태그
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11), Inches(0.4))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    p_c = tf_c.paragraphs[0]
    p_c.text = category.upper()
    p_c.font.size = Pt(11)
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_PRIMARY
    
    # 메인 타이틀
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11), Inches(0.6))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_NAVY
    
    if subtitle:
        p_sub = tf_t.add_paragraph()
        p_sub.text = subtitle
        p_sub.font.size = Pt(12)
        p_sub.font.color.rgb = COLOR_TEXT_MUTED

def add_card(slide, left, top, width, height, title, items, bg_color=COLOR_CARD, border_color=COLOR_BORDER):
    """카드형 정보 박스 추가"""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1.5)
    
    tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.2), width - Inches(0.4), height - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p_title = tf.paragraphs[0]
    p_title.text = title
    p_title.font.size = Pt(15)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_NAVY
    p_title.space_after = Pt(10)
    
    for item in items:
        p = tf.add_paragraph()
        p.text = f"•  {item}"
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_TEXT_MAIN
        p.space_after = Pt(6)
    return card

# ==========================================
# Slide 1: 표지
# ==========================================
s1 = prs.slides.add_slide(blank_layout)
set_slide_background(s1, COLOR_NAVY)

# 표지 장식 박스
dec = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(0.15), Inches(3.8))
dec.fill.solid()
dec.fill.fore_color.rgb = COLOR_PRIMARY
dec.line.fill.background()

tb_title = s1.shapes.add_textbox(Inches(1.2), Inches(1.5), Inches(11), Inches(3.8))
tf1 = tb_title.text_frame
tf1.word_wrap = True

p_tag = tf1.paragraphs[0]
p_tag.text = "AI AGENT & FULL-STACK WELLNESS PROJECT"
p_tag.font.size = Pt(13)
p_tag.font.bold = True
p_tag.font.color.rgb = COLOR_PRIMARY
p_tag.space_after = Pt(12)

p_main = tf1.add_paragraph()
p_main.text = "🥗 AI 다이어트 & 영양 코칭 서비스"
p_main.font.size = Pt(36)
p_main.font.bold = True
p_main.font.color.rgb = RGBColor(255, 255, 255)
p_main.space_after = Pt(14)

p_sub = tf1.add_paragraph()
p_sub.text = "식약처 표준 영양 DB와 Function Calling 기반 맞춤형 식단 분석 및 정기 결산 시스템"
p_sub.font.size = Pt(16)
p_sub.font.color.rgb = RGBColor(203, 213, 225)
p_sub.space_after = Pt(35)

p_info = tf1.add_paragraph()
p_info.text = "발표자 : 메타코드M 라이브 스터디  |  기술 스택 : Gemini 3.6 Flash · Streamlit · SQLite · Plotly · Telegram"
p_info.font.size = Pt(12)
p_info.font.color.rgb = RGBColor(148, 163, 184)

# ==========================================
# Slide 2: 기획 배경 및 문제 정의
# ==========================================
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2, COLOR_BG)
add_header(s2, "Problem & Solution", "기획 배경 및 해결하고자 한 문제", "기존 다이어트 앱과 일반 생성형 AI의 한계를 극복하는 신뢰성 높은 웰니스 에이전트")

add_card(s2, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "⚠️ 기존 다이어트 앱 & LLM의 한계", [
    "기록의 번거로움: 사용자가 음식마다 그램(g) 수를 일일이 검색하고 수동 입력해야 하는 높은 피로도",
    "LLM의 치명적 환각 (Hallucination): 일반 챗봇에게 칼로리를 물으면 임의로 수치를 지어내어 영양 왜곡 발생",
    "개인화 결여: 사용자 체형/목표에 맞지 않는 획일적인 칼로리 가이드",
    "지속성 부족: 앱에 직접 들어오지 않으면 식단 피드백과 월간 달성도를 확인하기 어려움"
])

add_card(s2, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "✨ AI 코치의 해결 솔루션", [
    "📸 멀티모달 사진 식단 분석: 음식 사진 1장으로 메뉴를 자동 인식하여 사용자 편의성 극대화",
    "🔍 식약처 표준 DB Function Calling: 파이썬 검색 도구를 강제 연동하여 100% 신뢰할 수 있는 수치 반환",
    "📏 BMR 기반 맞춤 목표 자동 산출: 미플린-세인트지올 공식으로 신체 맞춤 칼로리/단백질 추천",
    "📱 텔레그램 월간 자동 결산: 매월 1일 전월 통계 요약 및 칼로리 추이 그래프를 메신저로 자동 전송"
])

# ==========================================
# Slide 3: 시스템 아키텍처
# ==========================================
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3, COLOR_BG)
add_header(s3, "System Architecture", "전체 시스템 아키텍처 및 기술 스택", "클라이언트 인터페이스부터 AI 에이전트, 로컬 DB, 외부 알림 채널까지 유기적인 풀스택 구조")

add_card(s3, Inches(0.8), Inches(1.8), Inches(3.7), Inches(4.8), "🖥️ Frontend (UI/UX)", [
    "Streamlit Web Framework: 반응형 웹 인터페이스",
    "Plotly: 인터랙티브 게이지, 도넛, 꺾은선 대시보드",
    "멀티모달 업로더: 파일 업로드 및 카메라 실시간 촬영",
    "세션 & 권한 관리: 사용자별 독립 세션 유지"
])

add_card(s3, Inches(4.8), Inches(1.8), Inches(3.7), Inches(4.8), "🤖 AI Agent & Tools", [
    "Google Gemini 3.6 Flash: 초고속 멀티모달 추론",
    "Function Calling: search_food_nutrition 도구 바인딩",
    "식약처 영양 DB: 5,000+ 식품 표준 영양 데이터셋",
    "3단계 코칭 프롬프트: 요약 → 진단 → 메뉴 추천"
])

add_card(s3, Inches(8.8), Inches(1.8), Inches(3.7), Inches(4.8), "💾 Database & Services", [
    "SQLite (diet_app.db): users / meal_records 관리",
    "보안 암호화: SHA-256 + Salt 비밀번호 해싱",
    "Telegram Bot API: 월간 결산 메시지 및 차트 전송",
    "정기 스케줄러: scheduler.py 매월 1일 브로드캐스트"
])

# ==========================================
# Slide 4: 핵심 기술 ① - AI Agent & Function Calling
# ==========================================
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4, COLOR_BG)
add_header(s4, "Core Technology 1", "멀티모달 AI 코치 & Function Calling", "임의의 추측을 배제하고 정확한 공공데이터 영양 수치만을 기반으로 코칭 수행")

add_card(s4, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "💡 Function Calling (도구 바인딩) 작동 원리", [
    "1. 사용자 입력: 사진(닭가슴살 샐러드) 또는 텍스트 입력",
    "2. LLM 의도 판단: 식단 분석을 위해 영양 데이터 조회가 필요함을 인식",
    "3. 도구 실행: Python의 `search_food_nutrition(음식명)` 함수를 자동 호출",
    "4. DB 조회: 식약처 CSV에서 칼로리, 탄단지, 당류, 나트륨 수치 추출",
    "5. 최종 코칭 생성: 조회된 실제 데이터를 기반으로 목표 대비 진단 및 피드백 제공"
])

add_card(s4, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "📋 3단계 전문 코칭 프롬프트 체계", [
    "Step 1. 영양소 요약: 섭취한 음식의 총 칼로리 및 탄·단·지, 나트륨 상세 표기",
    "Step 2. 목표 대비 진단: 일일 목표치(예: 2,000kcal) 대비 현재 식단의 과부족 상태 평가",
    "Step 3. 솔루션 제안: 다음 식사(저녁/간식)에서 보충할 추천 대체 메뉴 및 행동 팁 안내",
    "환각율 0%: 모든 영양 수치를 DB 조회값으로 고정하여 신뢰성 보장"
])

# ==========================================
# Slide 5: 핵심 기술 ② - 신체 맞춤 영양 추천 & 개인 DB
# ==========================================
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5, COLOR_BG)
add_header(s5, "Core Technology 2", "신체 정보 기반 맞춤 영양 자동 추천 & 개인 DB", "미플린-세인트지올(Mifflin-St Jeor) 과학적 공식을 통한 개인화 설정")

add_card(s5, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "📏 AI 영양 추천 알고리즘", [
    "기초대사량 (BMR) 정밀 계산:\n   - 남성: (10×체중) + (6.25×키) - (5×나이) + 5\n   - 여성: (10×체중) + (6.25×키) - (5×나이) - 161",
    "활동대사량 (TDEE) 반영: 운동 빈도별 1.2 ~ 1.725 계수 적용",
    "목표별 칼로리/단백질 최적화:\n   - 감량(다이어트): TDEE - 450kcal / 체중 1kg당 1.6g 단백질\n   - 벌크업: TDEE + 300kcal / 체중 1kg당 1.8g 단백질",
    "신체 스펙 수정 시 원클릭 재계산 지원 ([내 설정] 탭)"
])

add_card(s5, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "🗄️ SQLite 데이터베이스 아키텍처", [
    "users 테이블: ID, 비밀번호 해시, 솔트, 성별, 나이, 키, 몸무게, 목표 칼로리, 목표 단백질, 텔레그램 Chat ID",
    "meal_records 테이블: 일자별 식사 구분(아침/점심/저녁/간식), 음식명, 칼로리, 탄단지, 당류, 나트륨, 코칭 메모",
    "보안 암호화: SHA-256 + Salt 단방향 해싱으로 계정 안전 보장",
    "식단 CRUD: 사이드바에서 간편 추가 및 언제든 오기입 삭제 가능"
])

# ==========================================
# Slide 6: 핵심 기술 ③ - 반응형 인터랙티브 대시보드
# ==========================================
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6, COLOR_BG)
add_header(s6, "Core Technology 3", "반응형 인터랙티브 통계 대시보드", "Plotly 기반의 직관적 시각화로 일/주/월/년 식단 섭취 패턴 분석")

add_card(s6, Inches(0.8), Inches(1.8), Inches(5.6), Inches(2.3), "📅 일별 (Daily) 대시보드", [
    "목표 달성 게이지 차트: 당일 섭취 칼로리 vs 목표 칼로리 달성도",
    "3대 영양소 도넛 차트: 탄수화물, 단백질, 지방 섭취 비율 한눈에 확인",
    "당일 식단 타임라인: 시간대별 식사 상세 내역 및 삭제 관리"
])

add_card(s6, Inches(6.8), Inches(1.8), Inches(5.6), Inches(2.3), "📈 주간 (Weekly) 트렌드", [
    "일별 칼로리 vs 목표 기준선 복합 막대/선 차트 (최근 7일)",
    "단백질 섭취량 추이 차트 및 주간 평균 달성 지표",
    "주간 기록 충실도 (기록 일수 / 7일) 제공"
])

add_card(s6, Inches(0.8), Inches(4.3), Inches(5.6), Inches(2.3), "🗓️ 월별 (Monthly) 결산", [
    "월간 일별 칼로리 변화 추이 선 그래프 및 목표선 표기",
    "월간 목표 달성 성공률 (%) 및 총 섭취 칼로리 KPI",
    "🏆 이번 달 가장 많이 섭취한 음식 TOP 5 가로 막대 차트"
])

add_card(s6, Inches(6.8), Inches(4.3), Inches(5.6), Inches(2.3), "📊 연간 (Yearly) 장기 분석", [
    "연간 1~12월 월평균 칼로리 및 단백질 섭취 변화 다중 축 차트",
    "계절별/월별 식습관 변화 패턴 및 장기적 다이어트 성과 추적"
])

# ==========================================
# Slide 7: 핵심 기술 ④ - 텔레그램 월간 결산 자동화
# ==========================================
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7, COLOR_BG)
add_header(s7, "Core Technology 4", "텔레그램 연동 및 월간 결산 자동화", "앱을 실행하지 않아도 매월 1일 정기 리포트를 개인 메신저로 자동 전달")

add_card(s7, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "📱 텔레그램 연동 및 리포트 구성", [
    "간편한 Chat ID 연동: 텔레그램 봇으로 고유 ID 확인 후 등록",
    "종합 결산 텍스트 요약:\n   • 총 기록 일수 및 총 식사 횟수\n   • 월간 총 칼로리 및 일평균 섭취량\n   • 목표 달성 성공률 (%) 및 성공 일수\n   • 이번 달 최다 섭취 음식 TOP 3",
    "AI 코칭 총평: 달성률에 따른 맞춤형 격려 및 개선 조언",
    "칼로리 추이 그래프 이미지 자동 생성 (Matplotlib) 및 첨부"
])

add_card(s7, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "⏰ 자동 발송 파이프라인 (scheduler.py)", [
    "백그라운드 스케줄러: 매월 1일 정기 트리거",
    "일괄 브로드캐스트: 텔레그램 ID를 연동한 모든 사용자 DB 조회",
    "개인화 리포트 생성: 사용자별 전월 데이터 독립 집계 및 그래프 렌더링",
    "즉시 테스트 발송 지원: 웹 화면에서 원클릭으로 이번 달 리포트 즉시 수신 가능"
])

# ==========================================
# Slide 8: 강의 커리큘럼 연계 및 기술적 의의
# ==========================================
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8, COLOR_BG)
add_header(s8, "Course Mapping", "강의 커리큘럼(1~6차시) 연계 및 의의", "강의에서 다룬 핵심 AI 이론을 실무 풀스택 프로젝트로 구현")

add_card(s8, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "📚 차시별 핵심 이론 접목", [
    "1차시 (프롬프트 엔지니어링): 페르소나 부여 및 구조화된 System Instruction",
    "2~4차시 (데이터 전처리 & 검색): 식약처 CSV 정제 및 키워드 기반 영양 매칭 로직",
    "5차시 (Tool Calling & ReAct): LLM 도구 바인딩 및 함수 자동 호출 에이전트",
    "6차시 (상태 관리 & 멀티모달): 세션 히스토리 메모리 및 사진+텍스트 동시 처리"
])

add_card(s8, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "🏆 프로젝트의 기술적 의의", [
    "단순 튜토리얼을 넘은 풀스택 완성: LLM 단독 실행이 아닌 DB, UI, 외부 메신저까지 결합",
    "할루시네이션 완벽 통제: 공공데이터 검색 도구를 강제하여 의료/영양 도메인 신뢰성 확보",
    "실제 사용 가능한 완성도: 비밀번호 암호화, 개인 DB 격리, 동적 모듈 리로드, 글로벌 클라우드 배포 완료"
])

# ==========================================
# Slide 9: 시연 요약 및 향후 발전 방향
# ==========================================
s9 = prs.slides.add_slide(blank_layout)
set_slide_background(s9, COLOR_BG)
add_header(s9, "Summary & Future Work", "서비스 시연 요약 및 향후 발전 방향", "실제 배포 완료 및 향후 스마트 헬스케어로의 확장 가능성")

add_card(s9, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "🚀 서비스 구현 및 배포 성과", [
    "GitHub 저장소: rye6837-web/impossible_to_get_lost_my_weight",
    "Streamlit Community Cloud 배포 완료: 전 세계 어디서나 모바일/PC 접속 가능",
    "핵심 가치: 번거로운 식단 입력을 사진 1장으로 단축하고, 정밀한 영양 통계와 월간 리포트 자동 제공"
])

add_card(s9, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "🔮 향후 확장 계획", [
    "스마트워치 / 헬스 데이터 연동: 애플워치·갤럭시워치 걸음 수 및 활동 소모 칼로리 실시간 동기화",
    "AI 맞춤 식단 플래너 & 장바구니: 부족한 영양소를 채워주는 일주일 식단표 생성 및 밀키트 구매 연계",
    "연속 혈당 측정기(CGM) 데이터 접목: 혈당 스파이크 방지 식사 순서 코칭 기능 추가"
])

# 저장
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AI_Diet_Coach_Presentation.pptx")
prs.save(output_path)
print(f"✅ PPT 파일 생성 성공: {output_path}")
