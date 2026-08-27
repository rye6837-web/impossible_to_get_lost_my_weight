import os
import sys
from PIL import Image
import streamlit as st

# 1. 경로 설정: agent 폴더와 tools 폴더를 파이썬 검색 경로(sys.path)에 등록
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AGENT_DIR = os.path.join(BASE_DIR, 'agent')
TOOLS_DIR = os.path.join(BASE_DIR, 'tools')

for p in [BASE_DIR, AGENT_DIR, TOOLS_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from agent import create_diet_agent

# 2. Streamlit 웹 페이지 레이아웃
st.set_page_config(page_title="AI 다이어트 코치", page_icon="🥗", layout="wide")

st.title("🥗 AI 다이어트 & 영양 코칭 에이전트")
st.caption("식품의약품안전처 표준 영양 DB 기반 맞춤형 식단 분석 및 웰니스 코칭 서비스")

# 4. 세션 상태 관리 (에이전트 인스턴스 및 대화 내역 유지)
if "agent" not in st.session_state:
    st.session_state.agent = create_diet_agent()
    st.session_state.messages = []

# 3. 사이드바: 다이어트 목표 설정 & 📸 사진 입력 UI
with st.sidebar:
    st.header("🎯 내 다이어트 목표")
    target_cal = st.number_input("일일 목표 칼로리 (kcal)", min_value=1200, max_value=4000, value=2000, step=50)
    target_protein = st.number_input("목표 단백질 (g)", min_value=30, max_value=250, value=100, step=5)
    st.divider()
    st.info(f"💡 현재 설정: **{target_cal} kcal** / 단백질 **{target_protein} g**")
    
    st.header("📸 식단 사진 찍기 / 업로드")
    upload_mode = st.radio("사진 입력 방식", ["파일 업로드", "카메라 촬영"], horizontal=True)
    
    uploaded_image_file = None
    if upload_mode == "파일 업로드":
        uploaded_image_file = st.file_uploader("음식 사진 선택", type=["jpg", "jpeg", "png"])
    else:
        uploaded_image_file = st.camera_input("음식 사진 촬영")

    # 사진이 입력되었을 때 분석 버튼 활성화
    if uploaded_image_file:
        pil_image = Image.open(uploaded_image_file)
        st.image(pil_image, caption="선택된 식단 사진", use_container_width=True)
        
        if st.button("🔍 사진 식단 분석 요청", use_container_width=True, type="primary"):
            # 사용자 메시지 기록
            user_msg = "📸 [음식 사진 첨부] 이 사진 속 식단을 분석해줘."
            st.session_state.messages.append({"role": "user", "content": user_msg, "image": pil_image})
            
            # 에이전트에 이미지 + 목표 프롬프트 전송
            prompt_text = (
                f"[사용자 일일 목표: 하루 {target_cal}kcal, 단백질 {target_protein}g]\n"
                "사진 속 음식들의 종류와 대략적인 양을 파악하고, "
                "반드시 `search_food_nutrition` 도구로 각각의 영양 정보를 조회하여 식단을 분석해줘."
            )
            with st.spinner("사진 속 음식 분석 및 영양 DB 조회 중..."):
                try:
                    response_text = st.session_state.agent.send_message([pil_image, prompt_text])
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                except Exception as e:
                    st.session_state.messages.append({"role": "assistant", "content": f"오류 발생: {e}"})
            st.rerun()

    st.divider()
    if st.button("대화 기록 초기화", use_container_width=True):
        st.session_state.agent = create_diet_agent()
        st.session_state.messages = []
        st.rerun()

# 5. 기존 대화 기록 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "image" in msg and msg["image"]:
            st.image(msg["image"], width=300)
        st.markdown(msg["content"])

# 6. 텍스트 사용자 입력창
if prompt := st.chat_input("오늘 드신 식단을 입력해보세요! (예: 점심에 닭가슴살 100g이랑 밥 한 공기 먹었어)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("식품영양 DB 조회 및 영양 분석 중..."):
            context_prompt = f"[사용자 일일 목표: 하루 {target_cal}kcal, 단백질 {target_protein}g] {prompt}"
            try:
                response_text = st.session_state.agent.send_message(context_prompt)
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                error_msg = f"응답 생성 중 오류가 발생했습니다: {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
