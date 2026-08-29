import os
import sys
import json
import re
import streamlit as st
from google import genai
from google.genai import types
from typing import Optional, Dict, Any, Tuple

# 1. 모듈 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from app_tools.food_db import search_food_nutrition
from app_tools.exercise_tool import calculate_exercise_calories
from app_tools.nutrition_rag import search_nutrition_knowledge

def get_api_key() -> str:
    """Gemini API 키를 여러 소스에서 순차적으로 탐색합니다."""
    if "GEMINI_API_KEY" in st.session_state and st.session_state["GEMINI_API_KEY"]:
        return st.session_state["GEMINI_API_KEY"]
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY", "")

# 3. 에이전트 시스템 프롬프트 (3대 도구 및 스마트 메타데이터 태깅)
SYSTEM_INSTRUCTION = """
당신은 전문적이고 친절한 'AI 다이어트 & 종합 웰니스 코치 에이전트'입니다.

당신은 다음 3가지 전문 도구(Tools)를 적극적으로 활용해야 합니다:
1. `search_food_nutrition(food_name)`: 사용자가 음식이나 식단을 이야기하면, 칼로리와 영양소를 절대 임의로 지어내지 말고 반드시 이 도구를 호출하여 식약처 표준 영양 수치를 확인하세요.
2. `calculate_exercise_calories(exercise_name, duration_minutes, user_weight)`: 사용자가 운동(러닝, 헬스, 수영 등)을 했다고 하면, 이 도구를 호출하여 과학적인 METs 기반 소모 칼로리를 계산하세요.
3. `search_nutrition_knowledge(query)`: 사용자가 혈당 관리, 다이어트 정체기, 단백질 흡수 타이밍, 대체 식재료, 야식 대처법 등 다이어트 상식/원리를 물어보면 이 도구를 검색하여 전문적인 가이드를 제공하세요.

답변 가이드라인:
- 영양/식단 분석 시: 섭취한 음식의 총 칼로리 및 탄/단/지/나트륨 수치를 요약하고, 사용자의 일일 목표치 대비 진단과 다음 식사 추천 팁을 친절히 안내하세요.
- 운동 분석 시: 소모된 칼로리가 오늘 식단 관리에 얼마나 기여했는지 격려하고 칭찬해 주세요.

[중요: 데이터베이스 자동 저장을 위한 메타데이터 태그 규칙]
- 사용자가 먹은 식단을 분석하여 총 칼로리와 영양소가 도출되었을 때, 응답의 맨 마지막 줄에 반드시 아래 형식의 JSON 태그를 한 줄로 붙여주세요 (사용자에게는 숨겨지고 시스템이 파싱합니다):
<!-- MEAL_DATA: {"food_name": "대표 음식명(또는 종합 식단명)", "calories": 520, "carbs": 65, "protein": 32, "fat": 14, "sugar": 5, "sodium": 650, "meal_type": "점심"} -->

- 사용자가 수행한 운동을 분석하여 소모 칼로리가 도출되었을 때, 응답의 맨 마지막 줄에 반드시 아래 형식의 JSON 태그를 한 줄로 붙여주세요:
<!-- EXERCISE_DATA: {"exercise_name": "운동명", "duration_min": 30, "calories_burned": 220} -->
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
                tools=[
                    search_food_nutrition, 
                    calculate_exercise_calories, 
                    search_nutrition_knowledge
                ],
            )
        )

    def send_message(self, contents) -> str:
        """
        contents: 텍스트 문자열 또는 [이미지 객체, 텍스트] 형태 모두 지원
        """
        response = self.chat.send_message(contents)
        return response.text

def parse_agent_metadata(response_text: str) -> Tuple[str, Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    에이전트 응답 텍스트에서 MEAL_DATA 또는 EXERCISE_DATA 메타데이터 태그를 파싱하여 분리합니다.
    반환: (클린 텍스트, 식단 메타데이터 딕셔너리, 운동 메타데이터 딕셔너리)
    """
    meal_data = None
    exercise_data = None
    
    # MEAL_DATA 정규식 매칭
    meal_match = re.search(r'<!--\s*MEAL_DATA:\s*(\{.*?\})\s*-->', response_text, re.DOTALL)
    if meal_match:
        try:
            meal_data = json.loads(meal_match.group(1))
        except Exception:
            pass
            
    # EXERCISE_DATA 정규식 매칭
    ex_match = re.search(r'<!--\s*EXERCISE_DATA:\s*(\{.*?\})\s*-->', response_text, re.DOTALL)
    if ex_match:
        try:
            exercise_data = json.loads(ex_match.group(1))
        except Exception:
            pass
            
    # 본문에서 주석 태그 제거
    clean_text = re.sub(r'<!--\s*(?:MEAL_DATA|EXERCISE_DATA):\s*\{.*?\}\s*-->', '', response_text, flags=re.DOTALL).strip()
    return clean_text, meal_data, exercise_data

def create_diet_agent(api_key: str = ""):
    return DietAgent(api_key=api_key)

if __name__ == "__main__":
    print("🤖 3대 전문 도구 탑재 AI 다이어트 코치 테스트 중...")
    try:
        agent = create_diet_agent()
        resp = agent.send_message("오늘 점심에 닭가슴살 샐러드 먹었어")
        clean, meal, ex = parse_agent_metadata(resp)
        print("\n[클린 응답]:\n", clean)
        print("\n[추출된 식단 메타데이터]:\n", meal)
    except Exception as e:
        print(f"\n❌ 실행 오류: {e}")
