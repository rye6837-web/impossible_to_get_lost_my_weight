import os
import io
import requests
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # GUI 없는 백엔드 사용
from datetime import datetime
from typing import Optional, Tuple, Dict, Any

from db.database import get_user_by_id, get_monthly_summary

def get_telegram_bot_token() -> str:
    """텔레그램 봇 토큰을 검색합니다."""
    # 1. session_state
    if "TELEGRAM_BOT_TOKEN" in st.session_state and st.session_state["TELEGRAM_BOT_TOKEN"]:
        return st.session_state["TELEGRAM_BOT_TOKEN"]
    # 2. secrets.toml
    try:
        if "TELEGRAM_BOT_TOKEN" in st.secrets:
            return st.secrets["TELEGRAM_BOT_TOKEN"]
    except Exception:
        pass
    # 3. 환경 변수
    return os.getenv("TELEGRAM_BOT_TOKEN", "")

def send_telegram_message(chat_id: str, text: str, bot_token: Optional[str] = None) -> Tuple[bool, str]:
    """텔레그램 텍스트 메시지를 전송합니다."""
    token = bot_token or get_telegram_bot_token()
    if not token:
        return False, "TELEGRAM_BOT_TOKEN이 설정되지 않았습니다. Bot Token을 입력해주세요."
    if not chat_id:
        return False, "사용자의 텔레그램 Chat ID가 설정되지 않았습니다."
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        res_data = response.json()
        if res_data.get("ok"):
            return True, "메시지가 성공적으로 전송되었습니다!"
        else:
            return False, f"텔레그램 전송 실패: {res_data.get('description', '알 수 없는 오류')}"
    except Exception as e:
        return False, f"텔레그램 API 호출 오류: {e}"

def generate_monthly_chart_image(monthly_res: Dict[str, Any], target_cal: int = 2000) -> Optional[io.BytesIO]:
    """월간 통계 그래프를 이미지 바이트로 생성합니다."""
    days_data = monthly_res.get("days_data", [])
    if not days_data:
        return None
        
    days = [d["day"][8:] for d in days_data]
    cals = [d["sum_cal"] for d in days_data]
    
    plt.figure(figsize=(10, 5))
    plt.plot(days, cals, marker='o', color='#3366CC', linewidth=2.5, label='섭취 칼로리 (kcal)')
    plt.axhline(y=target_cal, color='red', linestyle='--', linewidth=1.5, label=f'일일 목표 ({target_cal} kcal)')
    
    plt.title(f"[{monthly_res['year']}년 {monthly_res['month']}월] 일별 칼로리 섭취 추이", fontsize=14, fontweight='bold')
    plt.xlabel("일자", fontsize=11)
    plt.ylabel("칼로리 (kcal)", fontsize=11)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='upper right')
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    buf.seek(0)
    plt.close()
    return buf

def send_telegram_monthly_report(user_id: int, year: int, month: int, bot_token: Optional[str] = None) -> Tuple[bool, str]:
    """사용자의 월간 식단 결산 통계 리포트 메시지 및 차트를 텔레그램으로 전송합니다."""
    user = get_user_by_id(user_id)
    if not user:
        return False, "사용자 정보를 찾을 수 없습니다."
        
    chat_id = user.get("telegram_chat_id")
    if not chat_id:
        return False, "등록된 텔레그램 Chat ID가 없습니다. 먼저 [내 설정]에서 Chat ID를 등록해주세요."
        
    token = bot_token or get_telegram_bot_token()
    if not token:
        return False, "텔레그램 봇 토큰(BOT_TOKEN)이 설정되지 않았습니다."
        
    target_cal = int(user.get("target_cal", 2000))
    target_pro = int(user.get("target_protein", 100))
    monthly_res = get_monthly_summary(user_id, year, month, target_cal)
    
    # 리포트 텍스트 구성
    report_text = (
        f"🥗 *[AI 다이어트 코치]*\n"
        f"📊 *{user['username']} 님의 {year}년 {month}월 식단 결산 리포트*\n\n"
        f"🎯 *목표 설정*: 일일 {target_cal} kcal / 단백질 {target_pro} g\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"• 📅 *총 식단 기록 일수*: {monthly_res['recorded_days']}일 ({monthly_res['total_meals']}회 식사)\n"
        f"• 🔥 *총 섭취 칼로리*: {monthly_res['total_calories']:,} kcal\n"
        f"• 📈 *일평균 섭취 칼로리*: {monthly_res['avg_calories']} kcal\n"
        f"• 🏆 *목표 달성 성공률*: {monthly_res['success_rate']}% ({monthly_res['success_days']}일 성공)\n\n"
    )
    
    # 최다 섭취 음식 TOP 3
    if monthly_res.get("top_foods"):
        report_text += "🍱 *이번 달 최다 섭취 음식 TOP 3*:\n"
        for i, food in enumerate(monthly_res["top_foods"][:3], 1):
            report_text += f"  {i}. {food['food_name']} ({food['count']}회, 총 {int(food['total_cal'])} kcal)\n"
        report_text += "\n"
        
    # AI 코칭 총평
    if monthly_res['success_rate'] >= 70:
        report_text += "💡 *코칭 총평*: 훌륭합니다! 꾸준히 목표를 지켜가고 계시네요. 다음 달에도 이 페이스를 유지해보세요! 💪"
    elif monthly_res['recorded_days'] > 0:
        report_text += "💡 *코칭 총평*: 꾸준히 기록하는 습관이 멋집니다! 다음 달에는 일일 목표치에 조금 더 가깝게 밸런스를 맞춰보세요. ✨"
    else:
        report_text += "💡 *코칭 총평*: 이번 달에는 기록이 많지 않았습니다. 다음 달에는 매일 식단을 기록하며 건강을 챙겨보세요! 🌱"

    # 1. 텍스트 전송
    ok, msg = send_telegram_message(chat_id, report_text, token)
    if not ok:
        return False, msg
        
    # 2. 그래프 이미지 전송 (옵션)
    img_buf = generate_monthly_chart_image(monthly_res, target_cal)
    if img_buf:
        photo_url = f"https://api.telegram.org/bot{token}/sendPhoto"
        try:
            files = {'photo': ('chart.png', img_buf, 'image/png')}
            requests.post(photo_url, data={'chat_id': chat_id, 'caption': f"📊 {year}년 {month}월 칼로리 추이 그래프"}, files=files, timeout=15)
        except Exception:
            pass  # 텍스트는 이미 성공했으므로 이미지는 보조
            
    return True, f"{month}월 결산 리포트가 텔레그램으로 성공적으로 전송되었습니다! 📱"
