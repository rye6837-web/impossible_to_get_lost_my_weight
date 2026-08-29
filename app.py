import os
import sys
from datetime import datetime, date
from PIL import Image
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# 1. 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AGENT_DIR = os.path.join(BASE_DIR, 'agent')
TOOLS_DIR = os.path.join(BASE_DIR, 'tools')
DB_DIR = os.path.join(BASE_DIR, 'db')
SERVICES_DIR = os.path.join(BASE_DIR, 'services')

for p in [BASE_DIR, AGENT_DIR, TOOLS_DIR, DB_DIR, SERVICES_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from agent import create_diet_agent, parse_agent_metadata
from services.telegram_service import send_telegram_monthly_report, send_telegram_message, get_telegram_bot_token

def get_or_create_agent(api_key: str = ""):
    try:
        return create_diet_agent(api_key=api_key)
    except Exception:
        return None

import importlib
import db.database as db_module
importlib.reload(db_module)

register_user = db_module.register_user
authenticate_user = db_module.authenticate_user
update_user_goals = db_module.update_user_goals
update_user_profile = db_module.update_user_profile
update_user_telegram = db_module.update_user_telegram
get_user_by_id = db_module.get_user_by_id
calculate_recommended_nutrition = db_module.calculate_recommended_nutrition
add_meal_record = db_module.add_meal_record
delete_meal_record = db_module.delete_meal_record
add_exercise_record = db_module.add_exercise_record
delete_exercise_record = db_module.delete_exercise_record
get_daily_summary = db_module.get_daily_summary
get_weekly_summary = db_module.get_weekly_summary
get_monthly_summary = db_module.get_monthly_summary
get_yearly_summary = db_module.get_yearly_summary

# 2. Streamlit 웹 페이지 설정
st.set_page_config(page_title="AI 다이어트 & 웰니스 코치", page_icon="🥗", layout="wide")

# 세션 상태 초기화
if "user" not in st.session_state:
    st.session_state.user = None

if "agent" not in st.session_state:
    st.session_state.agent = get_or_create_agent()
    st.session_state.messages = []

# --- [비로그인 상태: 회원가입 및 로그인 화면] ---
if st.session_state.user is None:
    st.title("🥗 AI 다이어트 & 종합 웰니스 코칭 플랫폼")
    st.caption("식약처 표준 영양 DB · METs 운동 대사량 · 개인 맞춤형 풀스택 코칭")
    
    col1, col2, col3 = st.columns([1, 2.5, 1])
    with col2:
        tab_login, tab_register = st.tabs(["🔑 로그인", "📝 회원가입"])
        
        # [로그인 탭]
        with tab_login:
            st.subheader("로그인")
            with st.form("login_form"):
                login_id = st.text_input("아이디", placeholder="아이디를 입력하세요")
                login_pw = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
                submitted = st.form_submit_button("로그인", use_container_width=True, type="primary")
                
                if submitted:
                    user = authenticate_user(login_id, login_pw)
                    if user:
                        st.session_state.user = user
                        st.session_state.agent = get_or_create_agent()
                        st.session_state.messages = []
                        st.success(f"{user['username']}님, 환영합니다!")
                        st.rerun()
                    else:
                        st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
                        
        # [회원가입 탭: 신체 정보 기반 목표 자동 추천]
        with tab_register:
            st.subheader("신규 회원가입")
            reg_id = st.text_input("새 아이디", placeholder="사용할 아이디", key="reg_id_input")
            reg_pw = st.text_input("새 비밀번호 (4자 이상)", type="password", placeholder="비밀번호", key="reg_pw_input")
            
            st.markdown("#### 📏 신체 정보 & 다이어트 목적")
            c1, c2 = st.columns(2)
            with c1:
                gender = st.selectbox("성별", ["남성", "여성"], key="reg_gender")
                height = st.number_input("키 (cm)", min_value=100.0, max_value=250.0, value=175.0, step=0.5, key="reg_height")
                activity = st.selectbox(
                    "평소 활동량", 
                    [
                        "활동 적음 (거의 운동 안 함)", 
                        "가벼운 활동 (주 1~3회 운동)", 
                        "보통 활동 (주 3~5회 운동)", 
                        "많은 활동 (주 6~7회 강한 운동)"
                    ],
                    index=1,
                    key="reg_activity"
                )
            with c2:
                age = st.number_input("나이 (세)", min_value=10, max_value=100, value=28, step=1, key="reg_age")
                weight = st.number_input("몸무게 (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.5, key="reg_weight")
                goal = st.selectbox(
                    "다이어트 목적", 
                    [
                        "체중 감량 (다이어트)", 
                        "체중 유지 (건강 관리)", 
                        "근육 증가 (벌크업)"
                    ],
                    index=0,
                    key="reg_goal"
                )
            
            rec_cal, rec_protein = calculate_recommended_nutrition(
                gender=gender,
                age=int(age),
                height=float(height),
                weight=float(weight),
                activity=activity,
                goal=goal
            )
            
            st.info(
                f"💡 **신체 맞춤 AI 추천**: 일일 **{rec_cal} kcal** / 단백질 **{rec_protein} g**\n\n"
                f"(기초대사량 및 활동량 분석 결과에 따른 추천값이며, 아래에서 직접 수정할 수 있습니다.)"
            )
            
            c_cal, c_pro = st.columns(2)
            with c_cal:
                reg_cal = st.number_input("최종 일일 목표 칼로리 (kcal)", min_value=1000, max_value=4500, value=rec_cal, step=50, key="reg_cal_input")
            with c_pro:
                reg_protein = st.number_input("최종 일일 목표 단백질 (g)", min_value=30, max_value=300, value=rec_protein, step=5, key="reg_pro_input")
            
            if st.button("🎉 회원가입 완료", use_container_width=True, type="primary"):
                success, msg = register_user(
                    username=reg_id, 
                    password=reg_pw, 
                    gender=gender,
                    age=int(age),
                    height=float(height),
                    weight=float(weight),
                    target_cal=int(reg_cal), 
                    target_protein=int(reg_protein)
                )
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
    st.stop()

# --- [로그인 상태: 메인 서비스] ---
current_user = get_user_by_id(st.session_state.user["id"]) or st.session_state.user
st.session_state.user = current_user
user_id = current_user["id"]
user_weight = float(current_user.get("weight", 70.0))
target_cal = int(current_user.get("target_cal", 2000))
target_protein = int(current_user.get("target_protein", 100))

# 사이드바: 프로필, 목표 현황, 식단 및 운동 직접 등록
with st.sidebar:
    st.markdown(f"### 👤 **{current_user['username']}** 님")
    st.caption(f"신체: {current_user.get('gender', '남성')} | {current_user.get('height', 175)}cm | {user_weight}kg")
    
    if st.button("🚪 로그아웃", use_container_width=True):
        st.session_state.user = None
        st.session_state.messages = []
        st.rerun()
        
    st.divider()
    
    # 오늘 영양 및 순 칼로리 요약 미니 배너
    today_sum = get_daily_summary(user_id)
    st.markdown("#### 📅 오늘 섭취 & 운동 현황")
    st.metric(
        label="음식 섭취 칼로리", 
        value=f"{today_sum['total_cal']} kcal", 
        delta=f"목표: {target_cal} kcal"
    )
    st.metric(
        label="🔥 운동 소모 칼로리", 
        value=f"-{today_sum['total_burned']} kcal", 
        delta=f"{today_sum['total_ex_min']}분 운동"
    )
    st.metric(
        label="✨ 순 칼로리 (Net)", 
        value=f"{today_sum['net_cal']} kcal", 
        delta=f"{round(today_sum['net_cal'] - target_cal, 1)} kcal",
        delta_color="inverse" if today_sum['net_cal'] > target_cal else "normal"
    )
    
    st.divider()
    
    # 직접 기록 탭 (식단 / 운동)
    tab_rec_meal, tab_rec_ex = st.tabs(["🍱 식단 기록", "🏃 운동 기록"])
    
    with tab_rec_meal:
        with st.form("manual_meal_form"):
            f_date = st.date_input("식사 날짜", value=date.today(), key="meal_date_input")
            f_type = st.selectbox("식사 종류", ["아침", "점심", "저녁", "간식", "야식"], index=1)
            f_name = st.text_input("음식명", placeholder="예: 닭가슴살 샐러드")
            
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                f_cal = st.number_input("칼로리 (kcal)", min_value=0.0, value=300.0, step=10.0)
                f_carbs = st.number_input("탄수화물 (g)", min_value=0.0, value=20.0, step=1.0)
                f_sugar = st.number_input("당류 (g)", min_value=0.0, value=2.0, step=1.0)
            with c_f2:
                f_protein = st.number_input("단백질 (g)", min_value=0.0, value=25.0, step=1.0)
                f_fat = st.number_input("지방 (g)", min_value=0.0, value=5.0, step=1.0)
                f_sodium = st.number_input("나트륨 (mg)", min_value=0.0, value=250.0, step=10.0)
                
            f_memo = st.text_input("메모", placeholder="특이사항 입력")
            save_meal_btn = st.form_submit_button("식단 DB 저장", use_container_width=True, type="primary")
            
            if save_meal_btn:
                rec_datetime = f"{f_date.strftime('%Y-%m-%d')} {datetime.now().strftime('%H:%M:%S')}"
                ok, msg = add_meal_record(
                    user_id=user_id,
                    food_name=f_name,
                    calories=f_cal,
                    carbs=f_carbs,
                    protein=f_protein,
                    fat=f_fat,
                    sugar=f_sugar,
                    sodium=f_sodium,
                    meal_type=f_type,
                    recorded_at=rec_datetime,
                    feedback=f_memo
                )
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
                    
    with tab_rec_ex:
        with st.form("manual_exercise_form"):
            e_date = st.date_input("운동 날짜", value=date.today(), key="ex_date_input")
            e_name = st.text_input("운동 종류", placeholder="예: 러닝, 헬스, 수영, 자전거")
            e_min = st.number_input("운동 시간 (분)", min_value=1.0, max_value=300.0, value=30.0, step=5.0)
            e_cal = st.number_input("소모 칼로리 (kcal, 모르면 0 입력 시 자동 계산)", min_value=0.0, value=0.0, step=10.0)
            e_memo = st.text_input("메모", placeholder="운동 강도 등")
            save_ex_btn = st.form_submit_button("운동 DB 저장", use_container_width=True, type="primary")
            
            if save_ex_btn:
                # 0이면 METs 자동 계산
                final_burned = e_cal
                if final_burned <= 0:
                    from tools.exercise_tool import calculate_exercise_calories
                    res = calculate_exercise_calories(e_name, e_min, user_weight)
                    final_burned = res.get("소모칼로리(kcal)", 150.0)
                    
                rec_datetime = f"{e_date.strftime('%Y-%m-%d')} {datetime.now().strftime('%H:%M:%S')}"
                ok, msg = add_exercise_record(
                    user_id=user_id,
                    exercise_name=e_name,
                    duration_min=e_min,
                    calories_burned=final_burned,
                    memo=e_memo,
                    recorded_at=rec_datetime
                )
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

# 상단 서비스 메뉴 탭
tab_coach, tab_dashboard, tab_settings = st.tabs([
    "🥗 AI 식단 & 웰니스 코치", 
    "📊 식단 & 운동 통계 대시보드", 
    "⚙️ 내 설정 & 텔레그램 연동"
])

# ==========================================
# 1. AI 식단 코치 대화 탭 (Human-in-the-Loop 자동 저장 연동)
# ==========================================
with tab_coach:
    st.title("🥗 AI 다이어트 & 웰니스 코칭 에이전트")
    st.caption("식약처 표준 영양 DB · METs 운동 대사량 · 영양 백과 지식 RAG 3대 도구 탑재")
    
    # API 키 미등록 시 입력 안내
    if st.session_state.agent is None:
        st.warning("⚠️ Google Gemini API 키가 아직 설정되지 않았습니다.")
        with st.form("api_key_form"):
            input_key = st.text_input("Gemini API Key", type="password", placeholder="AIzaSy...")
            save_key_btn = st.form_submit_button("API 키 적용", type="primary")
            if save_key_btn and input_key.strip():
                st.session_state["GEMINI_API_KEY"] = input_key.strip()
                try:
                    st.session_state.agent = create_diet_agent(api_key=input_key.strip())
                    st.success("✅ API 키가 성공적으로 등록되었습니다!")
                    st.rerun()
                except Exception as e:
                    st.error(f"API 키 등록 실패: {e}")
        st.info("💡 Tip: `.streamlit/secrets.toml` 파일에 `GEMINI_API_KEY = '...'`를 등록해두시면 자동 로드됩니다.")
    
    # 📸 사진 업로드 / 카메라 촬영 섹션
    with st.expander("📸 음식 사진으로 식단 분석하기", expanded=False):
        c_photo1, c_photo2 = st.columns([1, 1])
        with c_photo1:
            upload_mode = st.radio("사진 입력 방식", ["파일 업로드", "카메라 촬영"], horizontal=True)
            uploaded_image_file = None
            if upload_mode == "파일 업로드":
                uploaded_image_file = st.file_uploader("음식 사진 선택", type=["jpg", "jpeg", "png"])
            else:
                uploaded_image_file = st.camera_input("음식 사진 촬영")
        
        with c_photo2:
            if uploaded_image_file:
                pil_image = Image.open(uploaded_image_file)
                st.image(pil_image, caption="선택된 식단 사진", use_container_width=True)
                
                if st.button("🔍 사진 식단 분석 요청", use_container_width=True, type="primary"):
                    user_msg = "📸 [음식 사진 첨부] 이 사진 속 식단을 분석해줘."
                    st.session_state.messages.append({"role": "user", "content": user_msg, "image": pil_image})
                    
                    prompt_text = (
                        f"[사용자 정보: 체중 {user_weight}kg, 일일 목표: {target_cal}kcal, 단백질 {target_protein}g]\n"
                        "사진 속 음식들의 종류와 대략적인 양을 파악하고, "
                        "`search_food_nutrition` 도구로 각각의 영양 정보를 조회하여 식단을 분석해줘. "
                        "분석 완료 시 마지막 줄에 <!-- MEAL_DATA: {...} --> 태그를 반드시 포함해줘."
                    )
                    with st.spinner("사진 속 음식 분석 및 영양 DB 조회 중..."):
                        try:
                            response_text = st.session_state.agent.send_message([pil_image, prompt_text])
                            clean_text, meal_meta, ex_meta = parse_agent_metadata(response_text)
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": clean_text,
                                "meal_meta": meal_meta,
                                "ex_meta": ex_meta
                            })
                        except Exception as e:
                            st.session_state.messages.append({"role": "assistant", "content": f"오류 발생: {e}"})
                    st.rerun()

    # 대화 기록 렌더링 (Human-in-the-Loop 스마트 저장 카드 연동)
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            if "image" in msg and msg["image"]:
                st.image(msg["image"], width=300)
            st.markdown(msg["content"])
            
            # [1순위 핵심] AI가 감지한 식단 정보 스마트 저장 카드
            if msg["role"] == "assistant" and msg.get("meal_meta"):
                m_data = msg["meal_meta"]
                with st.container():
                    st.markdown(
                        f"🍱 **[감지된 식단]**: **{m_data.get('food_name', '식단')}** "
                        f"({m_data.get('calories', 0)} kcal | 탄 {m_data.get('carbs', 0)}g · 단 {m_data.get('protein', 0)}g · 지 {m_data.get('fat', 0)}g)"
                    )
                    c_btn1, c_btn2 = st.columns([2, 3])
                    with c_btn1:
                        m_type = st.selectbox(
                            "식사 분류", 
                            ["아침", "점심", "저녁", "간식", "야식"], 
                            index=["아침", "점심", "저녁", "간식", "야식"].index(m_data.get("meal_type", "점심")) if m_data.get("meal_type") in ["아침", "점심", "저녁", "간식", "야식"] else 1,
                            key=f"card_mtype_{idx}"
                        )
                    with c_btn2:
                        if st.button("💾 이 식단 DB에 바로 저장", key=f"save_meal_card_{idx}", type="primary", use_container_width=True):
                            ok, res_msg = add_meal_record(
                                user_id=user_id,
                                food_name=m_data.get("food_name", "식단"),
                                calories=float(m_data.get("calories", 0)),
                                carbs=float(m_data.get("carbs", 0)),
                                protein=float(m_data.get("protein", 0)),
                                fat=float(m_data.get("fat", 0)),
                                sugar=float(m_data.get("sugar", 0)),
                                sodium=float(m_data.get("sodium", 0)),
                                meal_type=m_type
                            )
                            if ok:
                                st.success("✅ 식단이 개인 DB에 성공적으로 저장되었습니다!")
                                st.rerun()
                            else:
                                st.error(res_msg)

            # [2순위 핵심] AI가 감지한 운동 정보 스마트 저장 카드
            if msg["role"] == "assistant" and msg.get("ex_meta"):
                e_data = msg["ex_meta"]
                with st.container():
                    st.markdown(
                        f"🔥 **[감지된 운동]**: **{e_data.get('exercise_name', '운동')}** "
                        f"({e_data.get('duration_min', 30)}분 | **{e_data.get('calories_burned', 0)} kcal** 소모)"
                    )
                    if st.button("💾 이 운동 DB에 바로 저장", key=f"save_ex_card_{idx}", type="primary", use_container_width=True):
                        ok, res_msg = add_exercise_record(
                            user_id=user_id,
                            exercise_name=e_data.get("exercise_name", "운동"),
                            duration_min=float(e_data.get("duration_min", 30)),
                            calories_burned=float(e_data.get("calories_burned", 0))
                        )
                        if ok:
                            st.success("✅ 운동 기록이 개인 DB에 성공적으로 저장되었습니다!")
                            st.rerun()
                        else:
                            st.error(res_msg)

    # 텍스트 입력창
    if prompt := st.chat_input("식단, 운동, 또는 영양 질문을 입력하세요! (예: 점심에 김치찌개 먹었어 / 오늘 러닝 30분 했어 / 혈당 관리 팁 알려줘)"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("AI 웰니스 코치 분석 중..."):
                context_prompt = (
                    f"[사용자 정보: 체중 {user_weight}kg, 일일 목표: {target_cal}kcal, 단백질 {target_protein}g]\n"
                    f"{prompt}\n"
                    "식단 분석 완료 시 <!-- MEAL_DATA: {...} --> 태그를, 운동 계산 완료 시 <!-- EXERCISE_DATA: {...} --> 태그를 마지막 줄에 포함해주세요."
                )
                try:
                    response_text = st.session_state.agent.send_message(context_prompt)
                    clean_text, meal_meta, ex_meta = parse_agent_metadata(response_text)
                    st.markdown(clean_text)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": clean_text,
                        "meal_meta": meal_meta,
                        "ex_meta": ex_meta
                    })
                    st.rerun()
                except Exception as e:
                    error_msg = f"응답 생성 중 오류가 발생했습니다: {e}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

    if st.button("🧹 대화 내용 초기화"):
        st.session_state.agent = get_or_create_agent()
        st.session_state.messages = []
        st.rerun()

# ==========================================
# 2. 식단 & 운동 통계 대시보드 탭 (일/주/월/년)
# ==========================================
with tab_dashboard:
    st.header("📊 개인 맞춤 식단 & 운동 통계 대시보드")
    
    subtab_daily, subtab_weekly, subtab_monthly, subtab_yearly = st.tabs([
        "📅 일별 통계", 
        "📈 주간 통계", 
        "🗓️ 월별 통계", 
        "📊 연간 통계"
    ])
    
    # --- [일별 통계] ---
    with subtab_daily:
        c_d1, c_d2 = st.columns([1, 3])
        with c_d1:
            selected_date = st.date_input("조회 날짜 선택", value=date.today(), key="daily_stat_date")
        
        date_str = selected_date.strftime("%Y-%m-%d")
        daily_res = get_daily_summary(user_id, date_str)
        
        # 1. 주요 지표 카드 (식단 섭취 + 운동 소모 + 순 칼로리)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("총 섭취 칼로리", f"{daily_res['total_cal']} kcal", f"목표 {target_cal} kcal")
        m2.metric("🔥 운동 소모", f"-{daily_res['total_burned']} kcal", f"{daily_res['total_ex_min']}분 운동")
        m3.metric("✨ 순 칼로리 (Net)", f"{daily_res['net_cal']} kcal", f"목표 대비 {round(daily_res['net_cal'] - target_cal, 1)} kcal")
        m4.metric("단백질 섭취", f"{daily_res['total_protein']} g", f"목표 {target_protein} g")
        
        st.divider()
        
        # 2. 시각화 차트
        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            # 순 칼로리 게이지 차트
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=daily_res['net_cal'],
                title={'text': f"<b>{date_str} 순 칼로리 달성도</b><br><span style='font-size:12px;color:gray;'>섭취({daily_res['total_cal']}) - 소모({daily_res['total_burned']})</span>"},
                delta={'reference': target_cal, 'increasing': {'color': "#EF553B" if daily_res['net_cal'] > target_cal else "#00CC96"}},
                gauge={
                    'axis': {'range': [None, target_cal * 1.5]},
                    'bar': {'color': "#4E79A7"},
                    'steps': [
                        {'range': [0, target_cal * 0.8], 'color': "#E8F4F8"},
                        {'range': [target_cal * 0.8, target_cal * 1.1], 'color': "#D1E7DD"},
                        {'range': [target_cal * 1.1, target_cal * 1.5], 'color': "#F8D7DA"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': target_cal
                    }
                }
            ))
            fig_gauge.update_layout(height=320, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)
            
        with c_chart2:
            # 3대 영양소 도넛 차트
            nutri_labels = ['탄수화물(g)', '단백질(g)', '지방(g)']
            nutri_values = [daily_res['total_carbs'], daily_res['total_protein'], daily_res['total_fat']]
            
            if sum(nutri_values) > 0:
                fig_pie = px.pie(
                    names=nutri_labels, 
                    values=nutri_values, 
                    title=f"<b>3대 영양소 섭취 밸런스</b>",
                    hole=0.45,
                    color_discrete_sequence=['#3366CC', '#109618', '#FF9900']
                )
                fig_pie.update_layout(height=320, margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("💡 해당 날짜에 기록된 영양 데이터가 없습니다.")

        # 3. 당일 식단 & 운동 목록
        c_list1, c_list2 = st.columns(2)
        with c_list1:
            st.markdown(f"#### 📋 {date_str} 상세 식단 기록 ({len(daily_res['records'])}건)")
            if daily_res['records']:
                for rec in daily_res['records']:
                    with st.container():
                        cr1, cr2 = st.columns([4, 1])
                        with cr1:
                            st.markdown(f"**[{rec['meal_type']}]** **{rec['food_name']}** — **{rec['calories']} kcal**")
                            st.caption(f"탄 {rec['carbs']}g · 단 {rec['protein']}g · 지 {rec['fat']}g | {rec['recorded_at'][11:16]}")
                        with cr2:
                            if st.button("🗑️", key=f"del_meal_{rec['id']}"):
                                if delete_meal_record(rec['id'], user_id):
                                    st.rerun()
                        st.divider()
            else:
                st.info("등록된 식단이 없습니다.")
                
        with c_list2:
            st.markdown(f"#### 🏃 {date_str} 운동 기록 ({len(daily_res['exercise_records'])}건)")
            if daily_res['exercise_records']:
                for ex in daily_res['exercise_records']:
                    with st.container():
                        er1, er2 = st.columns([4, 1])
                        with er1:
                            st.markdown(f"**{ex['exercise_name']}** ({ex['duration_min']}분) — **🔥 {ex['calories_burned']} kcal**")
                            if ex['memo']:
                                st.caption(f"💬 {ex['memo']}")
                        with er2:
                            if st.button("🗑️", key=f"del_ex_{ex['id']}"):
                                if delete_exercise_record(ex['id'], user_id):
                                    st.rerun()
                        st.divider()
            else:
                st.info("등록된 운동이 없습니다.")

    # --- [주간 통계] ---
    with subtab_weekly:
        weekly_res = get_weekly_summary(user_id)
        st.markdown(f"#### 📈 최근 7일 식단 트렌드 ({weekly_res['start_date']} ~ {weekly_res['end_date']})")
        
        w_m1, w_m2, w_m3 = st.columns(3)
        w_m1.metric("주간 평균 칼로리", f"{weekly_res['avg_calories']} kcal", f"목표 대비 {round(weekly_res['avg_calories'] - target_cal, 1)} kcal")
        w_m2.metric("주간 평균 단백질", f"{weekly_res['avg_protein']} g", f"목표 대비 {round(weekly_res['avg_protein'] - target_protein, 1)} g")
        w_m3.metric("기록 일수", f"{weekly_res['active_days_count']}일 / 7일")
        
        df_week = pd.DataFrame(weekly_res['daily_data'])
        if not df_week.empty:
            df_week['day_label'] = df_week['date'].str[5:] + " (" + df_week['weekday'] + ")"
            
            # 주간 칼로리 막대 및 목표선 차트
            fig_w_cal = go.Figure()
            fig_w_cal.add_trace(go.Bar(
                x=df_week['day_label'], 
                y=df_week['calories'], 
                name="섭취 칼로리(kcal)",
                marker_color='#3366CC'
            ))
            fig_w_cal.add_trace(go.Scatter(
                x=df_week['day_label'],
                y=[target_cal] * len(df_week),
                mode='lines',
                name='목표 칼로리',
                line=dict(color='red', dash='dash', width=2)
            ))
            fig_w_cal.update_layout(title="<b>일별 칼로리 섭취 vs 일일 목표</b>", height=350, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_w_cal, use_container_width=True)
            
            # 주간 단백질 추이 차트
            fig_w_pro = go.Figure()
            fig_w_pro.add_trace(go.Bar(
                x=df_week['day_label'], 
                y=df_week['protein'], 
                name="단백질(g)",
                marker_color='#109618'
            ))
            fig_w_pro.add_trace(go.Scatter(
                x=df_week['day_label'],
                y=[target_protein] * len(df_week),
                mode='lines',
                name='목표 단백질',
                line=dict(color='orange', dash='dash', width=2)
            ))
            fig_w_pro.update_layout(title="<b>일별 단백질 섭취량(g) 추이</b>", height=320, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_w_pro, use_container_width=True)

    # --- [월별 통계] ---
    with subtab_monthly:
        now = datetime.now()
        c_m_sel1, c_m_sel2 = st.columns(2)
        with c_m_sel1:
            sel_year = st.selectbox("연도 선택", range(2024, now.year + 2), index=now.year - 2024, key="monthly_sel_year")
        with c_m_sel2:
            sel_month = st.selectbox("월 선택", range(1, 13), index=now.month - 1, key="monthly_sel_month")
            
        monthly_res = get_monthly_summary(user_id, sel_year, sel_month, target_cal)
        
        st.markdown(f"#### 🗓️ {sel_year}년 {sel_month}월 결산 리포트")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("총 섭취 칼로리", f"{monthly_res['total_calories']:,} kcal")
        kpi2.metric("일평균 섭취 칼로리", f"{monthly_res['avg_calories']} kcal")
        kpi3.metric("기록 일수", f"{monthly_res['recorded_days']}일")
        kpi4.metric("목표 달성률", f"{monthly_res['success_rate']}%", f"{monthly_res['success_days']}일 성공")
        
        c_mchart1, c_mchart2 = st.columns([3, 2])
        with c_mchart1:
            if monthly_res['days_data']:
                df_month = pd.DataFrame(monthly_res['days_data'])
                df_month['day_num'] = df_month['day'].str[8:] + "일"
                fig_m = px.line(
                    df_month, 
                    x='day_num', 
                    y='sum_cal', 
                    markers=True,
                    title=f"<b>{sel_month}월 일별 칼로리 변화 추이</b>",
                    labels={'day_num': '일자', 'sum_cal': '칼로리(kcal)'}
                )
                fig_m.add_hline(y=target_cal, line_dash="dash", line_color="red", annotation_text="목표 칼로리")
                fig_m.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_m, use_container_width=True)
            else:
                st.info("해당 월에 기록된 식단 데이터가 없습니다.")
                
        with c_mchart2:
            st.markdown("##### 🏆 이번 달 최다 섭취 메뉴 TOP 5")
            if monthly_res['top_foods']:
                df_top = pd.DataFrame(monthly_res['top_foods'])
                fig_top = px.bar(
                    df_top, 
                    x='count', 
                    y='food_name', 
                    orientation='h',
                    labels={'count': '섭취 횟수', 'food_name': '음식명'},
                    color='count',
                    color_continuous_scale='Blues'
                )
                fig_top.update_layout(height=350, yaxis={'categoryorder': 'total ascending'}, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_top, use_container_width=True)
            else:
                st.info("기록된 음식이 없습니다.")

    # --- [연간 통계] ---
    with subtab_yearly:
        sel_y = st.selectbox("연도 선택", range(2024, now.year + 2), index=now.year - 2024, key="yearly_sel_year")
        yearly_res = get_yearly_summary(user_id, sel_y)
        
        st.markdown(f"#### 📊 {sel_y}년 연간 월별 칼로리 & 단백질 추이")
        df_year = pd.DataFrame(yearly_res['monthly_data'])
        
        fig_y = go.Figure()
        fig_y.add_trace(go.Scatter(
            x=df_year['month'], 
            y=df_year['avg_calories'], 
            mode='lines+markers',
            name="월평균 칼로리(kcal)",
            line=dict(color="#3366CC", width=3)
        ))
        fig_y.add_trace(go.Scatter(
            x=df_year['month'], 
            y=df_year['avg_protein'], 
            mode='lines+markers',
            name="월평균 단백질(g)",
            yaxis="y2",
            line=dict(color="#109618", width=3)
        ))
        fig_y.update_layout(
            title=f"<b>{sel_y}년 월별 평균 섭취 추이</b>",
            yaxis=dict(title="칼로리(kcal)"),
            yaxis2=dict(title="단백질(g)", overlaying="y", side="right"),
            height=380,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_y, use_container_width=True)

# ==========================================
# 3. 내 설정 & 텔레그램 연동 탭
# ==========================================
with tab_settings:
    st.header("⚙️ 내 정보 & 환경 설정")
    
    col_prof, col_goals = st.columns(2)
    
    # 1. 신체 정보 수정
    with col_prof:
        st.markdown("#### 📏 신체 정보 수정 (키 / 몸무게)")
        with st.form("update_profile_form"):
            curr_gender = current_user.get("gender", "남성")
            curr_age = int(current_user.get("age", 28))
            curr_height = float(current_user.get("height", 175.0))
            curr_weight = float(current_user.get("weight", 70.0))
            
            p_gender = st.selectbox("성별", ["남성", "여성"], index=0 if curr_gender == "남성" else 1)
            p_age = st.number_input("나이 (세)", min_value=10, max_value=100, value=curr_age, step=1)
            p_height = st.number_input("키 (cm)", min_value=100.0, max_value=250.0, value=curr_height, step=0.5)
            p_weight = st.number_input("몸무게 (kg)", min_value=30.0, max_value=200.0, value=curr_weight, step=0.5)
            
            save_prof_btn = st.form_submit_button("신체 정보 저장", use_container_width=True, type="primary")
            
            if save_prof_btn:
                if update_user_profile(user_id, p_gender, int(p_age), float(p_height), float(p_weight)):
                    st.success("신체 정보가 성공적으로 수정되었습니다!")
                    st.rerun()
                else:
                    st.error("신체 정보 저장 실패")

    # 2. 다이어트 목표 설정
    with col_goals:
        st.markdown("#### 🎯 일일 다이어트 목표 설정")
        
        # 신체 정보 기준 자동 계산 도우미
        with st.expander("💡 내 신체 기준 맞춤 목표 계산기", expanded=False):
            calc_act = st.selectbox(
                "활동량", 
                ["활동 적음 (거의 운동 안 함)", "가벼운 활동 (주 1~3회 운동)", "보통 활동 (주 3~5회 운동)", "많은 활동 (주 6~7회 강한 운동)"],
                index=1
            )
            calc_goal = st.selectbox(
                "목적", 
                ["체중 감량 (다이어트)", "체중 유지 (건강 관리)", "근육 증가 (벌크업)"],
                index=0
            )
            rec_c, rec_p = calculate_recommended_nutrition(
                gender=current_user.get("gender", "남성"),
                age=int(current_user.get("age", 28)),
                height=float(current_user.get("height", 175.0)),
                weight=float(current_user.get("weight", 70.0)),
                activity=calc_act,
                goal=calc_goal
            )
            st.info(f"👉 추천 수치: **{rec_c} kcal** / **{rec_p} g**")
            
        with st.form("update_goals_form"):
            new_target_cal = st.number_input("일일 목표 칼로리 (kcal)", min_value=1000, max_value=4500, value=target_cal, step=50)
            new_target_pro = st.number_input("일일 목표 단백질 (g)", min_value=30, max_value=300, value=target_protein, step=5)
            save_goal_btn = st.form_submit_button("목표 수치 저장", use_container_width=True, type="primary")
            
            if save_goal_btn:
                if update_user_goals(user_id, new_target_cal, new_target_pro):
                    st.success("목표가 성공적으로 갱신되었습니다!")
                    st.rerun()
                else:
                    st.error("목표 저장 실패")

    st.divider()
    
    # 3. 텔레그램 연동 섹션
    st.markdown("#### 📱 텔레그램 리포트 연동")
    st.caption("매월 1일 월간 식단 결산 통계 리포트를 텔레그램으로 자동 전송받을 수 있습니다.")
    
    col_tg1, col_tg2 = st.columns(2)
    with col_tg1:
        with st.form("update_telegram_form"):
            current_tg = current_user.get("telegram_chat_id") or ""
            new_tg_id = st.text_input("텔레그램 Chat ID", value=current_tg, placeholder="예: 123456789")
            save_tg_btn = st.form_submit_button("텔레그램 Chat ID 저장", use_container_width=True, type="primary")
            
            if save_tg_btn:
                if update_user_telegram(user_id, new_tg_id):
                    st.success("텔레그램 Chat ID가 저장되었습니다!")
                    st.rerun()
                else:
                    st.error("텔레그램 ID 저장 실패")
                    
        # 봇 토큰 설정
        saved_bot_token = get_telegram_bot_token()
        with st.form("update_bot_token_form"):
            tg_token_input = st.text_input("텔레그램 Bot Token", value=saved_bot_token, type="password", placeholder="7123456789:AAH...")
            save_token_btn = st.form_submit_button("Bot Token 적용", use_container_width=True)
            if save_token_btn and tg_token_input.strip():
                st.session_state["TELEGRAM_BOT_TOKEN"] = tg_token_input.strip()
                st.success("봇 토큰이 적용되었습니다!")
                st.rerun()

    with col_tg2:
        st.markdown("##### 🚀 텔레그램 리포트 테스트 발송")
        if not current_user.get("telegram_chat_id"):
            st.warning("⚠️ Chat ID를 먼저 등록해주세요.")
        elif not get_telegram_bot_token():
            st.warning("⚠️ 텔레그램 Bot Token을 등록해주세요.")
        else:
            st.success(f"✅ 연동 완료! (Chat ID: `{current_user.get('telegram_chat_id')}`)")
            
            now_dt = datetime.now()
            if st.button("📲 이번 달 식단 결산 리포트 즉시 전송", use_container_width=True, type="primary"):
                with st.spinner("텔레그램으로 월간 결산 리포트 전송 중..."):
                    ok, msg = send_telegram_monthly_report(user_id, now_dt.year, now_dt.month)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
                        
            if st.button("✉️ 연동 확인 테스트 메시지 전송", use_container_width=True):
                ok, msg = send_telegram_message(
                    current_user["telegram_chat_id"], 
                    "🎉 *[AI 다이어트 코치]*\n텔레그램 알림 연동이 성공적으로 완료되었습니다! 매달 1일에 월간 식단 통계 리포트가 전송됩니다."
                )
                if ok:
                    st.success("테스트 메시지가 발송되었습니다! 텔레그램을 확인해보세요.")
                else:
                    st.error(msg)

    st.info("💡 텔레그램 `@BotFather`에서 발급받은 **Bot Token**을 입력하시면 즉시 알림 전송이 활성화됩니다.")
