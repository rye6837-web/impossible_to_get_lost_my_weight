import os
import sys
import streamlit as st
from google import genai
# pyrefly: ignore [missing-import]
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

# 2. API 키 및 클라이언트 초기화 (배포 환경 및 로컬 환경 동시 대응)
GEMINI_API_KEY = getattr(st, 'secrets', {}).get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6IV9Uq7G9MV3WNCiBQDdfO4ig_Wid-jc6aLO__5jhbd0g"))
client = genai.Client(api_key=GEMINI_API_KEY)

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
    def __init__(self):
        self.chat = client.chats.create(
            model="gemini-3.1-flash-lite",
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

def create_diet_agent():
    return DietAgent()

if __name__ == "__main__":
    print("🤖 최신 AI 다이어트 코치 에이전트 테스트 중...")
    try:
        agent = create_diet_agent()
        response_text = agent.send_message("오늘 점심에 닭가슴살 100g이랑 밥 먹었는데 영양 분석해줘.")
        print("\n[에이전트 응답]:\n", response_text)
    except Exception as e:
        print(f"\n❌ 실행 오류 발생: {e}")
