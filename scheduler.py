import os
import sys
import time
from datetime import datetime, date, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from db.database import get_connection
from services.telegram_service import send_telegram_monthly_report

def run_monthly_broadcast():
    """모든 텔레그램 연동 사용자에게 지난달 결산 리포트를 발송합니다."""
    today = date.today()
    # 지난달 계산
    first_day_this_month = today.replace(day=1)
    last_day_prev_month = first_day_this_month - timedelta(days=1)
    prev_year = last_day_prev_month.year
    prev_month = last_day_prev_month.month

    print(f"[{datetime.now()}] 📢 {prev_year}년 {prev_month}월 정기 결산 리포트 자동 발송 시작...")
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, telegram_chat_id FROM users WHERE telegram_chat_id IS NOT NULL AND telegram_chat_id != ''")
        users = cursor.fetchall()
        
    print(f"발송 대상 사용자: 총 {len(users)}명")
    for u in users:
        try:
            ok, msg = send_telegram_monthly_report(u["id"], prev_year, prev_month)
            print(f" -> [{u['username']}] {msg}")
        except Exception as e:
            print(f" -> [{u['username']}] 발송 오류: {e}")
            
    print(f"[{datetime.now()}] ✅ 월간 정기 발송 완료!")

if __name__ == "__main__":
    # 직접 실행 시 즉시 발송 테스트
    run_monthly_broadcast()
