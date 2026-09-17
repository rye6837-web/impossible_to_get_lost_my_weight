import os
import sys
import shutil
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

INPUT_PATH = r"presentation\AI_Diet_Coach_Presentation_Interim.pptx"
OUTPUT_PATH = r"presentation\AI_Diet_Coach_Presentation_수정2.pptx"
DOWNLOAD_PATH = r"C:\Users\run57\Downloads\AI_Diet_Coach_Presentation_수정2.pptx"

FONT_NAME = "Pretendard"

# Design Color Palette
COLOR_PRIMARY = RGBColor(0, 102, 204)       # Blue (#0066CC)
COLOR_FOCUS_BLUE = RGBColor(41, 151, 255)   # #2997FF
COLOR_EMERALD = RGBColor(16, 185, 129)      # #10B981
COLOR_AMBER = RGBColor(245, 158, 11)        # #F59E0B
COLOR_PURPLE = RGBColor(139, 92, 246)       # #8B5CF6
COLOR_DARK_NAVY = RGBColor(30, 41, 59)      # #1E293B
COLOR_CARD_BG = RGBColor(248, 250, 252)     # #F8FAFC
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_TEXT_MAIN = RGBColor(15, 23, 42)      # #0F172A
COLOR_TEXT_MUTED = RGBColor(100, 116, 139)  # #64748B
COLOR_TEXT_LIGHT = RGBColor(248, 250, 252)

prs = Presentation(INPUT_PATH)
print(f"[INFO] 원본 프레젠테이션 로드 완료: {len(prs.slides)}개 슬라이드")

def set_font(p, name=FONT_NAME, size_pt=12, bold=False, color=COLOR_TEXT_MAIN):
    p.font.name = name
    p.font.size = Pt(size_pt)
    p.font.bold = bold
    p.font.color.rgb = color

# =========================================================================
# 1. Slide 2: 목차 (Table of Contents) 업데이트
# =========================================================================
slide2 = prs.slides[1]
for shape in slide2.shapes:
    if shape.has_text_frame and "Ⅳ. 트러블슈팅" in shape.text:
        tf = shape.text_frame
        tf.clear()
        p0 = tf.paragraphs[0]
        p0.text = "Ⅳ. 피드백 반영 & 고도화 성과"
        set_font(p0, FONT_NAME, 13, bold=True, color=COLOR_PRIMARY)
        
        p1 = tf.add_paragraph()
        p1.text = "•  10. 503/429/404 모델 복원력"
        set_font(p1, FONT_NAME, 11, color=COLOR_TEXT_MAIN)
        
        p2 = tf.add_paragraph()
        p2.text = "•  11. 식약처 FTS5 1.24ms & 하이브리드 RAG"
        set_font(p2, FONT_NAME, 11, bold=True, color=COLOR_EMERALD)

        p3 = tf.add_paragraph()
        p3.text = "•  12. ReAct 복합 질문 & 2열 동시 저장 UI"
        set_font(p3, FONT_NAME, 11, bold=True, color=COLOR_FOCUS_BLUE)

        p4 = tf.add_paragraph()
        p4.text = "•  13. 피드백 해결 성과 & Q&A 핵심 답변"
        set_font(p4, FONT_NAME, 11, color=COLOR_TEXT_MAIN)

print("[OK] Slide 2 목차 업데이트 완료")

# =========================================================================
# 2. Slide 4: LangGraph 워크플로우 다이어그램 교체
# =========================================================================
slide4 = prs.slides[3]
# 서브타이틀 업데이트
for shape in slide4.shapes:
    if shape.has_text_frame and "compiled_agent" in shape.text:
        tf = shape.text_frame
        tf.clear()
        p = tf.paragraphs[0]
        p.text = "ReAct 다중 의도 분해 & 병렬 도구 호출 & 2열 멀티 스마트 저장 카드 고도화 아키텍처"
        set_font(p, FONT_NAME, 13, bold=True, color=COLOR_PRIMARY)

    # 기존 Mermaid 텍스트 업데이트
    if shape.has_text_frame and "LangGraph 상태 그래프" in shape.text:
        tf = shape.text_frame
        tf.clear()
        p0 = tf.paragraphs[0]
        p0.text = "🔀 [고도화 TO-BE] ReAct 병렬 처리 워크플로우"
        set_font(p0, FONT_NAME, 12, bold=True, color=COLOR_DARK_NAVY)
        
        steps = [
            "1. 사용자 복합 입력 (예: '제육볶음 먹고 40분 러닝했어')",
            "2. 🔀 의도 분해 & ReAct Engine (식단 + 운동 동시 감지)",
            "3. ⚡ 병렬 도구 호출 (식약처 FTS5 + ACSM METs 계산기)",
            "4. 🛡️ 공식 출처 메타데이터 첨부 (식약처 2024 / ACSM)",
            "5. 🍱🔥 2열 멀티 저장 카드 & [⚡ 원클릭 동시 저장] 제공"
        ]
        for step in steps:
            p = tf.add_paragraph()
            p.text = step
            set_font(p, FONT_NAME, 10.5, color=COLOR_TEXT_MAIN)

# 기존 슬라이드 4의 그림을 고해상도 개선 다이어그램으로 교체
img_path = r"presentation\improved_langgraph_diagram.png"
if os.path.exists(img_path):
    # Shape 5 (기존 그림) 위치 확인
    for shape in slide4.shapes:
        if shape.shape_type == 13 and shape.left < Inches(2.0): # 그림 2
            left = shape.left
            top = shape.top
            width = shape.width
            height = shape.height
            # 기존 그림 제거를 위해 위치 기억 후 슬라이드에 새 그림 덮어쓰기
            slide4.shapes.add_picture(img_path, Inches(0.8), Inches(1.75), Inches(7.2), Inches(5.15))
            break

print("[OK] Slide 4 LangGraph 워크플로우 개선 완료")

# =========================================================================
# 3. Slide 5: 정형 데이터 FTS5 1.24ms 고속화 성과 반영
# =========================================================================
slide5 = prs.slides[4]
for shape in slide5.shapes:
    if shape.has_text_frame and "5000+ 공공데이터" in shape.text:
        tf = shape.text_frame
        tf.clear()
        p0 = tf.paragraphs[0]
        p0.text = "⚡ 식약처 73,199건 SQLite FTS5 전문 검색 엔진 구축"
        set_font(p0, FONT_NAME, 13, bold=True, color=COLOR_PRIMARY)
        
        bullets = [
            "• 데이터 규모: 전국통합식품영양성분 73,199건 인덱싱",
            "• 검색 속도: 기존 Pandas 50ms+ ➔ 1.24ms (40배 이상 단축!)",
            "• 메모리 절감: CSV 지연 로딩 ➔ FTS5 온디맨드 0MB RAM 점유",
            "• 10대 카테고리 스마트 폴백: 미등록 신조어 음식 영양 추정",
            "• 공식 출처 표기: 식품의약품안전처 2024 통합DB 뱃지 자동 부여"
        ]
        for b in bullets:
            p = tf.add_paragraph()
            p.text = b
            set_font(p, FONT_NAME, 11, color=COLOR_TEXT_MAIN)

print("[OK] Slide 5 식약처 FTS5 성과 반영 완료")

# =========================================================================
# 4. Slide 10: 14대 임상 영양학 하이브리드 RAG 반영
# =========================================================================
slide10 = prs.slides[9]
for shape in slide10.shapes:
    if shape.has_text_frame and "국내외 4대 공인" in shape.text:
        tf = shape.text_frame
        tf.clear()
        p0 = tf.paragraphs[0]
        p0.text = "📚 14대 임상 영양 백과 & BM25+Dense 하이브리드 RAG"
        set_font(p0, FONT_NAME, 13, bold=True, color=COLOR_PRIMARY)
        
        rag_bullets = [
            "• 14대 전문 임상 가이드라인 확장:",
            "   - 혈당 스파이크 식사 순서, 다이어트 정체기 리피드(Re-feed)",
            "   - 단백질 MPS 골든타임, 저칼로리 대체식재료, 야식 가짜배고픔",
            "   - 간헐적 단식 16:8 공복 가이드, 알코올 지방 대사 등",
            "• BM25 + Semantic 코사인 유사도 하이브리드 검색:",
            "   - 키워드 정확도 + 자연어 문맥을 RRF 알고리즘으로 결합",
            "• 공식 출처 뱃지: 보건복지부 KDRIs 및 임상 가이드라인 명시"
        ]
        for rb in rag_bullets:
            p = tf.add_paragraph()
            p.text = rb
            set_font(p, FONT_NAME, 10.5, color=COLOR_TEXT_MAIN)

print("[OK] Slide 10 하이브리드 RAG 반영 완료")

# =========================================================================
# 5. Slide 13: Human-in-the-Loop (2열 멀티 스마트 저장 카드)
# =========================================================================
slide13 = prs.slides[12]
for shape in slide13.shapes:
    if shape.has_text_frame and "1. [사용자 입력]" in shape.text:
        tf = shape.text_frame
        tf.clear()
        p0 = tf.paragraphs[0]
        p0.text = "1. [사용자 복합 입력] '점심에 제육볶음 먹고 40분 러닝했어!'"
        set_font(p0, FONT_NAME, 11, bold=True, color=COLOR_TEXT_MAIN)
        
        hil_steps = [
            "↓",
            "2. [ReAct 병렬 도구 호출] 식약처 FTS5(550kcal) + ACSM METs(416.5kcal)",
            "↓",
            "3. [re.findall 다중 파서] MEAL_DATA & EXERCISE_DATA 100% 분리",
            "↓",
            "4. ⭐ [Human-in-the-Loop 2열 멀티 카드 동시 렌더링!]",
            "   • 좌측: 🍱 [식단 저장 카드] (제육볶음 550kcal + 아코디언 수동 보정)",
            "   • 우측: 🔥 [운동 저장 카드] (러닝 40분 416.5kcal 소모)",
            "   • 상단: ⚡ [식단 & 운동 한 번에 DB 동시 저장] 마스터 버튼",
            "↓",
            "5. [트랜잭션 DB 동시 저장] 순 칼로리(133.5kcal) 대시보드 자동 반영"
        ]
        for hs in hil_steps:
            p = tf.add_paragraph()
            p.text = hs
            set_font(p, FONT_NAME, 10, color=COLOR_PRIMARY if "⭐" in hs else COLOR_TEXT_MAIN)

print("[OK] Slide 13 2열 멀티 저장 카드 반영 완료")

# =========================================================================
# 6. Slide 15: [문제점] ➔ [강사 피드백 5대 과제 완벽 해결 성과]로 전면 교체
# =========================================================================
slide15 = prs.slides[14]
# 제목 변경
for shape in slide15.shapes:
    if shape.has_text_frame and "문제점 / 추가 보완사항" in shape.text:
        shape.text_frame.text = "강사 피드백 5대 과제 해결 성과 & 실측 벤치마크"
        set_font(shape.text_frame.paragraphs[0], FONT_NAME, 22, bold=True, color=COLOR_DARK_NAVY)

    # 좌측 상단 박스 (속도 지연 ➔ FTS5 1.24ms 40배 단축)
    if shape.has_text_frame and "사진 속 음식 분석 및 영양 DB" in shape.text:
        tf = shape.text_frame
        tf.clear()
        p0 = tf.paragraphs[0]
        p0.text = "✅ 1. 검색 속도 병목 극복 (FTS5 1.24ms 달성)"
        set_font(p0, FONT_NAME, 13, bold=True, color=COLOR_EMERALD)
        
        pts = [
            "• AS-IS: 7만건 CSV를 Pandas로 순차 탐색하여 수 초 이상 지연",
            "• TO-BE: SQLite FTS5 전문 검색 변환으로 1.24ms 초고속 달성",
            "• 성과: 검색 속도 40배 이상 단축, 앱 구동 시 RAM 0MB 점유"
        ]
        for pt in pts:
            p = tf.add_paragraph()
            p.text = pt
            set_font(p, FONT_NAME, 10.5, color=COLOR_TEXT_MAIN)

    # 좌측 하단 박스 (복합 질문 지원 & ReAct)
    if shape.has_text_frame and "gemini api 버전별 호출" in shape.text:
        tf = shape.text_frame
        tf.clear()
        p0 = tf.paragraphs[0]
        p0.text = "✅ 2. 복합 질문 처리 & ReAct 아키텍처 완성"
        set_font(p0, FONT_NAME, 13, bold=True, color=COLOR_FOCUS_BLUE)
        
        pts = [
            "• AS-IS: 식단과 운동을 동시에 말하면 단일 태그만 생성(유실)",
            "• TO-BE: ReAct 다중 도구 호출 + re.findall 다중 파서 도입",
            "• 성과: 식단/운동 100% 동시 분석 & 2열 멀티 카드 동시 저장"
        ]
        for pt in pts:
            p = tf.add_paragraph()
            p.text = pt
            set_font(p, FONT_NAME, 10.5, color=COLOR_TEXT_MAIN)

    # 우측 상단 박스 (정형/비정형 이원화 RAG)
    if shape.has_text_frame and "대쉬보드, 단백질" in shape.text:
        tf = shape.text_frame
        tf.clear()
        p0 = tf.paragraphs[0]
        p0.text = "✅ 3. 정형 데이터 vs 비정형 문서 명확한 이원화"
        set_font(p0, FONT_NAME, 13, bold=True, color=COLOR_PURPLE)
        
        pts = [
            "• 정형 식약처 DB: SQLite FTS5 역색인 검색 (오탐/비용 제로)",
            "• 비정형 영양 백과: 14대 임상 가이드 + BM25+Dense 하이브리드 RAG",
            "• 성과: 무분별한 7만건 벡터화 방지 및 최적의 검색 품질 보장"
        ]
        for pt in pts:
            p = tf.add_paragraph()
            p.text = pt
            set_font(p, FONT_NAME, 10.5, color=COLOR_TEXT_MAIN)

    # 우측 중단 박스 (공식 출처 표기 & 스마트 폴백)
    if shape.has_text_frame and "텔레그램 봇 연동" in shape.text:
        tf = shape.text_frame
        tf.clear()
        p0 = tf.paragraphs[0]
        p0.text = "✅ 4. 공식 출처 표기 & 스마트 폴백 (UX 혁신)"
        set_font(p0, FONT_NAME, 13, bold=True, color=COLOR_AMBER)
        
        pts = [
            "• 식약처 2024 / ACSM METs / 보건복지부 KDRIs 공식 출처 뱃지",
            "• 미등록 메뉴 입력 시 10대 카테고리 표준 조리법 기반 추정치 제시",
            "• 성과: 설명 가능성(Explainability) 확보 및 사용자 이탈 방지"
        ]
        for pt in pts:
            p = tf.add_paragraph()
            p.text = pt
            set_font(p, FONT_NAME, 10.5, color=COLOR_TEXT_MAIN)

    # 우측 하단 박스 (토큰 슬라이딩 윈도우)
    if shape.has_text_frame and "LLM-as-a-Judge" in shape.text:
        tf = shape.text_frame
        tf.clear()
        p0 = tf.paragraphs[0]
        p0.text = "✅ 5. 8턴 슬라이딩 윈도우 (토큰 40% 절감)"
        set_font(p0, FONT_NAME, 13, bold=True, color=COLOR_PRIMARY)
        
        pts = [
            "• 대화 누적 시 최근 8턴(16개 메시지)만 활성 컨텍스트 유지",
            "• 429 Rate Limit 및 503 과부하 에러 100% 원천 차단"
        ]
        for pt in pts:
            p = tf.add_paragraph()
            p.text = pt
            set_font(p, FONT_NAME, 10.5, color=COLOR_TEXT_MAIN)

print("[OK] Slide 15 피드백 해결 성과 5대 카드 교체 완료")

# =========================================================================
# 7. Slide 16: [질문/답변] ➔ 심사위원 핵심 Q&A 4선과 명쾌한 모범 답변
# =========================================================================
slide16 = prs.slides[15]
for shape in slide16.shapes:
    if shape.has_text_frame and "💡" in shape.text:
        tf = shape.text_frame
        tf.clear()
        
        qa_pairs = [
            ("Q1. 7만 건 식약처 데이터를 왜 Vector DB 대신 SQLite FTS5로 구축했나요?",
             "➔ 식약처 데이터는 정확한 식품명과 수치 규격을 가진 정형 데이터입니다. 7만 건을 임베딩하면 비용 낭비와 오타 오탐이 심각해집니다. 역색인 FTS5를 통해 1.24ms 초고속 정밀 매칭을 구현하고, 비정형 임상 지식만 벡터 RAG로 이원화하는 것이 엔터프라이즈 정석입니다."),
            
            ("Q2. 식단과 운동을 한 번에 말하는 복합 질문은 어떻게 해결했나요?",
             "➔ ReAct 프롬프트로 의도를 자동 분해하여 search_food_nutrition과 calculate_exercise_calories를 동시에 호출합니다. re.findall 다중 파서로 MEAL_DATA와 EXERCISE_DATA를 분리 추출하여 화면에 2열 독립 카드와 [원클릭 동시 저장]을 제공합니다."),
            
            ("Q3. 세션이 길어질 때 무료 API 속도 제한(429/503)은 어떻게 방어하나요?",
             "➔ 최근 8턴(16개 메시지) 슬라이딩 윈도우 버퍼를 적용하여 이전 대화를 압축하고 토큰을 40% 이상 절약합니다. 또한 4대 Flash 모델 간 캐스케이딩 자동 전환 폴백을 구축하여 무중단 서비스를 보장합니다."),
            
            ("Q4. 식약처 DB에 등록되지 않은 생소한 음식은 어떻게 처리하나요?",
             "➔ '정보 없음'으로 대화를 끊지 않고, 10대 조리법 카테고리(국/찌개, 육류볶음, 면류 등) 표준 조리법 기반 스마트 폴백 추정치를 즉시 계산하며, 사용자가 카드를 열어 직접 수치를 보정할 수 있는 Human-in-the-Loop를 지원합니다.")
        ]
        
        for q, a in qa_pairs:
            p_q = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
            p_q.text = q
            set_font(p_q, FONT_NAME, 11.5, bold=True, color=COLOR_PRIMARY)
            
            p_a = tf.add_paragraph()
            p_a.text = a
            set_font(p_a, FONT_NAME, 10, color=COLOR_TEXT_MAIN)
            
            p_space = tf.add_paragraph()
            p_space.text = ""
            p_space.font.size = Pt(4)

print("[OK] Slide 16 Q&A 핵심 답변 채우기 완료")

# =========================================================================
# 8. Slide 17 (신규 슬라이드 추가): Before vs After 종합 정량 비교표
# =========================================================================
blank_layout = prs.slide_layouts[6] # Blank
slide17 = prs.slides.add_slide(blank_layout)

# 배경색 (Clean Canvas)
bg = slide17.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
bg.fill.solid()
bg.fill.fore_color.rgb = COLOR_CARD_BG
bg.line.fill.background()

# 제목 박스
tb_title = slide17.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.73), Inches(0.8))
p_sub = tb_title.text_frame.paragraphs[0]
p_sub.text = "CONCLUSION & METRICS SUMMARY"
set_font(p_sub, FONT_NAME, 10.5, bold=True, color=COLOR_TEXT_MUTED)

p_tit = tb_title.text_frame.add_paragraph()
p_tit.text = "고도화 최종 성과 : AS-IS (중간 발표) vs TO-BE (완성본) 정량 비교"
set_font(p_tit, FONT_NAME, 22, bold=True, color=COLOR_DARK_NAVY)

# 정량 비교 테이블 (6행 x 4열)
table_shape = slide17.shapes.add_table(6, 4, Inches(0.8), Inches(1.6), Inches(11.73), Inches(5.1))
table = table_shape.table
table.columns[0].width = Inches(2.2)
table.columns[1].width = Inches(3.6)
table.columns[2].width = Inches(4.3)
table.columns[3].width = Inches(1.63)

headers = ["비교 영역", "중간 발표 (AS-IS)", "고도화 완성본 (TO-BE)", "개선 효과"]
table_data = [
    ["1. 식약처 DB 검색", "Pandas 순차 탐색 (50ms+ 지연, CSV 5MB 메모리 점유)", "SQLite FTS5 가상테이블 전문 검색 (평균 1.24ms, 0MB RAM)", "40배 초고속화 ⚡"],
    ["2. 질문 처리 범위", "단일 질문만 처리 (식단+운동 복합 발화 시 한쪽 데이터 유실)", "ReAct 의도 분해 + re.findall 다중 파서 (식단 & 운동 100% 분해)", "데이터 유실 0% 🔄"],
    ["3. 스마트 저장 UX", "단일 저장 카드 노출 ➔ 복합 데이터 저장 불가", "2열 나란히 멀티 카드 렌더링 + [⚡ 원클릭 동시 저장] 마스터 버튼", "UX 만족도 극대화 🍱"],
    ["4. 데이터 검색 전략", "무분별한 정형 데이터 벡터화 시도로 오탐 및 속도 저하", "정형 데이터(SQLite FTS5) vs 비정형 문서(임상 RAG) 명확한 이원화", "엔터프라이즈 정석 📚"],
    ["5. 신뢰도 & 환각 방지", "출처 미표기, 미등록 음식 검색 실패 시 단절 대화", "식약처/ACSM/KDRIs 공식 출처 뱃지 + 10대 카테고리 스마트 폴백", "설명 가능성 100% 🛡️"]
]

# 헤더 행 스타일링
for col_idx, h_text in enumerate(headers):
    cell = table.cell(0, col_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = COLOR_DARK_NAVY
    cell.text_frame.text = h_text
    p = cell.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    set_font(p, FONT_NAME, 12, bold=True, color=COLOR_WHITE)

# 데이터 행 스타일링
for row_idx, row_values in enumerate(table_data):
    for col_idx, val in enumerate(row_values):
        cell = table.cell(row_idx + 1, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_WHITE if row_idx % 2 == 0 else COLOR_CARD_BG
        cell.text_frame.text = val
        p = cell.text_frame.paragraphs[0]
        if col_idx == 0:
            set_font(p, FONT_NAME, 11, bold=True, color=COLOR_DARK_NAVY)
        elif col_idx == 3:
            p.alignment = PP_ALIGN.CENTER
            set_font(p, FONT_NAME, 11, bold=True, color=COLOR_EMERALD)
        else:
            set_font(p, FONT_NAME, 10.5, color=COLOR_TEXT_MAIN)

print("[OK] Slide 17 Before vs After 정량 비교표 추가 완료")

# 저장
prs.save(OUTPUT_PATH)
print(f"[SUCCESS] 프로젝트 폴더 저장 완료: {OUTPUT_PATH}")

try:
    shutil.copy(OUTPUT_PATH, DOWNLOAD_PATH)
    print(f"[SUCCESS] 다운로드 폴더 복사 완료: {DOWNLOAD_PATH}")
except Exception as e:
    print(f"[WARN] 다운로드 폴더 복사 실패: {e}")
