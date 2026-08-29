import os
import pandas as pd

# 1. 파일 경로 탐색
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))

candidate_paths = [
    os.path.join(PROJECT_DIR, 'merge', 'merged_food_nutrition.csv'),
    os.path.join(PROJECT_DIR, 'data', 'merged_food_nutrition.csv'),
    os.path.join(PROJECT_DIR, 'merged_food_nutrition.csv'),
    os.path.join(BASE_DIR, 'merged_food_nutrition.csv')
]

CSV_PATH = None
for path in candidate_paths:
    if os.path.exists(path):
        CSV_PATH = path
        break

if CSV_PATH is None:
    raise FileNotFoundError("merged_food_nutrition.csv 파일을 찾을 수 없습니다.")

print(f"영양 데이터베이스 로딩 중... ({CSV_PATH})")
df_nutrition = pd.read_csv(CSV_PATH)
print("✅ 영양 데이터베이스 로딩 완료!")

# 2. 영양 검색 함수 (regex=False 추가된 완성본)
def search_food_nutrition(food_name: str) -> dict:
    """
    음식 이름을 입력받아 영양성분(칼로리, 탄수화물, 단백질, 지방, 당류, 나트륨 등)을 검색하여 반환합니다.
    """
    if not food_name or df_nutrition.empty:
        return {"error": "데이터를 찾을 수 없습니다."}

    # regex=False를 넣어 정규식 경고(UserWarning)를 방지합니다.
    matches = df_nutrition[df_nutrition['식품명'].str.contains(food_name, case=False, na=False, regex=False)]
    
    if matches.empty:
        # 띄어쓰기 기준 첫 단어로 재검색
        keyword = food_name.split()[0]
        matches = df_nutrition[df_nutrition['식품명'].str.contains(keyword, case=False, na=False, regex=False)]

    if matches.empty:
        return {"result": f"'{food_name}'에 대한 영양 정보를 찾지 못했습니다."}

    # 가장 연관성 높은 1개 항목 추출
    top_match = matches.iloc[0]
    return {
        "식품명": str(top_match['식품명']),
        "기준량": str(top_match.get('영양성분함량기준량', '100g')),
        "칼로리(kcal)": float(top_match['에너지(kcal)']),
        "단백질(g)": float(top_match['단백질(g)']),
        "지방(g)": float(top_match['지방(g)']),
        "탄수화물(g)": float(top_match['탄수화물(g)']),
        "당류(g)": float(top_match.get('당류(g)', 0)),
        "나트륨(mg)": float(top_match.get('나트륨(mg)', 0))
    }

if __name__ == "__main__":
    print("\n[검색 테스트 결과]")
    print(search_food_nutrition("제육볶음"))
    print(search_food_nutrition("닭가슴살"))
