import os
import sys
import sqlite3
import pandas as pd
from typing import Optional, Dict, Any

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))

# 1. SQLite FTS5 데이터베이스 및 CSV 폴백 경로 탐색
DB_PATH = os.path.join(PROJECT_DIR, 'data', 'processed', 'food_nutrition.db')

candidate_csv_paths = [
    os.path.join(PROJECT_DIR, 'data', 'processed', 'merged_food_nutrition.csv'),
    os.path.join(PROJECT_DIR, 'merge', 'merged_food_nutrition.csv'),
    os.path.join(PROJECT_DIR, 'data', 'merged_food_nutrition.csv'),
    os.path.join(PROJECT_DIR, 'merged_food_nutrition.csv'),
    os.path.join(BASE_DIR, 'merged_food_nutrition.csv')
]

CSV_PATH = None
for path in candidate_csv_paths:
    if os.path.exists(path):
        CSV_PATH = path
        break

# FTS5 DB 존재 시 메모리 낭비 없이 0MB 상태로 가동, 없을 때만 CSV 지연 로딩
USE_FTS5 = os.path.exists(DB_PATH)
df_nutrition = None

if USE_FTS5:
    print(f"[INFO] ⚡ SQLite FTS5 전문 검색 엔진 활성화 ({DB_PATH})")
else:
    if CSV_PATH and os.path.exists(CSV_PATH):
        try:
            print(f"[INFO] FTS5 DB 부재로 CSV 백업 로딩 중... ({CSV_PATH})")
            df_nutrition = pd.read_csv(CSV_PATH)
            print("[INFO] CSV 백업 로딩 완료!")
        except Exception as e:
            print(f"[WARN] CSV 로딩 실패: {e}")

# 2. 스마트 폴백(Smart Fallback) 영양성분 프리셋 (10대 카테고리)
FALLBACK_PRESETS = [
    {
        "keywords": ["찌개", "국", "탕", "전골", "해장국", "비지찌개", "순두부", "된장", "김치찌개", "뚝배기"],
        "category": "국·찌개류",
        "nutrition": {"칼로리(kcal)": 350.0, "탄수화물(g)": 20.0, "단백질(g)": 22.0, "지방(g)": 18.0, "당류(g)": 5.0, "나트륨(mg)": 1300.0}
    },
    {
        "keywords": ["볶음", "두루치기", "조림", "제육", "불고기", "갈비", "닭갈비", "오삼"],
        "category": "육류 볶음·조림류",
        "nutrition": {"칼로리(kcal)": 550.0, "탄수화물(g)": 25.0, "단백질(g)": 35.0, "지방(g)": 32.0, "당류(g)": 12.0, "나트륨(mg)": 950.0}
    },
    {
        "keywords": ["구이", "삼겹살", "소고기", "스테이크", "목살", "치킨", "통닭", "오리고기", "생선구이"],
        "category": "육류·생선 구이류",
        "nutrition": {"칼로리(kcal)": 580.0, "탄수화물(g)": 5.0, "단백질(g)": 40.0, "지방(g)": 42.0, "당류(g)": 1.0, "나트륨(mg)": 550.0}
    },
    {
        "keywords": ["밥", "덮밥", "볶음밥", "비빔밥", "리조또", "죽", "초밥", "김밥", "주먹밥"],
        "category": "밥·식사류",
        "nutrition": {"칼로리(kcal)": 550.0, "탄수화물(g)": 88.0, "단백질(g)": 18.0, "지방(g)": 13.0, "당류(g)": 6.0, "나트륨(mg)": 780.0}
    },
    {
        "keywords": ["면", "라면", "파스타", "국수", "우동", "짬뽕", "짜장", "스파게티", "모밀", "소바", "칼국수"],
        "category": "면류",
        "nutrition": {"칼로리(kcal)": 530.0, "탄수화물(g)": 85.0, "단백질(g)": 15.0, "지방(g)": 14.0, "당류(g)": 7.0, "나트륨(mg)": 1550.0}
    },
    {
        "keywords": ["샐러드", "야채", "채소", "포케", "월남쌈", "샤브샤브"],
        "category": "샐러드·건강식류",
        "nutrition": {"칼로리(kcal)": 280.0, "탄수화물(g)": 20.0, "단백질(g)": 18.0, "지방(g)": 14.0, "당류(g)": 6.0, "나트륨(mg)": 380.0}
    },
    {
        "keywords": ["빵", "샌드위치", "베이글", "토스트", "버거", "햄버거", "케이크", "디저트", "와플", "도넛"],
        "category": "베이커리·패스트푸드류",
        "nutrition": {"칼로리(kcal)": 480.0, "탄수화물(g)": 55.0, "단백질(g)": 18.0, "지방(g)": 20.0, "당류(g)": 18.0, "나트륨(mg)": 720.0}
    },
    {
        "keywords": ["튀김", "탕수육", "돈까스", "감자튀김", "너겟", "전", "부침개", "핫도그"],
        "category": "튀김·전류",
        "nutrition": {"칼로리(kcal)": 650.0, "탄수화물(g)": 50.0, "단백질(g)": 24.0, "지방(g)": 38.0, "당류(g)": 8.0, "나트륨(mg)": 880.0}
    },
    {
        "keywords": ["커피", "라떼", "음료", "스무디", "주스", "쉐이크", "에이드", "밀크티"],
        "category": "음료·카페류",
        "nutrition": {"칼로리(kcal)": 180.0, "탄수화물(g)": 30.0, "단백질(g)": 5.0, "지방(g)": 4.0, "당류(g)": 25.0, "나트륨(mg)": 90.0}
    }
]

def get_fallback_nutrition(food_name: str) -> dict:
    """식약처 미등록 음식에 대해 조리법 기반 카테고리 표준 영양소를 추정합니다."""
    food_clean = food_name.strip()
    matched_preset = None
    
    for preset in FALLBACK_PRESETS:
        if any(kw in food_clean for kw in preset["keywords"]):
            matched_preset = preset
            break
            
    if matched_preset is None:
        category = "일반 한식·가정식"
        nutri = {"칼로리(kcal)": 500.0, "탄수화물(g)": 75.0, "단백질(g)": 20.0, "지방(g)": 12.0, "당류(g)": 5.0, "나트륨(mg)": 800.0}
    else:
        category = matched_preset["category"]
        nutri = matched_preset["nutrition"]
        
    return {
        "식품명": f"{food_clean} (조리법 추정)",
        "기준량": "1인분 (표준 조리 기준)",
        "칼로리(kcal)": nutri["칼로리(kcal)"],
        "단백질(g)": nutri["단백질(g)"],
        "지방(g)": nutri["지방(g)"],
        "탄수화물(g)": nutri["탄수화물(g)"],
        "당류(g)": nutri["당류(g)"],
        "나트륨(mg)": nutri["나트륨(mg)"],
        "is_fallback": True,
        "추정카테고리": category,
        "출처": "일반 조리법 기반 AI 표준 영양 추정치 (식약처 미등록)",
        "안내문구": f"'{food_clean}'은(는) 식약처 DB 미등록 메뉴로, 유사한 [{category}] 표준 조리법 기반으로 영양소를 추정했습니다. 실제 양이나 조리법에 따라 오차가 있을 수 있습니다."
    }

def _search_food_fts(food_name: str) -> Optional[dict]:
    """SQLite FTS5 가상 테이블을 조회하여 1ms 내에 가장 관련성 높은 영양 정보를 반환합니다."""
    if not os.path.exists(DB_PATH):
        return None
        
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()
        clean_q = food_name.strip().replace('"', '').replace("'", "")
        
        # 1. 접두사 와일드카드 검색 (예: "신라면"*)
        query_pattern = f'"{clean_q}"*'
        cursor.execute("""
            SELECT 식품명, 기준량, 칼로리, 단백질, 지방, 탄수화물, 당류, 나트륨 
            FROM foods_fts 
            WHERE 식품명 MATCH ? 
            LIMIT 1;
        """, (query_pattern,))
        row = cursor.fetchone()
        
        # 2. 첫 단어로 재검색 (예: "신라면 컵라면" -> "신라면"*)
        if not row and " " in clean_q:
            first_kw = clean_q.split()[0]
            cursor.execute("""
                SELECT 식품명, 기준량, 칼로리, 단백질, 지방, 탄수화물, 당류, 나트륨 
                FROM foods_fts 
                WHERE 식품명 MATCH ? 
                LIMIT 1;
            """, (f'"{first_kw}"*',))
            row = cursor.fetchone()
            
        conn.close()
        
        if row:
            return {
                "식품명": str(row[0]),
                "기준량": str(row[1]),
                "칼로리(kcal)": float(row[2]),
                "단백질(g)": float(row[3]),
                "지방(g)": float(row[4]),
                "탄수화물(g)": float(row[5]),
                "당류(g)": float(row[6]),
                "나트륨(mg)": float(row[7]),
                "is_fallback": False,
                "출처": "식품의약품안전처 2024 통합식품영양성분DB"
            }
    except Exception as e:
        pass
    return None

# 3. 영양 검색 함수 (FTS5 우선 -> CSV 폴백 -> 스마트 폴백 3중 방어선)
def search_food_nutrition(food_name: str) -> dict:
    """
    음식 이름을 입력받아 영양성분(칼로리, 탄수화물, 단백질, 지방, 당류, 나트륨 등)을 검색하여 반환합니다.
    1. SQLite FTS5 1ms 초고속 전문 검색 (최우선)
    2. CSV 판다스 문자열 검색 (DB 부재 시 백업)
    3. 미등록 음식 10대 카테고리 스마트 폴백 (최종 방어선)
    """
    if not food_name:
        return {"error": "음식명을 입력해주세요."}

    # [1단계] FTS5 전문 검색 (속도 1ms 미만)
    fts_res = _search_food_fts(food_name)
    if fts_res is not None:
        return fts_res

    # [2단계] CSV 판다스 검색 (백업)
    global df_nutrition
    if df_nutrition is not None and not df_nutrition.empty:
        matches = df_nutrition[df_nutrition['식품명'].str.contains(food_name, case=False, na=False, regex=False)]
        if matches.empty and " " in food_name:
            keyword = food_name.split()[0]
            matches = df_nutrition[df_nutrition['식품명'].str.contains(keyword, case=False, na=False, regex=False)]
            
        if not matches.empty:
            top_match = matches.iloc[0]
            return {
                "식품명": str(top_match['식품명']),
                "기준량": str(top_match.get('영양성분함량기준량', '100g')),
                "칼로리(kcal)": float(top_match['에너지(kcal)']),
                "단백질(g)": float(top_match['단백질(g)']),
                "지방(g)": float(top_match['지방(g)']),
                "탄수화물(g)": float(top_match['탄수화물(g)']),
                "당류(g)": float(top_match.get('당류(g)', 0)),
                "나트륨(mg)": float(top_match.get('나트륨(mg)', 0)),
                "is_fallback": False,
                "출처": "식품의약품안전처 2024 통합식품영양성분DB"
            }

    # [3단계] 스마트 폴백 추정치 반환
    return get_fallback_nutrition(food_name)

if __name__ == "__main__":
    print("\n[1. FTS5 초고속 등록 식품 검색 테스트]")
    print(search_food_nutrition("제육볶음"))
    print("\n[2. 미등록 식품 스마트 폴백 테스트]")
    print(search_food_nutrition("엄마표 비지찌개"))
