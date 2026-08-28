import os
import sys
import streamlit as st
from google import genai
from google.genai import types

# 1. 모듈 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))
TOOLS_DIR = os.path.join(PROJECT_DIR, 'tools')

if TOOLS_DIR not in sys.path:
    sys.path.append(TOOLS_DIR)
if PROJECT_DIR not in sys.path:
    sys.path.append(PROJECT_DIR)

from tools import search_food_nutrition

def get_api_key() -> str:
    """Gemini API 키를 여러 소스에서 순차적으로 탐색합니다."""
    # 1. Streamlit session_state
    if "GEMINI_API_KEY" in st.session_state and st.session_state["GEMINI_API_KEY"]:
        return st.session_state["GEMINI_API_KEY"]
    # 2. Streamlit secrets
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    # 3. 환경 변수
    return os.getenv("GEMINI_API_KEY", "")

# 3. 에이전트 시스템 프롬프트
SYSTEM_INSTRUCTION = """
당신은 전문적이고 친절한 'AI 다이어트 & 웰니스 코치 에이전트'입니다.
사용자가 식단이나 음식을 이야기하면, 칼로리와 영양소를 절대 임의로 지어내지 말고 반드시 `search_food_nutrition` 도구를 호출하여 정확한 수치를 확인하세요.

답변 가이드라인:
1. 섭취한 음식의 총 칼로리 및 탄수화물, 단백질, 지방, 당류, 나트륨 수치를 요약해 보여줍니다.
2. 사용자의 일일 목표치 대비 현재 식단이 적절한지 진단합니다.
3. 다음 식사(저녁 또는 간식)에 섭취하면 좋은 대체 추천 메뉴와 실천 팁을 제안합니다.
"""

class DietAgent:
    def __init__(self, api_key: str = ""):
        self.api_key = api_key or get_api_key()
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다. API 키를 입력하거나 .streamlit/secrets.toml에 등록해주세요.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.chat = self.client.chats.create(
            model="gemini-3.6-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=[search_food_nutrition],
            )
        )

    def send_message(self, contents) -> str:
        """
        contents: 텍스트 문자열 또는 [이미지 객체, 텍스트] 형태 모두 지원
        """
        response = self.chat.send_message(contents)
        return response.text

def create_diet_agent(api_key: str = ""):
    return DietAgent(api_key=api_key)

if __name__ == "__main__":
    print("🤖 최신 AI 다이어트 코치 에이전트 테스트 중...")
    try:
        agent = create_diet_agent()
        response_text = agent.send_message("오늘 점심에 닭가슴살 100g이랑 밥 먹었는데 영양 분석해줘.")
        print("\n[에이전트 응답]:\n", response_text)
    except Exception as e:
        print(f"\n❌ 실행 오류 발생: {e}")
