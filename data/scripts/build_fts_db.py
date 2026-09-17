import os
import sys
import sqlite3
import pandas as pd
import time

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..'))
DATA_DIR = os.path.join(PROJECT_DIR, 'data', 'processed')
CSV_PATH = os.path.join(DATA_DIR, 'merged_food_nutrition.csv')
DB_PATH = os.path.join(DATA_DIR, 'food_nutrition.db')

def build_fts_database():
    print(f"=== 식약처 7만 건 FTS5 전문 검색 DB 빌드 시작 ===")
    print(f"CSV 원본: {CSV_PATH}")
    print(f"DB 대상: {DB_PATH}")

    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {CSV_PATH}")

    t0 = time.time()
    print("[1/3] CSV 데이터 로딩 중...")
    df = pd.read_csv(CSV_PATH)
    df.fillna(0, inplace=True)
    row_count = len(df)
    print(f"총 {row_count:,}건 데이터 로드 완료 ({time.time() - t0:.2f}초)")

    # 기존 DB 파일 삭제 후 재생성 (Clean build)
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception:
            pass

    t1 = time.time()
    print("[2/3] SQLite FTS5 가상 테이블 및 인덱스 생성 중...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # SQLite 성능 최적화 PRAGMA 설정
    cursor.execute("PRAGMA synchronous = OFF;")
    cursor.execute("PRAGMA journal_mode = MEMORY;")
    cursor.execute("PRAGMA cache_size = 100000;")

    cursor.execute("""
        CREATE VIRTUAL TABLE foods_fts USING fts5(
            식품명,
            기준량 UNINDEXED,
            칼로리 UNINDEXED,
            단백질 UNINDEXED,
            지방 UNINDEXED,
            탄수화물 UNINDEXED,
            당류 UNINDEXED,
            나트륨 UNINDEXED,
            tokenize = 'unicode61'
        );
    """)

    print("[3/3] FTS5 테이블로 고속 벌크 인서트 중...")
    records = []
    for _, row in df.iterrows():
        records.append((
            str(row['식품명']),
            str(row.get('영양성분함량기준량', '100g')),
            float(row.get('에너지(kcal)', 0)),
            float(row.get('단백질(g)', 0)),
            float(row.get('지방(g)', 0)),
            float(row.get('탄수화물(g)', 0)),
            float(row.get('당류(g)', 0)),
            float(row.get('나트륨(mg)', 0))
        ))

    cursor.executemany("""
        INSERT INTO foods_fts (식품명, 기준량, 칼로리, 단백질, 지방, 탄수화물, 당류, 나트륨)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, records)

    conn.commit()
    conn.close()

    total_time = time.time() - t0
    db_size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
    print(f"\n✅ FTS5 DB 빌드 성공!")
    print(f"   - 총 인덱싱 레코드: {row_count:,}건")
    print(f"   - 생성된 DB 크기: {db_size_mb:.2f} MB")
    print(f"   - 총 소요 시간: {total_time:.2f}초")
    print(f"   - 저장 위치: {DB_PATH}")

if __name__ == "__main__":
    build_fts_database()
