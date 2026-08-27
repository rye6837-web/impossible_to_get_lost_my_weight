import os
import pandas as pd

# 1. 경로 설정 (파이썬 파일 위치 기준으로 data 폴더와 저장 경로 지정)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ../data 폴더 지정
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'data'))

# 2. 추출할 핵심 컬럼 목록 (영양 진단 핵심 지표)
columns = [
    '식품명', '영양성분함량기준량', '에너지(kcal)', 
    '단백질(g)', '지방(g)', '탄수화물(g)', '당류(g)', '나트륨(mg)'
]

# 3. 읽어올 CSV 파일 목록
file_names = [
    '전국통합식품영양성분정보_원재료성식품_표준데이터.csv',
    '전국통합식품영양성분정보_가공식품_표준데이터.csv',
    '전국통합식품영양성분정보_음식_표준데이터.csv'
]

df_list = []
for file_name in file_names:
    file_path = os.path.join(DATA_DIR, file_name)
    try:
        # UTF-8 또는 CP949(EUC-KR) 인코딩 자동 대응
        try:
            df = pd.read_csv(file_path, usecols=lambda c: c in columns, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, usecols=lambda c: c in columns, encoding='cp949')
        
        df_list.append(df)
        print(f"로드 성공: {file_name} ({len(df):,}행)")
    except Exception as e:
        print(f"파일 읽기 오류 ({file_name}): {e}")

# 4. 3개 데이터 통합 및 저장
if df_list:
    combined_df = pd.concat(df_list, ignore_index=True)
    # 결측치(NaN) 0으로 보정
    combined_df.fillna(0, inplace=True)
    
    output_path = os.path.join(BASE_DIR, 'merged_food_nutrition.csv')
    combined_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n✅ 통합 완료: 총 {len(combined_df):,}건의 영양 데이터가 생성되었습니다.")
    print(f"저장 위치: {output_path}")
else:
    print(f"\n❌ data 폴더({DATA_DIR})에서 CSV 파일을 찾을 수 없습니다.")
