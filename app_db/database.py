import os
import sqlite3
import hashlib
import secrets
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, Tuple, List

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))
DB_PATH = os.path.join(PROJECT_DIR, 'diet_app.db')

def get_connection():
    """SQLite 데이터베이스 연결을 반환합니다."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """데이터베이스 및 테이블을 초기화합니다."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. 사용자 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                gender TEXT DEFAULT '남성',
                age INTEGER DEFAULT 28,
                height REAL DEFAULT 175.0,
                weight REAL DEFAULT 70.0,
                target_cal INTEGER DEFAULT 2000,
                target_protein INTEGER DEFAULT 100,
                telegram_chat_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 기존 테이블에 새 컬럼이 없을 경우 마이그레이션
        cursor.execute("PRAGMA table_info(users)")
        columns = [col["name"] for col in cursor.fetchall()]
        if "gender" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN gender TEXT DEFAULT '남성'")
        if "age" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN age INTEGER DEFAULT 28")
        if "height" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN height REAL DEFAULT 175.0")
        if "weight" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN weight REAL DEFAULT 70.0")

        # 2. 식단 기록 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meal_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                recorded_at TEXT NOT NULL,
                meal_type TEXT DEFAULT '식사',
                food_name TEXT NOT NULL,
                calories REAL DEFAULT 0,
                carbs REAL DEFAULT 0,
                protein REAL DEFAULT 0,
                fat REAL DEFAULT 0,
                sugar REAL DEFAULT 0,
                sodium REAL DEFAULT 0,
                feedback TEXT,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        # 3. 운동 기록 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercise_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                recorded_at TEXT NOT NULL,
                exercise_name TEXT NOT NULL,
                duration_min REAL DEFAULT 30.0,
                calories_burned REAL DEFAULT 0,
                memo TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.commit()

def calculate_recommended_nutrition(
    gender: str = "남성", 
    age: int = 28, 
    height: float = 175.0, 
    weight: float = 70.0, 
    activity: str = "보통 활동 (주 3~5회 운동)", 
    goal: str = "체중 감량 (다이어트)"
) -> Tuple[int, int]:
    """
    미플린-세인트 지올(Mifflin-St Jeor) 공식을 기반으로 
    일일 권장 칼로리(kcal)와 단백질(g)을 추천 계산합니다.
    """
    if gender == "남성":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        
    activity_factors = {
        "활동 적음 (거의 운동 안 함)": 1.2,
        "가벼운 활동 (주 1~3회 운동)": 1.375,
        "보통 활동 (주 3~5회 운동)": 1.55,
        "많은 활동 (주 6~7회 강한 운동)": 1.725
    }
    factor = activity_factors.get(activity, 1.375)
    tdee = bmr * factor
    
    if goal == "체중 감량 (다이어트)":
        rec_cal = tdee - 450
        rec_protein = weight * 1.6
    elif goal == "근육 증가 (벌크업)":
        rec_cal = tdee + 300
        rec_protein = weight * 1.8
    else:
        rec_cal = tdee
        rec_protein = weight * 1.3
        
    rec_cal = max(1200, min(3800, int(round(rec_cal / 50.0) * 50)))
    rec_protein = max(40, min(250, int(round(rec_protein / 5.0) * 5)))
    
    return rec_cal, rec_protein

def _hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """비밀번호를 솔트와 함께 SHA-256으로 해싱합니다."""
    if salt is None:
        salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((password + salt).encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    return password_hash, salt

def register_user(
    username: str, 
    password: str, 
    gender: str = "남성",
    age: int = 28,
    height: float = 175.0,
    weight: float = 70.0,
    target_cal: int = 2000, 
    target_protein: int = 100
) -> Tuple[bool, str]:
    """신규 회원을 등록합니다."""
    if not username.strip() or not password.strip():
        return False, "아이디와 비밀번호를 모두 입력해주세요."
    
    if len(password) < 4:
        return False, "비밀번호는 최소 4자 이상이어야 합니다."
        
    password_hash, salt = _hash_password(password)
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, password_hash, salt, gender, age, height, weight, target_cal, target_protein)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (username.strip(), password_hash, salt, gender, age, height, weight, target_cal, target_protein))
            conn.commit()
            return True, "회원가입이 완료되었습니다. 로그인해주세요!"
    except sqlite3.IntegrityError:
        return False, "이미 존재하는 아이디입니다."
    except Exception as e:
        return False, f"회원가입 중 오류가 발생했습니다: {e}"

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """로그인을 검증하고 사용자 정보를 반환합니다."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username.strip(),))
        user = cursor.fetchone()
        
        if user is None:
            return None
        
        password_hash, _ = _hash_password(password, user["salt"])
        if password_hash == user["password_hash"]:
            return {
                "id": user["id"],
                "username": user["username"],
                "gender": user["gender"] if "gender" in user.keys() else "남성",
                "age": user["age"] if "age" in user.keys() else 28,
                "height": user["height"] if "height" in user.keys() else 175.0,
                "weight": user["weight"] if "weight" in user.keys() else 70.0,
                "target_cal": user["target_cal"],
                "target_protein": user["target_protein"],
                "telegram_chat_id": user["telegram_chat_id"],
                "created_at": user["created_at"]
            }
        return None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """사용자 ID로 최신 사용자 정보를 가져옵니다."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if user:
            return {
                "id": user["id"],
                "username": user["username"],
                "gender": user["gender"] if "gender" in user.keys() else "남성",
                "age": user["age"] if "age" in user.keys() else 28,
                "height": user["height"] if "height" in user.keys() else 175.0,
                "weight": user["weight"] if "weight" in user.keys() else 70.0,
                "target_cal": user["target_cal"],
                "target_protein": user["target_protein"],
                "telegram_chat_id": user["telegram_chat_id"],
                "created_at": user["created_at"]
            }
        return None

def update_user_goals(user_id: int, target_cal: int, target_protein: int) -> bool:
    """사용자의 목표 칼로리와 단백질을 갱신합니다."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET target_cal = ?, target_protein = ?
                WHERE id = ?
            """, (target_cal, target_protein, user_id))
            conn.commit()
            return True
    except Exception:
        return False

def update_user_profile(user_id: int, gender: str, age: int, height: float, weight: float) -> bool:
    """사용자의 신체 정보(성별, 나이, 키, 몸무게)를 갱신합니다."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET gender = ?, age = ?, height = ?, weight = ?
                WHERE id = ?
            """, (gender, age, height, weight, user_id))
            conn.commit()
            return True
    except Exception:
        return False

def update_user_telegram(user_id: int, telegram_chat_id: str) -> bool:
    """사용자의 텔레그램 Chat ID를 갱신합니다."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET telegram_chat_id = ?
                WHERE id = ?
            """, (telegram_chat_id.strip() if telegram_chat_id else None, user_id))
            conn.commit()
            return True
    except Exception:
        return False

# --- [식단 기록 CRUD 함수] ---

def add_meal_record(
    user_id: int,
    food_name: str,
    calories: float,
    carbs: float = 0.0,
    protein: float = 0.0,
    fat: float = 0.0,
    sugar: float = 0.0,
    sodium: float = 0.0,
    meal_type: str = "점심",
    recorded_at: Optional[str] = None,
    feedback: Optional[str] = None,
    image_path: Optional[str] = None
) -> Tuple[bool, str]:
    """식단 기록을 데이터베이스에 추가합니다."""
    if not food_name.strip():
        return False, "음식명을 입력해주세요."
        
    if recorded_at is None:
        recorded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO meal_records (
                    user_id, recorded_at, meal_type, food_name, 
                    calories, carbs, protein, fat, sugar, sodium, 
                    feedback, image_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, recorded_at, meal_type, food_name.strip(),
                calories, carbs, protein, fat, sugar, sodium,
                feedback, image_path
            ))
            conn.commit()
            return True, "식단 기록이 성공적으로 저장되었습니다!"
    except Exception as e:
        return False, f"식단 저장 실패: {e}"

def delete_meal_record(record_id: int, user_id: int) -> bool:
    """특정 식단 기록을 삭제합니다."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM meal_records WHERE id = ? AND user_id = ?", (record_id, user_id))
            conn.commit()
            return True
    except Exception:
        return False

# --- [운동 기록 CRUD 함수] ---

def add_exercise_record(
    user_id: int,
    exercise_name: str,
    duration_min: float,
    calories_burned: float,
    memo: Optional[str] = None,
    recorded_at: Optional[str] = None
) -> Tuple[bool, str]:
    """운동 기록을 데이터베이스에 추가합니다."""
    if not exercise_name.strip():
        return False, "운동명을 입력해주세요."
    if duration_min <= 0:
        return False, "운동 시간을 올바르게 입력해주세요."
        
    if recorded_at is None:
        recorded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO exercise_records (
                    user_id, recorded_at, exercise_name, duration_min, calories_burned, memo
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, recorded_at, exercise_name.strip(), duration_min, calories_burned, memo))
            conn.commit()
            return True, "운동 기록이 성공적으로 저장되었습니다!"
    except Exception as e:
        return False, f"운동 기록 저장 실패: {e}"

def delete_exercise_record(record_id: int, user_id: int) -> bool:
    """특정 운동 기록을 삭제합니다."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM exercise_records WHERE id = ? AND user_id = ?", (record_id, user_id))
            conn.commit()
            return True
    except Exception:
        return False

# --- [통계 집계 함수: 일별, 주간별, 월별, 년별] ---

def get_daily_summary(user_id: int, target_date: Optional[str] = None) -> Dict[str, Any]:
    """특정 날짜(YYYY-MM-DD)의 식단 및 운동 목록과 순 칼로리 합계를 집계합니다."""
    if target_date is None:
        target_date = date.today().strftime("%Y-%m-%d")
        
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. 식단 조회
        cursor.execute("""
            SELECT * FROM meal_records
            WHERE user_id = ? AND substr(recorded_at, 1, 10) = ?
            ORDER BY recorded_at ASC
        """, (user_id, target_date))
        rows = cursor.fetchall()
        records = [dict(row) for row in rows]
        
        # 2. 운동 조회
        cursor.execute("""
            SELECT * FROM exercise_records
            WHERE user_id = ? AND substr(recorded_at, 1, 10) = ?
            ORDER BY recorded_at ASC
        """, (user_id, target_date))
        ex_rows = cursor.fetchall()
        ex_records = [dict(row) for row in ex_rows]
        
        total_cal = sum(r["calories"] for r in records)
        total_carbs = sum(r["carbs"] for r in records)
        total_protein = sum(r["protein"] for r in records)
        total_fat = sum(r["fat"] for r in records)
        total_sugar = sum(r["sugar"] for r in records)
        total_sodium = sum(r["sodium"] for r in records)
        
        total_burned = sum(e["calories_burned"] for e in ex_records)
        total_ex_min = sum(e["duration_min"] for e in ex_records)
        net_cal = total_cal - total_burned
        
        return {
            "date": target_date,
            "records": records,
            "count": len(records),
            "total_cal": round(total_cal, 1),
            "total_carbs": round(total_carbs, 1),
            "total_protein": round(total_protein, 1),
            "total_fat": round(total_fat, 1),
            "total_sugar": round(total_sugar, 1),
            "total_sodium": round(total_sodium, 1),
            "exercise_records": ex_records,
            "exercise_count": len(ex_records),
            "total_burned": round(total_burned, 1),
            "total_ex_min": round(total_ex_min, 1),
            "net_cal": round(net_cal, 1)
        }

def get_weekly_summary(user_id: int, end_date_str: Optional[str] = None) -> Dict[str, Any]:
    """최근 7일간의 일별 칼로리 및 단백질 섭취 추이를 집계합니다."""
    if end_date_str:
        end_d = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    else:
        end_d = date.today()
        
    start_d = end_d - timedelta(days=6)
    start_str = start_d.strftime("%Y-%m-%d")
    end_str = end_d.strftime("%Y-%m-%d")
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                substr(recorded_at, 1, 10) as day,
                SUM(calories) as sum_cal,
                SUM(protein) as sum_protein,
                SUM(carbs) as sum_carbs,
                SUM(fat) as sum_fat,
                COUNT(*) as meal_count
            FROM meal_records
            WHERE user_id = ? AND substr(recorded_at, 1, 10) BETWEEN ? AND ?
            GROUP BY substr(recorded_at, 1, 10)
            ORDER BY day ASC
        """, (user_id, start_str, end_str))
        rows = {row["day"]: dict(row) for row in cursor.fetchall()}
        
    # 7일간 연속 데이터 생성
    daily_data = []
    curr = start_d
    while curr <= end_d:
        d_str = curr.strftime("%Y-%m-%d")
        if d_str in rows:
            daily_data.append({
                "date": d_str,
                "weekday": ["월", "화", "수", "목", "금", "토", "일"][curr.weekday()],
                "calories": round(rows[d_str]["sum_cal"], 1),
                "protein": round(rows[d_str]["sum_protein"], 1),
                "carbs": round(rows[d_str]["sum_carbs"], 1),
                "fat": round(rows[d_str]["sum_fat"], 1),
                "meal_count": rows[d_str]["meal_count"]
            })
        else:
            daily_data.append({
                "date": d_str,
                "weekday": ["월", "화", "수", "목", "금", "토", "일"][curr.weekday()],
                "calories": 0.0,
                "protein": 0.0,
                "carbs": 0.0,
                "fat": 0.0,
                "meal_count": 0
            })
        curr += timedelta(days=1)
        
    active_days = [d for d in daily_data if d["meal_count"] > 0]
    avg_cal = sum(d["calories"] for d in active_days) / len(active_days) if active_days else 0.0
    avg_protein = sum(d["protein"] for d in active_days) / len(active_days) if active_days else 0.0
    
    return {
        "start_date": start_str,
        "end_date": end_str,
        "daily_data": daily_data,
        "avg_calories": round(avg_cal, 1),
        "avg_protein": round(avg_protein, 1),
        "active_days_count": len(active_days)
    }

def get_monthly_summary(user_id: int, year: int, month: int, target_cal: int = 2000) -> Dict[str, Any]:
    """특정 월(Year-Month)의 식단 통계 및 인기 메뉴, 목표 달성률을 집계합니다."""
    month_prefix = f"{year:04d}-{month:02d}"
    
    with get_connection() as conn:
        cursor = conn.cursor()
        # 1. 일별 집계
        cursor.execute("""
            SELECT 
                substr(recorded_at, 1, 10) as day,
                SUM(calories) as sum_cal,
                SUM(protein) as sum_protein,
                COUNT(*) as meal_count
            FROM meal_records
            WHERE user_id = ? AND substr(recorded_at, 1, 7) = ?
            GROUP BY substr(recorded_at, 1, 10)
            ORDER BY day ASC
        """, (user_id, month_prefix))
        day_rows = cursor.fetchall()
        
        # 2. 최다 섭취 식품 TOP 5
        cursor.execute("""
            SELECT food_name, COUNT(*) as count, SUM(calories) as total_cal
            FROM meal_records
            WHERE user_id = ? AND substr(recorded_at, 1, 7) = ?
            GROUP BY food_name
            ORDER BY count DESC, total_cal DESC
            LIMIT 5
        """, (user_id, month_prefix))
        top_foods = [dict(row) for row in cursor.fetchall()]
        
    days_data = [dict(r) for r in day_rows]
    total_records = sum(d["meal_count"] for d in days_data)
    total_cal = sum(d["sum_cal"] for d in days_data)
    avg_cal = total_cal / len(days_data) if days_data else 0.0
    
    # 목표 달성 성공 일수 (목표치의 80%~115% 이내)
    success_days = sum(
        1 for d in days_data 
        if (target_cal * 0.8) <= d["sum_cal"] <= (target_cal * 1.15)
    )
    
    return {
        "year": year,
        "month": month,
        "month_str": month_prefix,
        "days_data": days_data,
        "recorded_days": len(days_data),
        "total_meals": total_records,
        "total_calories": round(total_cal, 1),
        "avg_calories": round(avg_cal, 1),
        "success_days": success_days,
        "success_rate": round((success_days / len(days_data) * 100), 1) if days_data else 0.0,
        "top_foods": top_foods
    }

def get_yearly_summary(user_id: int, year: int) -> Dict[str, Any]:
    """특정 연도의 월별 평균 칼로리 및 단백질 섭취량을 집계합니다."""
    year_str = f"{year:04d}"
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                substr(recorded_at, 6, 2) as month,
                SUM(calories) as total_cal,
                SUM(protein) as total_protein,
                COUNT(DISTINCT substr(recorded_at, 1, 10)) as active_days,
                COUNT(*) as total_meals
            FROM meal_records
            WHERE user_id = ? AND substr(recorded_at, 1, 4) = ?
            GROUP BY substr(recorded_at, 6, 2)
            ORDER BY month ASC
        """, (user_id, year_str))
        rows = {int(row["month"]): dict(row) for row in cursor.fetchall()}
        
    monthly_data = []
    for m in range(1, 13):
        if m in rows:
            r = rows[m]
            avg_cal = r["total_cal"] / r["active_days"] if r["active_days"] > 0 else 0.0
            avg_pro = r["total_protein"] / r["active_days"] if r["active_days"] > 0 else 0.0
            monthly_data.append({
                "month": f"{m}월",
                "month_num": m,
                "avg_calories": round(avg_cal, 1),
                "avg_protein": round(avg_pro, 1),
                "active_days": r["active_days"],
                "total_meals": r["total_meals"]
            })
        else:
            monthly_data.append({
                "month": f"{m}월",
                "month_num": m,
                "avg_calories": 0.0,
                "avg_protein": 0.0,
                "active_days": 0,
                "total_meals": 0
            })
            
    return {
        "year": year,
        "monthly_data": monthly_data
    }

# 모듈 로드시 DB 테이블 자동 초기화
init_db()
